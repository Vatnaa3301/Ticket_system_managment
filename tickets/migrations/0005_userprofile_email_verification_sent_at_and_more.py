from django.db import migrations, models

def mark_existing_users_verified(apps, schema_editor):
    UserProfile = apps.get_model('tickets', 'UserProfile')
    UserProfile.objects.all().update(is_email_verified=True)


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0004_userprofile_avatar_color_userprofile_header_color_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='email_verification_sent_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='email_verification_token',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='is_email_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(mark_existing_users_verified, migrations.RunPython.noop),
    ]
