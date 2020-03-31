from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('register/', views.register, name="register"),
    path('profile/', views.view_profile, name="profile"),
    path('course/', views.view_course, name="course"),
    path('badge/<code>', views.view_badge_detail, name="badge-detail"),
    path('forum/', views.view_forum, name="forum"),
    path('forum/post/<id>', views.view_post, name="post"),
    path('forum/addpost/', views.add_post, name="addpost"),
    path('forum/addreply/<post_id>/<parent_type>/<parent_id>', views.add_reply, name="addreply"),
]