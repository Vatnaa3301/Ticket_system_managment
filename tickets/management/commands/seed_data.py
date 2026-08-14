import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tickets.models import (
    Role, UserProfile, TicketCategory, Priority, TicketStatus,
    Ticket, TicketComment, SLARule, TicketLog, Notification
)

class Command(BaseCommand):
    help = 'Seeds initial data for Help Desk / Support Ticket System'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding initial ticket system data...")

        # 1. Roles
        roles_data = [
            ("Admin", "Full system access and admin management"),
            ("Support Agent", "Handles and resolves assigned support tickets"),
            ("User", "Standard user who creates support tickets"),
        ]
        roles_dict = {}
        for r_name, r_desc in roles_data:
            role, _ = Role.objects.get_or_create(role_name=r_name, defaults={'description': r_desc})
            roles_dict[r_name] = role

        # 2. Users & User Profiles
        users_data = [
            ("vatana", "admin@vatana.com", "Vatana King", "Admin", "IT Department", "012345678"),
            ("agent_sarah", "sarah@vatana.com", "Sarah Agent", "Support Agent", "Technical Support", "098765432"),
            ("john_doe", "john@vatana.com", "John Doe", "User", "Finance Department", "011223344"),
        ]
        users_dict = {}
        for username, email, full_name, r_name, dept, phone in users_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email, 'first_name': full_name.split()[0]}
            )
            if created:
                user.set_password("password123")
                user.save()
            
            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': roles_dict[r_name],
                    'full_name': full_name,
                    'department': dept,
                    'phone': phone,
                    'status': 'Active'
                }
            )
            users_dict[username] = user

        # Also create superuser admin if not existing
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser('admin', 'admin@ticket.com', 'admin123')
            UserProfile.objects.create(user=admin_user, role=roles_dict['Admin'], full_name='System Admin')
            users_dict['admin'] = admin_user

        # 3. Categories
        categories_data = [
            ("Technical Support", "Hardware, software, and IT support issues"),
            ("Billing & Accounts", "Invoicing, subscription, and payment queries"),
            ("Network & Access", "VPN, Wi-Fi, permission, and credential access"),
        ]
        cats_dict = {}
        for cat_name, desc in categories_data:
            cat, _ = TicketCategory.objects.get_or_create(category_name=cat_name, defaults={'description': desc})
            cats_dict[cat_name] = cat

        # 4. Priorities
        priorities_data = [
            ("Low", 48, 96),
            ("Medium", 24, 48),
            ("High", 4, 12),
            ("Critical", 1, 4),
        ]
        prio_dict = {}
        for p_name, resp, reso in priorities_data:
            prio, _ = Priority.objects.get_or_create(
                priority_name=p_name,
                defaults={'response_time_hours': resp, 'resolution_time_hours': reso}
            )
            prio_dict[p_name] = prio
            SLARule.objects.get_or_create(
                priority=prio,
                defaults={'response_time': resp, 'resolution_time': reso, 'description': f"Default SLA for {p_name}"}
            )

        # 5. Ticket Statuses (matching Jira columns in reference UI!)
        statuses_data = [
            ("To Do", "Ticket reported and waiting for pick up", 1),
            ("In Progress", "Work actively being performed on ticket", 2),
            ("In Review", "Resolution being tested or reviewed", 3),
            ("Done", "Ticket completed and resolved", 4),
        ]
        status_dict = {}
        for s_name, s_desc, s_order in statuses_data:
            st, _ = TicketStatus.objects.get_or_create(
                status_name=s_name,
                defaults={'description': s_desc, 'order': s_order}
            )
            status_dict[s_name] = st

        # 6. Demo Tickets matching Jira KAN-1, KAN-2, KAN-3 style
        today = datetime.date.today()
        tickets_data = [
            ("KAN-1", "Task 1", "Configure core authentication module and database connection", "To Do", "High", "Technical Support", "john_doe", "agent_sarah", today + datetime.timedelta(days=7)),
            ("KAN-2", "Task 2", "Implement role-based user permissions and support agent routing", "To Do", "Medium", "Network & Access", "john_doe", "agent_sarah", today + datetime.timedelta(days=14)),
            ("KAN-3", "Fix VPN Access Disconnection", "User experiences frequent VPN timeouts during peak hours", "In Progress", "Critical", "Network & Access", "john_doe", "agent_sarah", today + datetime.timedelta(days=2)),
            ("KAN-4", "Billing Invoice Generation Bug", "PDF invoice export fails when user has non-ASCII characters", "In Review", "High", "Billing & Accounts", "john_doe", "vatana", today + datetime.timedelta(days=3)),
            ("KAN-5", "Upgrade Office Wi-Fi Router Firmware", "Scheduled router firmware patch for 5th floor network", "Done", "Low", "Technical Support", "vatana", "agent_sarah", today - datetime.timedelta(days=1)),
        ]

        for code, subject, desc, st_name, p_name, cat_name, creator_uname, assignee_uname, due in tickets_data:
            ticket, created = Ticket.objects.get_or_create(
                ticket_code=code,
                defaults={
                    'subject': subject,
                    'description': desc,
                    'status': status_dict[st_name],
                    'priority': prio_dict[p_name],
                    'category': cats_dict[cat_name],
                    'user': users_dict.get(creator_uname, users_dict['vatana']),
                    'assigned_to': users_dict.get(assignee_uname),
                    'due_date': due
                }
            )
            if created:
                TicketLog.objects.create(
                    ticket=ticket,
                    user=users_dict.get(creator_uname, users_dict['vatana']),
                    action_type='Create',
                    new_value=f"Ticket {code} created with status {st_name}"
                )
                TicketComment.objects.create(
                    ticket=ticket,
                    user=users_dict.get(assignee_uname, users_dict['vatana']),
                    comment_text=f"Initial review started for {subject}."
                )

        self.stdout.write(self.style.SUCCESS("Successfully seeded initial data!"))
