import re
from django.db import migrations

def compute_prefix(name):
    if not name:
        return 'KAN'
    trimmed = name.strip()
    clean = re.sub(r'^(team\s+|space\s+)', '', trimmed, flags=re.IGNORECASE).strip()
    chars = re.sub(r'[^a-zA-Z0-9]', '', clean)
    if len(chars) < 2:
        chars = re.sub(r'[^a-zA-Z0-9]', '', trimmed)
    if len(chars) >= 3:
        return chars[:3].upper()
    elif chars:
        return chars.upper()
    return 'KAN'

def update_ticket_codes(apps, schema_editor):
    TeamSetting = apps.get_model('tickets', 'TeamSetting')
    Ticket = apps.get_model('tickets', 'Ticket')
    
    setting = TeamSetting.objects.filter(id=1).first()
    team_name = setting.name if setting else 'Team Coca'
    prefix = compute_prefix(team_name)

    for t in Ticket.objects.all():
        old_code = t.ticket_code or ''
        if '-' in old_code:
            num_part = old_code.split('-')[-1]
        else:
            num_part = str(t.ticket_id)
        t.ticket_code = f"{prefix}-{num_part}"
        t.save(update_fields=['ticket_code'])

def reverse_update(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0008_fix_admin_department'),
    ]

    operations = [
        migrations.RunPython(update_ticket_codes, reverse_update),
    ]
