from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import json
from .models import Ticket, TicketStatus, Priority, TicketCategory, Notification, UserProfile

class NotificationSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='alice', email='alice@example.com', password='password123')
        self.user2 = User.objects.create_user(username='bob', email='bob@example.com', password='password123')
        
        UserProfile.objects.create(user=self.user1, full_name='Alice Smith')
        UserProfile.objects.create(user=self.user2, full_name='Bob Jones')

        self.status_todo = TicketStatus.objects.create(status_name='To Do', order=1)
        self.status_done = TicketStatus.objects.create(status_name='Done', order=2)
        self.priority_med = Priority.objects.create(priority_name='Medium')
        self.category = TicketCategory.objects.create(category_name='Engineering')

    def test_assignment_notification_on_ticket_create(self):
        self.client.login(username='alice', password='password123')
        payload = {
            'subject': 'Build Notification Dropdown',
            'description': 'Implement Jira style dropdown',
            'assigned_to_id': self.user2.id,
            'priority_id': self.priority_med.priority_id,
            'status_id': self.status_todo.status_id
        }
        res = self.client.post('/api/tickets/create/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        
        # Check that Bob (user2) got an assignment notification
        notif = Notification.objects.filter(user=self.user2, notification_type='Assignment').first()
        self.assertIsNotNone(notif)
        self.assertIn('assigned', notif.title.lower())
        self.assertFalse(notif.is_read)

        # Alice should NOT have Bob's notification
        alice_notifs = Notification.objects.filter(user=self.user1)
        self.assertEqual(alice_notifs.count(), 0)

    def test_assignment_notification_on_reassign(self):
        ticket = Ticket.objects.create(
            ticket_code='KAN-1',
            subject='Initial Ticket',
            user=self.user1,
            assigned_to=self.user1,
            status=self.status_todo,
            priority=self.priority_med
        )
        self.client.login(username='alice', password='password123')
        payload = {
            'subject': 'Initial Ticket',
            'assigned_to_id': self.user2.id
        }
        res = self.client.post(f'/api/tickets/{ticket.ticket_id}/edit/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)

        # Bob (user2) should get notification
        notif = Notification.objects.filter(user=self.user2, ticket=ticket, notification_type='Assignment').first()
        self.assertIsNotNone(notif)

    def test_overdue_ticket_notification_generated(self):
        # Create an overdue ticket for Bob
        yesterday = timezone.now().date() - timedelta(days=2)
        ticket = Ticket.objects.create(
            ticket_code='KAN-2',
            subject='Overdue Task',
            user=self.user1,
            assigned_to=self.user2,
            due_date=yesterday,
            status=self.status_todo,
            priority=self.priority_med
        )

        # Bob calls notifications API
        self.client.login(username='bob', password='password123')
        res = self.client.get('/api/notifications/')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertGreaterEqual(data['unread_count'], 1)
        
        # Overdue item in response
        titles = [n['title'] for n in data['notifications']]
        self.assertTrue(any('overdue' in t.lower() for t in titles))

    def test_mark_notification_as_read(self):
        notif = Notification.objects.create(
            user=self.user2,
            title='Test Notice',
            message='Test Content',
            notification_type='Assignment',
            is_read=False
        )
        self.client.login(username='bob', password='password123')
        res = self.client.post(f'/api/notifications/{notif.notification_id}/read/')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['unread_count'], 0)

        notif.refresh_from_db()
        self.assertTrue(notif.is_read)

    def test_mark_all_notifications_read(self):
        Notification.objects.create(user=self.user2, title='Notice 1', notification_type='Assignment', is_read=False)
        Notification.objects.create(user=self.user2, title='Notice 2', notification_type='Overdue', is_read=False)

        self.client.login(username='bob', password='password123')
        res = self.client.post('/api/notifications/mark-all-read/')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['unread_count'], 0)

        self.assertEqual(Notification.objects.filter(user=self.user2, is_read=False).count(), 0)


class SpaceAndTeamTests(TestCase):
    def setUp(self):
        from .models import TeamSetting, Role
        self.client = Client()
        self.admin_role = Role.objects.create(role_name='Administrator')
        self.member_role = Role.objects.create(role_name='Member')

        self.admin_user = User.objects.create_superuser(username='admin_boss', email='admin_boss@example.com', password='password123')
        UserProfile.objects.create(user=self.admin_user, role=self.admin_role, full_name='Admin Boss')

        self.dev_user = User.objects.create_user(username='dev_john', email='dev_john@example.com', password='password123')
        UserProfile.objects.create(user=self.dev_user, role=self.member_role, full_name='John Developer')

        self.mkt_user = User.objects.create_user(username='mkt_sara', email='mkt_sara@example.com', password='password123')
        UserProfile.objects.create(user=self.mkt_user, role=self.member_role, full_name='Sara Marketing')

        self.space_dev = TeamSetting.objects.create(name='Dev Space', key='DEV', lead=self.admin_user)
        self.space_dev.members.add(self.admin_user, self.dev_user)

        self.space_mkt = TeamSetting.objects.create(name='Marketing Space', key='MKT', lead=self.mkt_user)
        self.space_mkt.members.add(self.mkt_user)

        self.status_todo = TicketStatus.objects.create(status_name='To Do', order=1)
        self.status_done = TicketStatus.objects.create(status_name='Done', order=2)
        self.priority_high = Priority.objects.create(priority_name='High')
        self.priority_med = Priority.objects.create(priority_name='Medium')

        # Create tickets in different spaces
        self.ticket_dev1 = Ticket.objects.create(
            ticket_code='DEV-1',
            space=self.space_dev,
            user=self.admin_user,
            assigned_to=self.dev_user,
            subject='Dev Architecture',
            status=self.status_todo,
            priority=self.priority_high
        )
        self.ticket_dev2 = Ticket.objects.create(
            ticket_code='DEV-2',
            space=self.space_dev,
            user=self.admin_user,
            assigned_to=self.dev_user,
            subject='Dev Backend Refactor',
            status=self.status_done,
            priority=self.priority_med
        )
        self.ticket_mkt1 = Ticket.objects.create(
            ticket_code='MKT-1',
            space=self.space_mkt,
            user=self.mkt_user,
            assigned_to=self.mkt_user,
            subject='Marketing Campaign Q3',
            status=self.status_todo,
            priority=self.priority_high
        )

    def test_procurement_report_filter_by_space(self):
        self.client.login(username='admin_boss', password='password123')
        
        # 1. Filter by Dev Space
        res_dev = self.client.get(f'/api/reports/procurement/data/?space_id={self.space_dev.id}')
        self.assertEqual(res_dev.status_code, 200)
        data_dev = res_dev.json()
        self.assertTrue(data_dev['success'])
        self.assertEqual(len(data_dev['tickets']), 2)
        dev_keys = [t['ticket_code'] for t in data_dev['tickets']]
        self.assertIn('DEV-1', dev_keys)
        self.assertIn('DEV-2', dev_keys)
        self.assertNotIn('MKT-1', dev_keys)

        # 2. Filter by Marketing Space
        res_mkt = self.client.get(f'/api/reports/procurement/data/?space_id={self.space_mkt.id}')
        self.assertEqual(res_mkt.status_code, 200)
        data_mkt = res_mkt.json()
        self.assertTrue(data_mkt['success'])
        self.assertEqual(len(data_mkt['tickets']), 1)
        self.assertEqual(data_mkt['tickets'][0]['ticket_code'], 'MKT-1')

        # 3. Filter by All Spaces
        res_all = self.client.get('/api/reports/procurement/data/?space_id=all')
        self.assertEqual(res_all.status_code, 200)
        data_all = res_all.json()
        self.assertTrue(data_all['success'])
        self.assertEqual(len(data_all['tickets']), 3)

    def test_teams_view_by_space(self):
        self.client.login(username='admin_boss', password='password123')
        
        # 1. View Dev Space members
        res_dev = self.client.get(f'/teams/?space_id={self.space_dev.id}')
        self.assertEqual(res_dev.status_code, 200)
        self.assertEqual(res_dev.context['total_count'], 2)
        dev_member_names = [m['username'] for m in res_dev.context['members']]
        self.assertIn('admin_boss', dev_member_names)
        self.assertIn('dev_john', dev_member_names)
        self.assertNotIn('mkt_sara', dev_member_names)

        # 2. View Marketing Space members
        res_mkt = self.client.get(f'/teams/?space_id={self.space_mkt.id}')
        self.assertEqual(res_mkt.status_code, 200)
        self.assertEqual(res_mkt.context['total_count'], 1)
        mkt_member_names = [m['username'] for m in res_mkt.context['members']]
        self.assertIn('mkt_sara', mkt_member_names)
        self.assertNotIn('dev_john', mkt_member_names)

        # 3. View All Spaces members
        res_all = self.client.get('/teams/?space_id=all')
        self.assertEqual(res_all.status_code, 200)
        self.assertEqual(res_all.context['total_count'], 3)

