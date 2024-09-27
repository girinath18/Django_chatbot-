from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import signup, login_view, dashboard, profile_view

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('profile/', profile_view, name='profile'),
    path('dashboard/', dashboard, name='dashboard'),
    path(
        'logout/', 
        LogoutView.as_view(next_page='login'),  # Redirect to login page after logout
        name='logout'
    ),
]
