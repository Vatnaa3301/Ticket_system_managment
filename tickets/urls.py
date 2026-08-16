from django.urls import path
from . import views

urlpatterns = [
    # Auth Views
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('verify-email/<str:token>/', views.verify_email_view, name='verify_email'),
    path('resend-verification/', views.resend_verification_view, name='resend_verification'),
    path('logout/', views.logout_view, name='logout'),

    path('', views.board_view, name='board'),
    path('for-you/', views.for_you_view, name='for_you'),
    path('board/', views.board_view, name='board_alias'),
    path('list/', views.list_view, name='list'),
    path('summary/', views.summary_view, name='summary'),
    path('teams/', views.teams_view, name='teams'),

    # APIs
    path('api/summary/', views.api_summary_metrics, name='api_summary_metrics'),
    path('api/board/data/', views.api_board_data, name='api_board_data'),
    path('api/board/sync/', views.api_board_sync, name='api_board_sync'),
    path('api/tickets/<int:ticket_id>/update-status/', views.api_update_status, name='api_update_status'),

    path('api/tickets/<int:ticket_id>/update-priority/', views.api_update_priority, name='api_update_priority'),
    path('api/statuses/create/', views.api_create_status, name='api_create_status'),
    path('api/statuses/<int:status_id>/move/', views.api_move_status, name='api_move_status'),
    path('api/statuses/<int:status_id>/delete/', views.api_delete_status, name='api_delete_status'),
    path('api/categories/create/', views.api_create_category, name='api_create_category'),


    path('api/tickets/create/', views.api_create_ticket, name='api_create_ticket'),

    path('api/tickets/<int:ticket_id>/details/', views.api_ticket_details, name='api_ticket_details'),
    path('api/tickets/<int:ticket_id>/edit/', views.api_edit_ticket, name='api_edit_ticket'),
    path('api/tickets/<int:ticket_id>/upload-attachment/', views.api_upload_attachment, name='api_upload_attachment'),
    path('api/tickets/<int:ticket_id>/comments/', views.api_add_comment, name='api_add_comment'),
    path('api/comments/upload-image/', views.api_upload_comment_image, name='api_upload_comment_image'),
    path('api/tickets/<int:ticket_id>/delete/', views.api_delete_ticket, name='api_delete_ticket'),
    path('api/users/create/', views.api_create_user, name='api_create_user'),
    path('api/users/<int:user_id>/update-role/', views.api_update_user_role, name='api_update_user_role'),
    path('api/users/<int:user_id>/remove/', views.api_remove_user, name='api_remove_user'),
    path('api/profile/', views.api_get_profile, name='api_get_profile'),
    path('api/profile/update/', views.api_update_profile, name='api_update_profile'),
    path('api/team/update-name/', views.api_update_team_name, name='api_update_team_name'),
    path('api/team/update-icon/', views.api_update_team_icon, name='api_update_team_icon'),
    path('api/tickets/search/', views.api_search_tickets, name='api_search_tickets'),
]

