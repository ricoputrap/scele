from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('register/', views.register, name="register"),
    path('profile/', views.view_profile, name="profile"),
    path('course/', views.view_course, name="course"),
    path('course/badges', views.view_course_badges, name="course-badges"),
    path('badge/<code>', views.view_badge_detail, name="badge-detail"),
    path('forum/', views.view_forum, name="forum"),
    path('forum/addpost/', views.add_post, name="addpost"),
    path('forum/post/<id>', views.view_post, name="post"),
    path('forum/post/edit/<id>', views.edit_post, name="edit-post"),
    path('forum/reply/edit/<id>', views.edit_reply, name="edit-reply"),
    path('forum/deleteitem/', views.delete_item, name="deleteitem"),
    path('forum/addreply/<post_id>/<parent_type>/<parent_id>', views.add_reply, name="addreply"),
    path('forum/post/addlike/', views.add_like, name="addlike"),
    path('forum/post/unlike/', views.unlike, name="unlike"),
    path('forum/post/viewlikers/', views.view_likers, name="viewlikers"),
    path('notifpage/', views.view_notification_page, name="notif-page"),
    path('getnotif/', views.get_notif_obj, name="get-notif"),
]