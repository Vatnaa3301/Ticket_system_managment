from django.core.cache import cache
from .models import TeamSetting

# Cache key for team settings — avoids a DB query on every request
_TEAM_SETTING_CACHE_KEY = 'global_team_setting'

def team_context(request):
    """Context processor providing global team settings and admin role state to all templates."""
    # Cache TeamSetting for 60 seconds to avoid get_or_create on every request
    team_setting = cache.get(_TEAM_SETTING_CACHE_KEY)
    if team_setting is None:
        team_setting = TeamSetting.get_settings()
        cache.set(_TEAM_SETTING_CACHE_KEY, team_setting, 60)

    is_admin = False
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        is_admin = request.user.is_superuser or bool(profile and profile.role and profile.role.role_name in ['Admin', 'Administrator'])

    return {
        'team_setting': team_setting,
        'team_name': team_setting.name,
        'team_initials': team_setting.initials,
        'team_icon_type': team_setting.icon_type,
        'team_icon_value': team_setting.icon_value,
        'team_icon_bg_color': team_setting.icon_bg_color,
        'is_admin': is_admin,
    }
