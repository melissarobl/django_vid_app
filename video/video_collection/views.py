from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models.functions import Lower
from .forms import VideoForm, SearchForm
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

    search_form = SearchForm(request.GET) # build form from data user has sent to app

    if search_form.is_valid():
        search_term = search_form.cleaned_data['search_term'] # same field as found in forms.py, example: 'yoga' or 'squats'
        videos = Video.objects.filter(name__icontains=search_term).order_by(Lower('name'))

    else: # form is not filled in or this is the first time the user sees the page
        search_form = SearchForm()
        videos = Video.objects.order_by(Lower('name'))

    return render(request, 'video_collection/video_list.html', { 'videos': videos, 'search_form': search_form})