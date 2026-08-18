from django.core.cache import cache
from .models import TeamSetting

# Cache key for team settings — avoids a DB query on every request
_TEAM_SETTING_CACHE_KEY = 'global_team_setting'

def team_context(request):
    """Context processor providing active space, all spaces list, max 3 limit, and admin role state to all templates."""
    active_space_id = None
    if request:
        if 'space_id' in request.GET:
            try:
                active_space_id = int(request.GET.get('space_id'))
                if hasattr(request, 'session'):
                    request.session['active_space_id'] = active_space_id
            except (ValueError, TypeError):
                pass
        elif hasattr(request, 'session'):
            active_space_id = request.session.get('active_space_id')

    active_space = None
    if active_space_id:
        active_space = TeamSetting.objects.filter(id=active_space_id).first()

    if not active_space:
        active_space = TeamSetting.get_settings()
        if request and hasattr(request, 'session'):
            request.session['active_space_id'] = active_space.id

    all_spaces = list(TeamSetting.objects.select_related('lead', 'lead__profile').all().order_by('id'))
    total_spaces_count = len(all_spaces)

    is_admin = False
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        is_admin = request.user.is_superuser or bool(profile and profile.role and profile.role.role_name in ['Admin', 'Administrator'])

    can_create_space = is_admin and (total_spaces_count < 3)

    return {
        'active_space': active_space,
        'team_setting': active_space,
        'team_name': active_space.name,
        'team_initials': active_space.initials,
        'team_icon_type': active_space.icon_type,
        'team_icon_value': active_space.icon_value,
        'team_icon_bg_color': active_space.icon_bg_color,
        'ticket_prefix': active_space.ticket_prefix,
        'all_spaces': all_spaces,
        'total_spaces_count': total_spaces_count,
        'can_create_space': can_create_space,
        'is_admin': is_admin,
    }
