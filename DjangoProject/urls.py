from django.contrib import admin
from django.urls import path
from main import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from main.views import  sql_api

urlpatterns = ([
    path('admin/', admin.site.urls),
    path('', views.glav, name='glav'),
    path('stories/', views.stories, name='stories'),
    path('support/', views.support, name='support'),
    path('about/', views.profile_view, name='about'),
    path('about/edit/', views.verify_phone, name='edit_profile'),
    path('login/telegram-login/', views.telegram_login, name='telegram_login'),
    path('create/', views.create_help_request, name='create_help_request'),
    path('list/', views.help_requests_list, name='help_requests_list'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('api/sql/', sql_api),
]
               + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
