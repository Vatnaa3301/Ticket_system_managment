from django.db import migrations

def fix_admin_department(apps, schema_editor):
    UserProfile = apps.get_model('tickets', 'UserProfile')
    # Update any userprofile with 'software enginor' in job_title or department
    for profile in UserProfile.objects.all():
        updated = False
        if profile.job_title and 'enginor' in profile.job_title.lower():
            profile.job_title = 'Software Team'
            updated = True
        if profile.department and 'enginor' in profile.department.lower():
            profile.department = 'Software Team'
            updated = True
        # For Admin_Vatana specifically or Vatanaking20@gmail.com
        if profile.user and (profile.user.username.lower() in ['admin_vatana', 'vatanaking20@gmail.com'] or profile.user.email.lower() == 'vatanaking20@gmail.com'):
            profile.department = 'Software Team'
            if profile.job_title and 'enginor' in profile.job_title.lower():
                profile.job_title = 'Software Team'
            updated = True
        if updated:
            profile.save()

def reverse_fix(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0007_add_ticket_indexes'),
    ]

    operations = [
        migrations.RunPython(fix_admin_department, reverse_fix),
    ]
