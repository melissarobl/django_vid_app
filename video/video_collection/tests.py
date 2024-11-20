from django.test import TestCase
from django.urls import reverse # converts name of URL into path for your server
from django.db import IntegrityError, transaction
from .models import Video
from django.core.exceptions import ValidationError

# is correct title shown on your homepage?
class TestHomePageMessage(TestCase):

    def test_app_title_message_shown_on_home_page(self):
        url = reverse('home') #generates correct URL
        self.client.get(url) # get page at given URL
        response = self.client.get(url)
        self.assertContains(response, 'Exercise Videos')

class TestAddVideos(TestCase):

    def test_add_video(self):

        valid_video = {
            'name': 'yoga',
            'url': 'https://www.youtube.com/watch?v=4vTJHUDB5ak',
            'notes': 'yoga for neck and shoulders'
        }

        url = reverse('add_video')
        response = self.client.post(url, data=valid_video, follow=True) # if redirected as part of request, then follow redirect

        self.assertTemplateUsed(response, 'video_collection/video_list.html')
        # does the video list show the new video?
        self.assertContains(response, 'yoga')
        self.assertContains(response, 'yoga for neck and shoulders')
        self.assertContains(response, 'https://www.youtube.com/watch?v=4vTJHUDB5ak')

        video_count = Video.objects.count()
        self.assertEqual(1, video_count)

        video = Video.objects.first()

        self.assertEqual('yoga', video.name)
        self.assertEqual('https://www.youtube.com/watch?v=4vTJHUDB5ak', video.url)
        self.assertEqual('yoga for neck and shoulders', video.notes)
        self.assertEqual('4vTJHUDB5ak', video.video_id)

    def test_add_video_invalid_url_not_added(self):

        invalid_video_urls = [
                'https://www.youtube.com/watch',
                'https://www.youtube.com/watch?',
                'https://www.youtube.com/watch?abc=123',
                'https://www.youtube.com/watch?v=',
                'https://github.com',
                'https://minneapolis.edu',
                'https://minneapolis.edu?v=123456',
            ]

        for invalid_video_url in invalid_video_urls:

            new_video ={
                'name': 'example',
                'url': invalid_video_url,
                'notes': 'example notes',
            }
            url = reverse('add_video')
            response = self.client.post(url, data=new_video)

            self.assertTemplateNotUsed('video_collection/add.html')

            messages = response.context['messages']
            message_texts = [ message.message for message in messages ]

            self.assertIn('Invalid YouTube URL', message_texts)
            self.assertIn('Please check the data entered.', message_texts)

            video_count = Video.objects.count()
            self.assertEqual(0, video_count)


class TestVideoList(TestCase):

    def test_all_videos_displayed_in_correct_order(self):
        # these will go in database:
        v1 = Video.objects.create(name='XYZ', notes='example', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=124')
        v3 = Video.objects.create(name='AAA', notes='example', url='https://www.youtube.com/watch?v=125')
        v4 = Video.objects.create(name='lmn', notes='example', url='https://www.youtube.com/watch?v=126')

        expected_video_order = [ v3, v2, v4, v1 ]
        url = reverse('video_list')
        response = self.client.get(url)

        videos_in_template = list(response.context['videos'])

        self.assertEqual(videos_in_template, expected_video_order)

    def test_not_video_message(self):
        url = reverse('video_list')
        response = self.client.get(url)
        self.assertContains(response, 'No videos')
        self.assertEqual(0, len(response.context['videos']))

    def test_video_number_message_one_video(self):
        v1 = Video.objects.create(name='XYZ', notes='example', url='https://www.youtube.com/watch?v=123')
        url = reverse('video_list')
        response = self.client.get(url)

        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')

    def test_video_number_message_two_videos(self):
        v1 = Video.objects.create(name='XYZ', notes='example', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='XYP', notes='example', url='https://www.youtube.com/watch?v=124')

        url = reverse('video_list')
        response = self.client.get(url)

        self.assertContains(response, '2 videos')


class TestVideoSearch(TestCase):

    def test_video_search_matches(self):
        v1 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v2 = Video.objects.create(name='nope', notes='example', url='https://www.youtube.com/watch?v=789')
        v3 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        v4 = Video.objects.create(name='hello aBc', notes='example', url='https://www.youtube.com/watch?v=101')

        expected_video_order = [v1, v3, v4]
        response = self.client.get(reverse('video_list') + '?search_term=abc')
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)

    def test_video_search_no_matches(self):
        v1 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v2 = Video.objects.create(name='nope', notes='example', url='https://www.youtube.com/watch?v=789')
        v3 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        v4 = Video.objects.create(name='hello aBc!!!', notes='example', url='https://www.youtube.com/watch?v=101')

        expected_video_order = []  # empty list
        response = self.client.get(reverse('video_list') + '?search_term=kittens')
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)
        self.assertContains(response, 'No videos')

class TestVideoModel(TestCase):

    def duplicate_video_raises_integrity_error(self):
        v1= Video.objects.create(name='ZYX', notes='example', url='https://www.youtube.com/watch?v=123')
        with self.assertRaises(IntegrityError):
            Video.objects.create(name='ZYX', notes='example', url='https://www.youtube.com/watch?v=123')


    def test_create_id(self):
        video = Video.objects.create(name='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4')
        self.assertEqual('IODxDxX7oi4', video.video_id)


    def test_create_id_valid_url_with_time_parameter(self):
        # a video that is playing and paused may have a timestamp in the query
        video = Video.objects.create(name='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4&ts=14')
        self.assertEqual('IODxDxX7oi4', video.video_id)


    def test_create_video_notes_optional(self):
        v1 = Video.objects.create(name='example', url='https://www.youtube.com/watch?v=67890')
        v2 = Video.objects.create(name='different example', notes='example',
                                  url='https://www.youtube.com/watch?v=12345')
        expected_videos = [v1, v2]
        database_videos = Video.objects.all()
        self.assertCountEqual(expected_videos,
                              database_videos)  # check contents of two lists/iterables but order doesn't matter.

    def test_invalid_urls_raise_validation_error(self):
        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch/somethingelse',
            'https://www.youtube.com/watch/somethingelse?v=1234567',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            '12345678',
            'hhhhhhhhhhhhttps://www.youtube.com/watch?',
            'http://www.youtube.com/watch?',
            'https://github.com',
            'https://minneapolis.edu'
            'https://minneapolis.edu?v=123456'
            ''
        ]

        for invalid_url in invalid_video_urls:
            with self.assertRaises(ValidationError):
                Video.objects.create(name='example', url=invalid_url, notes='example note')
        self.assertEqual(0, Video.objects.count())


class TestVideoDetails(TestCase):

    def setUp(self):
        video = Video.objects.create(name='example', url='https://www.youtube.com/watch?v=YYgYRSkFoJs', notes = 'test notes',) # set up example dictionary info

    def test_verify_page_shows_all_information_on_one_video_if_exists(self):
        video_1 = Video.objects.get(pk=1)  # get video object with pk of 1

        response = self.client.get(reverse('video_details', kwargs={'video_pk':1})) # get request to video_details page for video with pk 1

        self.assertTemplateUsed(response, 'video_collection/video_details.html') # make sure the video_details template was used

        # what data was sent to the template?
        data_rendered = response.context['video']
        self.assertEqual(data_rendered, video_1)

        # assert the following is shown on the page displayed:
        self.assertContains(response, 'test notes')
        self.assertContains(response, 'https://www.youtube.com/watch?v=YYgYRSkFoJs')
        self.assertContains(response, 'example')

    
    def test_verify_page_request_for_nonexistent_video_returns_404(self):
        response = self.client.get(reverse('video_details', kwargs={'video_pk':201})) # get request for video_details view for non-existent pk
        self.assertEqual(404, response.status_code) # make sure response's status code is 404

