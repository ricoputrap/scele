from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('register/', views.register, name="register"),
    path('profile/', views.view_profile, name="profile"),
    path('course/', views.view_course, name="course"),
]