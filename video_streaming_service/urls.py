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
from django.conf import settings
from django.conf.urls.static import static
from my_website_app.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ShowListView.as_view(), name='shows'),
    path('home/', home_screen_view, name='home_screen'),
    path('show/<int:pk>/', ShowDetail.as_view(), name='show'),
    path('api/episodes/<int:season_id>/', get_episodes_by_season, name='api-episodes-by-season'),
    # path('show/<slug:show_slug>/', ShowDetail.as_view(), name='show'),
    path('create-show/', ShowCreate.as_view(), name='show-create'),
    path('show-update/<int:pk>/', ShowUpdate.as_view(), name='show-update'),
    path('show-delete/<int:pk>/', ShowDelete.as_view(), name='show-delete'),
    path('register/', registration_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('login/', login_view, name='login'),
    path('account/', account_view, name='account'),
    path('account/edit_profile', edit_profile, name='edit_profile'),
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
    path('submit_review/<int:show_id>/', submit_review, name='submit_review'),
    path('account/change_password', change_password, name='change_password'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_URL)