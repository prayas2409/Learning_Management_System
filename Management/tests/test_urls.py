from django.test import TestCase, client
from django.urls import reverse, resolve
from Management.views import *

class TestUrls(TestCase):
    def test_add_mentor_url(self):
        """ This test case is for testing mentor url"""
        url = reverse('mentor')
        self.assertEquals(resolve(url).func.view_class, AddMentorAPIView)

    def test_invalid_add_mentor_url(self):
        """ This test case is for testing mentor url"""
        url = reverse('mentor')
        self.assertNotEqual(resolve(url).func, AddMentorAPIView)

    def test_getting_mentor_details_url(self):
        """ This test case is for testing mentor details url"""
        url = reverse('mentordetails')
        self.assertEquals(resolve(url).func.view_class, GetMentorDetailsAPIView)

    def test_invalid_getting_mentor_details_url(self):
        """ This test case is for testing mentor details url"""
        url = reverse('mentordetails')
        self.assertNotEqual(resolve(url).func, GetMentorDetailsAPIView)
