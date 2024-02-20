"""
URL configuration for video_streaming_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from my_website_app.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ShowListView.as_view(), name='shows'),
    path('home/', home_screen_view, name='home_screen'),
    path('show/<int:pk>/', ShowDetail.as_view(), name='show'),
    path('create-show/', ShowCreate.as_view(), name='show-create'),
    path('show-update/<int:pk>/', ShowUpdate.as_view(), name='show-update'),
    path('show-delete/<int:pk>/', ShowDelete.as_view(), name='show-delete'),
    path('register/', registration_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('login/', login_view, name='login'),
    path('account/', account_view, name='account'),
    path('show/<int:show_id>/add_to_favorites/', favourite_add, name='favourite_add'),
    path('show/<int:show_id>/remove_from_favorites/', remove_from_favorites, name='remove_from_favorites'),
    path('favourites/', favourite_list, name='favourites'),
    path('movies/', movies, name='movies'),
    path('movies/category/<slug:category_slug>/', movies, name='shows_by_category'),
    path('movies/search/', search, name='search'),
    path('activate/<uidb64>/<token>', activate, name='activate'),
    path('forgot_password/', forgot_password, name='forgot_password'),
    path('reset_password_validate/<uidb64>/<token>', reset_password_validate, name='reset_password_validate'),
    path('reset_password/', reset_password, name='reset_password'),

    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'),
         name='password_change_done'),

    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html'),
         name='password_change'),

    path('password_reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_done.html'),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
         name='password_reset_complete'),
]