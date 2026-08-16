from django import template
from django.utils.safestring import mark_safe

register = template.Library()

PRESET_ICONS = {
    'mountains': '''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;border-radius:inherit;display:block;">
        <rect width="40" height="40" rx="8" fill="#579DFF"/>
        <path d="M7 32L18 16L27 28L33 20L38 32H7Z" fill="#1C386E"/>
        <path d="M12 32L21 19L29 32H12Z" fill="#E9F2FF"/>
        <path d="M21 19L24 23.5L22.5 25.5L19.5 24L18 26L15.5 24.5L12 32H29L21 19Z" fill="#B3D4FF"/>
        <path d="M5 32L15 17L22 28L18 28.5L15 24L11 30L5 32Z" fill="#FFFFFF"/>
    </svg>''',
    
    'alien': '''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;border-radius:inherit;display:block;">
        <rect width="40" height="40" rx="8" fill="#00C7E5"/>
        <ellipse cx="20" cy="27" rx="14" ry="5" fill="#8777D9"/>
        <circle cx="20" cy="18" r="8" fill="#998DD9"/>
        <circle cx="20" cy="17" r="4.5" fill="#FFFFFF"/>
        <circle cx="20" cy="17" r="2.5" fill="#172B4D"/>
        <circle cx="21" cy="16" r="1" fill="#FFFFFF"/>
        <path d="M17 23H23" stroke="#172B4D" stroke-width="1.5" stroke-linecap="round"/>
        <ellipse cx="20" cy="26.5" rx="11" ry="3.5" fill="#57D9A3"/>
    </svg>''',
    
    'toucan': '''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;border-radius:inherit;display:block;">
        <rect width="40" height="40" rx="8" fill="#6554C0"/>
        <circle cx="16" cy="20" r="10" fill="#253858"/>
        <path d="M16 11C23 11 32 16 32 23C27 25 21 24 16 22V11Z" fill="#FFAB00"/>
        <path d="M25 14C29 17 32 20 32 23C29 23 27 21 25 19V14Z" fill="#FF5630"/>
        <circle cx="16" cy="18" r="4.5" fill="#FFFFFF"/>
        <circle cx="16" cy="18" r="2.2" fill="#091E42"/>
    </svg>''',

    'cloud': '''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;border-radius:inherit;display:block;">
        <rect width="40" height="40" rx="8" fill="#4C9AFF"/>
        <circle cx="15" cy="22" r="7" fill="#FFFFFF"/>
        <circle cx="22" cy="18" r="8" fill="#FFFFFF"/>
        <circle cx="28" cy="23" r="6" fill="#FFFFFF"/>
        <rect x="14" y="22" width="15" height="7" fill="#FFFFFF"/>
        <circle cx="18" cy="21" r="1.2" fill="#091E42"/>
        <circle cx="24" cy="21" r="1.2" fill="#091E42"/>
        <path d="M20 23.5Q21 25 22 23.5" stroke="#FF5630" stroke-width="1.2" stroke-linecap="round" fill="none"/>
        <circle cx="16.5" cy="22.5" r="1" fill="#FF8B8B" opacity="0.6"/>
        <circle cx="25.5" cy="22.5" r="1" fill="#FF8B8B" opacity="0.6"/>
    </svg>''',

    'disc': '''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;border-radius:inherit;display:block;">
        <rect width="40" height="40" rx="8" fill="#FF5630"/>
        <circle cx="20" cy="20" r="13" fill="#172B4D"/>
        <circle cx="20" cy="20" r="9" stroke="#344563" stroke-width="1"/>
        <circle cx="20" cy="20" r="5.5" fill="#00C7E5"/>
        <circle cx="20" cy="20" r="2" fill="#FFFFFF"/>
    </svg>''',

    'code': '''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;border-radius:inherit;display:block;">
        <rect width="40" height="40" rx="8" fill="#FF7452"/>
        <rect x="7" y="9" width="26" height="22" rx="3" fill="#172B4D"/>
        <circle cx="11" cy="13" r="1" fill="#FF5630"/>
        <circle cx="14" cy="13" r="1" fill="#FFAB00"/>
        <circle cx="17" cy="13" r="1" fill="#36B37E"/>
        <path d="M11 18H20M11 22H27M11 26H23" stroke="#00C7E5" stroke-width="2" stroke-linecap="round"/>
        <path d="M23 18H29" stroke="#FFC400" stroke-width="2" stroke-linecap="round"/>
    </svg>''',

    'coffee': '''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;border-radius:inherit;display:block;">
        <rect width="40" height="40" rx="8" fill="#00C7E5"/>
        <path d="M12 14H28L25 32H15L12 14Z" fill="#FFFFFF"/>
        <path d="M11 12H29V14H11V12Z" fill="#DEEBFF"/>
        <rect x="13.5" y="19" width="13" height="7" fill="#FF5630"/>
        <circle cx="20" cy="22.5" r="2" fill="#FFFFFF"/>
    </svg>''',

    'easel': '''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;border-radius:inherit;display:block;">
        <rect width="40" height="40" rx="8" fill="#FFC400"/>
        <rect x="10" y="9" width="20" height="15" rx="2" fill="#00C7E5"/>
        <path d="M13 20L17 15L21 19L24 16L27 20H13Z" fill="#FFFFFF"/>
        <circle cx="24" cy="13" r="1.5" fill="#FFFFFF"/>
        <path d="M14 24L11 33M26 24L29 33M20 24V33" stroke="#6554C0" stroke-width="2" stroke-linecap="round"/>
        <path d="M8 24H32" stroke="#6554C0" stroke-width="2" stroke-linecap="round"/>
    </svg>''',

    'drill': '''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;border-radius:inherit;display:block;">
        <rect width="40" height="40" rx="8" fill="#6554C0"/>
        <path d="M14 14H27V21H23L22 28H17L18 21H14V14Z" fill="#FFC400"/>
        <rect x="8" y="16" width="6" height="3" fill="#DFE1E6"/>
        <circle cx="20" cy="18" r="2" fill="#172B4D"/>
        <rect x="23" y="18" width="10" height="3" fill="#172B4D"/>
    </svg>''',

    'hotdog': '''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;border-radius:inherit;display:block;">
        <rect width="40" height="40" rx="8" fill="#FFAB00"/>
        <rect x="9" y="14" width="22" height="12" rx="6" fill="#F48924" transform="rotate(-30 20 20)"/>
        <rect x="6" y="18" width="28" height="6" rx="3" fill="#FF5630" transform="rotate(-30 20 20)"/>
        <path d="M10 26Q15 22 20 20Q25 18 30 14" stroke="#FFE380" stroke-width="1.8" stroke-linecap="round" fill="none"/>
    </svg>''',

    'koala': '''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;border-radius:inherit;display:block;">
        <rect width="40" height="40" rx="8" fill="#4C9AFF"/>
        <circle cx="12" cy="16" r="4.5" fill="#B3D4FF"/>
        <circle cx="28" cy="16" r="4.5" fill="#B3D4FF"/>
        <circle cx="12" cy="16" r="2.5" fill="#FFFFFF"/>
        <circle cx="28" cy="16" r="2.5" fill="#FFFFFF"/>
        <rect x="11" y="15" width="18" height="15" rx="7.5" fill="#B3D4FF"/>
        <circle cx="16" cy="20" r="1.3" fill="#091E42"/>
        <circle cx="24" cy="20" r="1.3" fill="#091E42"/>
        <ellipse cx="20" cy="23" rx="2.5" ry="3.5" fill="#091E42"/>
    </svg>''',

    'phone': '''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;border-radius:inherit;display:block;">
        <rect width="40" height="40" rx="8" fill="#0052CC"/>
        <rect x="13" y="8" width="14" height="24" rx="3" fill="#FFFFFF"/>
        <rect x="15" y="11" width="10" height="16" rx="1" fill="#FFEBE6"/>
        <circle cx="20" cy="17" r="2.5" fill="#FF5630"/>
        <circle cx="20" cy="29.5" r="1" fill="#97A0AF"/>
        <path d="M9 16Q7 20 9 24M31 16Q33 20 31 24" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round" fill="none"/>
    </svg>''',

    'wallet': '''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;border-radius:inherit;display:block;">
        <rect width="40" height="40" rx="8" fill="#FFC400"/>
        <rect x="8" y="12" width="24" height="17" rx="3" fill="#172B4D"/>
        <path d="M8 16H32" stroke="#253858" stroke-width="2"/>
        <rect x="23" y="17" width="9" height="7" rx="2" fill="#0052CC"/>
        <circle cx="26.5" cy="20.5" r="1.2" fill="#FFC400"/>
    </svg>''',

    'terminal': '''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;border-radius:inherit;display:block;">
        <rect width="40" height="40" rx="8" fill="#FF5630"/>
        <rect x="7" y="10" width="26" height="20" rx="3" fill="#172B4D"/>
        <rect x="7" y="10" width="26" height="5" fill="#253858"/>
        <circle cx="10.5" cy="12.5" r="1" fill="#FF8F73"/>
        <circle cx="13.5" cy="12.5" r="1" fill="#FFE380"/>
        <circle cx="16.5" cy="12.5" r="1" fill="#79F2C0"/>
        <path d="M21 16L17 22H21L19 27L25 20H21L23 16H21Z" fill="#FFC400"/>
    </svg>''',

    'notebook': '''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;border-radius:inherit;display:block;">
        <rect width="40" height="40" rx="8" fill="#00B8D9"/>
        <rect x="11" y="8" width="18" height="24" rx="2" fill="#FFFFFF"/>
        <circle cx="14" cy="12" r="1" fill="#FF5630"/>
        <circle cx="14" cy="16" r="1" fill="#FFAB00"/>
        <circle cx="14" cy="20" r="1" fill="#36B37E"/>
        <circle cx="14" cy="24" r="1" fill="#0052CC"/>
        <path d="M17 14H26M17 18H26M17 22H24" stroke="#97A0AF" stroke-width="1.5" stroke-linecap="round"/>
        <path d="M23 29L31 17L33 19L25 31L22 32L23 29Z" fill="#FFAB00"/>
    </svg>''',

    'airplane': '''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;border-radius:inherit;display:block;">
        <rect width="40" height="40" rx="8" fill="#00C7E5"/>
        <path d="M10 27L17 24L28 11C29.5 9.5 32 10.5 31.5 12.5L27 23L24 30L20 25L14 27L10 27Z" fill="#FFFFFF"/>
        <path d="M19 21L27 12L24 23L19 21Z" fill="#0052CC"/>
    </svg>''',

    'battery': '''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;border-radius:inherit;display:block;">
        <rect width="40" height="40" rx="8" fill="#00C7E5"/>
        <rect x="8" y="14" width="22" height="12" rx="2" fill="#5243AA"/>
        <rect x="30" y="17" width="2.5" height="6" rx="1" fill="#5243AA"/>
        <rect x="10" y="16" width="12" height="8" rx="1" fill="#FFAB00"/>
        <path d="M17 17L14 21H18L16 24L20 19H16L18 17H17Z" fill="#FFFFFF"/>
    </svg>''',

    'flag': '''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;border-radius:inherit;display:block;">
        <rect width="40" height="40" rx="8" fill="#FFAB00"/>
        <path d="M13 10V30" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>
        <path d="M14 11H29L25 17L29 23H14V11Z" fill="#FF5630"/>
    </svg>''',

    'sync': '''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;border-radius:inherit;display:block;">
        <rect width="40" height="40" rx="8" fill="#6554C0"/>
        <path d="M13 20C13 15.5 16.5 12 21 12C24 12 26.5 13.5 28 16" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" fill="none"/>
        <path d="M28 12V16H24" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M27 20C27 24.5 23.5 28 19 28C16 28 13.5 26.5 12 24" stroke="#00C7E5" stroke-width="3" stroke-linecap="round" fill="none"/>
        <path d="M12 28V24H16" stroke="#00C7E5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>''',

    'rocket': '''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;border-radius:inherit;display:block;">
        <rect width="40" height="40" rx="8" fill="#172B4D"/>
        <path d="M28 12C28 12 22 13 18 17C15 20 14 24 14 24L17 26L23 23C27 19 28 12 28 12Z" fill="#FFFFFF"/>
        <path d="M14 24L10 25L12 21L14 24Z" fill="#FF5630"/>
        <path d="M21 27L22 30L25 26L21 27Z" fill="#FF5630"/>
        <circle cx="22" cy="18" r="2" fill="#00C7E5"/>
        <circle cx="12" cy="28" r="1.5" fill="#FFAB00"/>
        <circle cx="9" cy="31" r="1" fill="#FF5630"/>
        <circle cx="13" cy="13" r="1" fill="#FFFFFF" opacity="0.6"/>
        <circle cx="29" cy="27" r="1" fill="#FFFFFF" opacity="0.6"/>
    </svg>''',

    'potion': '''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;border-radius:inherit;display:block;">
        <rect width="40" height="40" rx="8" fill="#6554C0"/>
        <path d="M18 10H22V15L28 25C29 27 27.5 29 25 29H15C12.5 29 11 27 12 25L18 15V10Z" fill="#FFFFFF"/>
        <path d="M13.5 23L16 19H24L26.5 23C27 26 25 28 23 28H17C15 28 13 26 13.5 23Z" fill="#FF5630"/>
        <circle cx="18" cy="24" r="1.2" fill="#FFFFFF"/>
        <circle cx="22" cy="22" r="1" fill="#FFFFFF"/>
    </svg>''',

    'sliders': '''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;border-radius:inherit;display:block;">
        <rect width="40" height="40" rx="8" fill="#FF5630"/>
        <path d="M13 10V30M20 10V30M27 10V30" stroke="#172B4D" stroke-width="2" stroke-linecap="round"/>
        <circle cx="13" cy="22" r="3" fill="#FFFFFF"/>
        <circle cx="20" cy="16" r="3" fill="#FFFFFF"/>
        <circle cx="27" cy="24" r="3" fill="#FFFFFF"/>
    </svg>''',

    'wrench': '''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;border-radius:inherit;display:block;">
        <rect width="40" height="40" rx="8" fill="#FF5630"/>
        <path d="M25 10C22.5 10 20.5 11.5 19.5 13.5L11 22C9.5 23.5 9.5 26 11 27.5C12.5 29 15 29 16.5 27.5L25 19C27 18 28.5 16 28.5 13.5C28.5 12.5 28 11.5 27.5 11L25 13.5L22.5 11L25 10Z" fill="#FFFFFF"/>
        <circle cx="13.5" cy="25" r="1.5" fill="#FF5630"/>
    </svg>''',

    'storm': '''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;border-radius:inherit;display:block;">
        <rect width="40" height="40" rx="8" fill="#5243AA"/>
        <path d="M14 20C14 17 16.5 15 19.5 15C22 15 24 16.5 24.5 18.5C26.5 18.5 28 20 28 22C28 24 26.5 25.5 24.5 25.5H14C12 25.5 10.5 24 10.5 22C10.5 20.5 11.5 19.2 13 19" fill="#FFFFFF"/>
        <path d="M19 25L16 29H20L18 33L23 27H19L21 25H19Z" fill="#FFAB00"/>
    </svg>''',

    'lifebuoy': '''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;border-radius:inherit;display:block;">
        <rect width="40" height="40" rx="8" fill="#00B8D9"/>
        <circle cx="20" cy="20" r="12" fill="#FFFFFF"/>
        <circle cx="20" cy="20" r="6" fill="#00B8D9"/>
        <path d="M14 10L17 15M26 10L23 15M14 30L17 25M26 30L23 25" stroke="#FF5630" stroke-width="3" stroke-linecap="round"/>
        <circle cx="20" cy="20" r="11" stroke="#FF5630" stroke-width="2" fill="none"/>
    </svg>''',

    'yeti': '''<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;border-radius:inherit;display:block;">
        <rect width="40" height="40" rx="8" fill="#0052CC"/>
        <ellipse cx="20" cy="25" rx="11" ry="9" fill="#FFFFFF"/>
        <circle cx="20" cy="18" r="8" fill="#FFFFFF"/>
        <rect x="14" y="16" width="12" height="9" rx="4.5" fill="#FFEBE6"/>
        <circle cx="17.5" cy="19.5" r="1.3" fill="#FF5630"/>
        <circle cx="22.5" cy="19.5" r="1.3" fill="#FF5630"/>
        <path d="M18 22.5Q20 24 22 22.5" stroke="#FF5630" stroke-width="1.2" stroke-linecap="round" fill="none"/>
    </svg>''',
}


@register.simple_tag
def render_team_avatar(icon_type='preset', icon_value='mountains', initials='TV', bg_color='#0052cc', custom_class=''):
    """Renders the appropriate team avatar: Preset SVG, custom uploaded image, or initials badge."""
    if icon_type == 'custom' and icon_value:
        return mark_safe(f'''<img src="{icon_value}" alt="Team Icon" class="team-avatar-img {custom_class}" style="width:100%;height:100%;object-fit:cover;border-radius:inherit;display:block;">''')
    
    if icon_type == 'preset' and icon_value in PRESET_ICONS:
        return mark_safe(PRESET_ICONS[icon_value])
        
    # Default to initials
    disp_initials = (initials or 'TV')[:2].upper()
    return mark_safe(f'''<div class="team-avatar-initials {custom_class}" style="width:100%;height:100%;background:{bg_color or '#0052cc'};color:#ffffff;border-radius:inherit;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:inherit;">{disp_initials}</div>''')


@register.filter
def get_preset_icon_svg(icon_key):
    """Filter to get raw SVG for a preset icon key."""
    return mark_safe(PRESET_ICONS.get(icon_key, ''))
