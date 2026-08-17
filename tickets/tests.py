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
