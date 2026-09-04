from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tickets.models import Role, UserProfile

class Command(BaseCommand):
    help = 'Initialize default roles and main Admin user (Vatanaking20@gmail.com / admin123)'

    def handle(self, *args, **kwargs):
        # 1. Ensure Roles exist
        admin_role, _ = Role.objects.get_or_create(
            role_name='Admin',
            defaults={'description': 'Administrator with full system access'}
        )
        agent_role, _ = Role.objects.get_or_create(
            role_name='Support Agent',
            defaults={'description': 'Support Agent who handles tickets'}
        )
        user_role, _ = Role.objects.get_or_create(
            role_name='User',
            defaults={'description': 'Regular user who submits tickets'}
        )

        admin_email = 'Vatanaking20@gmail.com'
        admin_password = 'admin123'
        admin_username = 'Vatanaking20@gmail.com'

        # Check if user with this email or username exists
        user = User.objects.filter(email__iexact=admin_email).first()
        if not user:
            user = User.objects.filter(username__iexact='admin').first()

        if user:
            user.username = admin_username
            user.email = admin_email
            user.set_password(admin_password)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Updated existing admin user to email/username: '{admin_email}'"))
        else:
            user = User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password
            )
            self.stdout.write(self.style.SUCCESS(f"Created new admin user: '{admin_email}'"))

        # Ensure UserProfile exists and has Admin role
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = admin_role
        profile.full_name = 'Admin Vatana'
        profile.status = 'Active'
        profile.save()

        # 2. Ensure Testing Account exists (test@kaola.com / password123)
        test_email = 'test@kaola.com'
        test_password = 'password123'
        test_username = 'test@kaola.com'

        test_user = User.objects.filter(email__iexact=test_email).first()
        if not test_user:
            test_user = User.objects.filter(username__iexact=test_username).first()
        if not test_user:
            test_user = User.objects.filter(username__iexact='tester').first()

        if test_user:
            test_user.username = test_username
            test_user.email = test_email
            test_user.set_password(test_password)
            test_user.is_superuser = False
            test_user.is_staff = True
            test_user.is_active = True
            test_user.save()
            self.stdout.write(self.style.SUCCESS(f"Updated existing test user: '{test_email}'"))
        else:
            test_user = User.objects.create_user(
                username=test_username,
                email=test_email,
                password=test_password,
                is_staff=True,
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS(f"Created new test user: '{test_email}'"))

        test_profile, _ = UserProfile.objects.get_or_create(user=test_user)
        test_profile.role = admin_role
        test_profile.full_name = 'Testing Account'
        test_profile.public_name = 'Tester'
        test_profile.status = 'Active'
        test_profile.is_email_verified = True
        test_profile.save()

        # Add test user to all team spaces
        from tickets.models import TeamSetting
        for space in TeamSetting.objects.all():
            space.members.add(test_user)

        # Ensure all other existing users have a UserProfile and role assigned
        for u in User.objects.all():
            p, _ = UserProfile.objects.get_or_create(user=u)
            if not p.role:
                if u.is_superuser:
                    p.role = admin_role
                else:
                    p.role = user_role
            if not p.full_name:
                p.full_name = u.first_name and f"{u.first_name} {u.last_name}" or u.username
            p.save()

        self.stdout.write(self.style.SUCCESS("Admin initialization, Testing account creation, and role assignment complete!"))

