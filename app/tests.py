"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".
"""

import django
from django.test import TestCase
from redcap import Project, RedcapError

# TODO: Configure your database in settings.py and sync before running tests.

class ViewTest(TestCase):
    """Tests for the application views."""

    if django.VERSION[:2] >= (1, 7):
        # Django 1.7 requires an explicit setup() when running tests in PTVS
        @classmethod
        def setUpClass(cls):
            super(ViewTest, cls).setUpClass()
            django.setup()

    def test_home(self):
        """Tests the home page."""
        response = self.client.get('/')
        self.assertContains(response, 'Home Page', 1, 200)
        print "test_home: PASSED"

    def test_contact(self):
        """Tests the contact page."""
        response = self.client.get('/contact')
        self.assertContains(response, 'Contact', 3, 200)
        print "test_contact: PASSED"

    def test_about(self):
        """Tests the about page."""
        response = self.client.get('/about')
        self.assertContains(response, 'About', 3, 200)
        print "test_about: PASSED"

    def test_messaging(self):
        """Tests the messaging page."""
        response = self.client.get('/messaging')
        self.assertContains(response, 'Messaging', 3, 200)
        print "test_messaging: PASSED"

    def test_redcap_connection(self):
        """Tests connecting to the REDCap database."""

        URL = 'https://hcbredcap.com.br/api/'
        TOKEN = 'F2C5AEE8A2594B0A9E442EE91C56CC7A'

        project = Project(URL, TOKEN)
        self.assertIsNotNone(project)

        print "test_redcap_connenction: PASSED"
