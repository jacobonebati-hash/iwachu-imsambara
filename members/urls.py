from django.urls import path
from . import views

urlpatterns = [
    path(
        '',
        views.home,
        name='home'
    ),

    path(
        'register/',
        views.register_member,
        name='register_member'
    ),

    path(
        'members/',
        views.members_list,
        name='members_list'
    ),

    path(
        'members/<int:member_id>/',
        views.member_detail,
        name='member_detail'
    ),

    path(
        'members/<int:member_id>/edit/',
        views.edit_member,
        name='edit_member'
    ),

    path(
        'members/<int:member_id>/delete/',
        views.delete_member,
        name='delete_member'
    ),
]