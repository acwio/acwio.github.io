from django.test import TestCase
from django.contrib.auth.models import User
from views import getEventList, getCategoryList
import requests


class EB_EventSearchTests(TestCase):
    def set_up(self):
        '''
        sets-up the user environment by pre-loading the category listing from the eventbrite api
        :return: [none]
        '''
        # create a dummy eb user
        User.objects.create_user(
            username='eb_user',
            password='eb_password'
        )



        # log the dummy user in
        self.client.login(username='eb_user', password='eb_password')

        # set-up the dummy user's session variables
        s = self.client.session

        if 'categories' in s:
            print 'already exists'

        # request each of the categories via the eventbrite api
        raw_response = requests.get("https://www.eventbriteapi.com/v3/categories", params={'token': 'BKKRDKVUVRC5WG4HAVLT'})

        # decode the response in JSON
        response = raw_response.json()

        # build and store dictionary for mapping id to category name in user session
        s['categories'] = {cat['id']: cat['name'] for cat in response['categories']}
        s.save()

    # Tests for Homepage (i.e. 127.0.0.1:8000)
    def test_index_view_basic(self):
        '''
            Tests the success of retrieving the index / homepage.
        :return:
        '''

        # submit a get request for the homepage
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    # Tests for /events/ without any specified categories.
    def test_events_no_category_valid(self):
        '''
            Tests the /events/ page (/display_results view) with no supplied categories
            and no supplied page number.
            (This should retrieve all events available.)
        :return:
        '''
        # set-up the user environment
        self.set_up()

        # submit a get request with a non-existent category (12345)
        response = self.client.get("/events/")
        self.assertEqual(response.status_code, 200)

    def test_events_no_category_valid_pagination(self):
        '''
            Tests the /events/ page (/display_results view) with no supplied categories and a specified page.
            (This should retrieve all events available.)
        :return:
        '''
        # set-up the user environment
        self.set_up()

        # submit a get request to navigate to page 2 of the events listing
        response = self.client.get("/events/", {'page': '2'})
        self.assertEqual(response.status_code, 200)

    def test_events_no_category_valid_pagination_outofrange(self):
        '''
            Tests the /events/ page (/display_results view) with no supplied categories and a specified page
            number that is out of range.
            (This should retrieve all events available.)
        :return:
        '''
        # set-up the user environment
        self.set_up()

        # submit a get request to navigate to page 99999 of the events listing
        response = self.client.get("/events/", {'page': '99999'})
        self.assertEqual(response.status_code, 200)

    def test_events_no_category_valid_pagination_nan(self):
        '''
            Tests the /events/ page (/display_results view) with no supplied categories and specifies a
            page number that is not a number.
            (This should retrieve all events available.)
        :return:
        '''
        # set-up the user environment
        self.set_up()

        # submit a get request to navigate to page 2 of the events listing
        response = self.client.get("/events/", {'page': 'dummy_word'})
        self.assertEqual(response.status_code, 200)


    # Tests for /events/ with specified categories.
    def test_events_category_valid(self):
        '''
            Tests the success of retrieving the /events/ page with three acceptable category inputs.
        :return:
        '''
        # set-up the user environment
        self.set_up()

        # submit a request with acceptable input
        response = self.client.get("/events/", {'cat1': '101', 'cat2': '110', 'cat3': '113'})
        self.assertEqual(response.status_code, 200)

    def test_events_category_valid_pagination(self):
        '''
            Tests the success of retrieving the /events/ page with three valid category inputs
            and a specified page number.
        :return:
        '''
        # set-up the user environment
        self.set_up()

        # submit a request with acceptable input and a specific page number
        response = self.client.get("/events/", {'cat1': '101', 'cat2': '110', 'cat3': '113', 'page': '2'})
        self.assertEqual(response.status_code, 200)

    def test_events_category_valid_pagination_outofrange(self):
        '''
            Tests the success of retrieving the /events/ page with three valid category inputs
            and a specified page number.
        :return:
        '''
        # set-up the user environment
        self.set_up()

        # submit a request with acceptable input and a specific page number
        response = self.client.get("/events/", {'cat1': '101', 'cat2': '110', 'cat3': '113', 'page': '9999'})
        self.assertEqual(response.status_code, 200)

    def test_events_category_valid_pagination_nan(self):
        '''
            Tests the success of retrieving the /events/ page with three valid category inputs
            and a page number that is not a number.
        :return:
        '''
        # set-up the user environment
        self.set_up()

        # submit a request with acceptable input and a specific page number
        response = self.client.get("/events/", {'cat1': '101', 'cat2': '110', 'cat3': '113', 'page': 'notanumber'})
        self.assertEqual(response.status_code, 200)

    def test_events_category_error_input_presence(self):
        '''
            Tests the /events/ page (/display_results view) with only two category inputs.
        :return:
        '''
        # set-up the user environment
        self.set_up()

        # submit a get request without the third category
        response = self.client.get("/events/", {'cat1': '101', 'cat2': '110'})
        self.assertEqual(response.context['form_error'], "Error: You must select 3 categories.")

    def test_events_category_error_uniqueness(self):
        '''
            Tests the /events/ page (/display_results view) with three category inputs, two of which are identical.
        :return:
        '''
        # set-up the user environment
        self.set_up()

        # submit a get request with two similar inputs
        response = self.client.get("/events/", {'cat1': '101', 'cat2': '101', 'cat3': '110'})
        self.assertEqual(response.context['form_error'], "Error: Selections must be unique.")

    def test_events_category_error_validity(self):
        '''
            Tests the /events/ page (/display_results view) with three category inputs, one of which is an invalid
            category.
        :return:
        '''
        # set-up the user environment
        self.set_up()

        # submit a get request with a non-existent category (12345)
        response = self.client.get("/events/", {'cat1': '12345', 'cat2': '101', 'cat3': '110'})
        self.assertEqual(response.context['form_error'],
                         "Error: One or more of the selected categories no longer exists.")