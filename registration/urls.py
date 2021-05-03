
from django.urls import path, reverse_lazy

from django.contrib.auth.decorators import login_required

from .decorators import verified_email

from django.contrib.auth import views as auth_views

from . import views

app_name = 'registration'

urlpatterns = [
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('phone_link/', views.phone_link, name='phone_link'),
    path('profile_pic_link/', views.profile_pic_link, name='profile_pic_link'),
    path('change_password/', views.change_password, name='change_password'),
    path('profile_page/', views.profile_page, name='profile_page'),
    path('reset_password/', verified_email(auth_views.PasswordResetView.as_view(
        success_url = reverse_lazy('registration:password_reset_done'),
        email_template_name = 'registration/email_templates/password_reset_email.html'
    )), name='password_reset'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(
        success_url=reverse_lazy('registration:password_reset_complete'),
    ), name='password_reset_confirm'),
    path('reset_password_complete/', verified_email(auth_views.PasswordResetCompleteView.as_view()), name='password_reset_complete'),
    path('activate/<uidb64>/<token>/', views.verify_email, name='verify'),
    path('add_review/', views.add_review, name='add_review'),
    path('edit_review/', views.edit_review, name='edit_review'),
    path('delete_review/', views.delete_review, name='delete_review'),
    path('average_rating/', views.get_average_rating, name='average_rating'),
    path('top_up_balance/', views.top_up_balance, name='top_up_balance'),
    path('purchase_history/', views.purchase_history, name='purchase_history'),
    path('get_stripe_token/', views.get_stripe_token, name='get_stripe_token'),
    
]
