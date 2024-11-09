from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .forms import VideoForm
from .models import Video


def home(request):
    app_name = 'Exercise Videos'
    return render(request, 'video_collection/home.html', { 'app_name': app_name})

def add(request):

    if request.method == 'POST':
        new_video_form = VideoForm(request.POST)
        if new_video_form.is_valid():
            try:
                new_video_form.save()
                return redirect('video_list')
                #messages.info(request, 'Video added successfully')
            except ValidationError:
                messages.warning(request, 'Invalid YouTube URL')
            except IntegrityError:
                messages.warning(request, 'You already added that video.')

            #todo show success message message or redirect to list of videos

        messages.warning(request, 'Please check the data entered.')
        return render(request, 'video_collection/add.html', {'new_video_form': new_video_form}) #redisplay data user typed in so they can make changes


    new_video_form = VideoForm() # make new empty video form
    return render(request, 'video_collection/add.html', { 'new_video_form': new_video_form})

def video_list(request):
    videos = Video.objects.all()
    return render(request, 'video_collection/video_list.html', { 'videos': videos})