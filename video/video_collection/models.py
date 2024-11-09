from urllib import parse
from django.core.exceptions import ValidationError
from django.db import models


# Create your models here. These are the items with input fields on your form/view

class Video(models.Model):
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=400)
    notes = models.TextField(blank=True, null=True) # blank means notes field is optional in fields
    video_id = models.CharField(max_length=40, unique=True)

    def save(self, *args, **kwargs):
        # extract the video id from a YouTube URL
        if not self.url.startswith('https://www.youtube.com/watch'):
            raise ValidationError('Not a YouTube URL {self.url}')

        url_components = parse.urlparse(self.url)
        query_string = url_components.query # 'v=123awe56'
        if not query_string:
            raise ValidationError(f'Invalid YouTube URL {self.url}')
        parameters = parse.parse_qs(query_string, strict_parsing=True) # dictionary
        v_parameters_list = parameters.get('v') # return None if no key found, e.g. abc=1234
        if not v_parameters_list: #  checking if None ore empty list
            raise ValidationError(f'Invalid YouTube URL, missing parameters {self.url}')
        self.video_id = v_parameters_list[0] # string

        super().save(*args, **kwargs) # call original Django save rules overwritten by above code


    def __str__(self):
        return f'ID: {self.pk}, Name: {self.name}, URL: {self.url}, Video ID: {self.video_id}, Notes: {self.notes[:200]}'
        # hint: if errors when first testing the add video function, it's probably in error in syntax in this line.
