"""us3000 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
import os
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from words import views as word_views
from profiles import views as profiles_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', word_views.IndexView.as_view(), name="home"),
    path('registration/', profiles_views.RegistrationView.as_view(), name="registration"),
    path('login/', profiles_views.LoginView.as_view(), name="login"),
    path('logout/', profiles_views.LogoutView.as_view(), name="logout"),
    path('learning-state/', word_views.LearningStateView.as_view(), name="learning_state"),

]

if settings.DEBUG:
    urlpatterns += static('/media/', document_root=os.path.join(settings.BASE_DIR, 'media'))
