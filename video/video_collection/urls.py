from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), # each path corresponds to a page
    path('add', views.add, name='add_video'),
    path('video_list', views.video_list, name='video_list'),
    path('videos/<int:video_pk>/', views.video_details, name='video_details'),
]