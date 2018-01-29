import os
import unittest
import json
from unittest.mock import MagicMock, patch
from app import create_app, db
from app.resources import TwilioResponseAPI


class ReplySiteTestCase(unittest.TestCase):
    """This class is our base test case that we inherit from in other cases"""

    def setUp(self):
        """Define test variables and initialize app."""
        os.environ['APP_MODE'] = "test"
        self.app = create_app()
        self.client = self.app.test_client
        self.guest = {'name': 'John and Jane Doe', 'total_attendees': 2, "phone_number": "5555555555"}
        self.invalid_guest = {'name': 'Steve and Dora Explora', 'total_attendees': 'blurple'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()


class GuestTestCase(ReplySiteTestCase):
    """This class tests our Guest api for adding, updating, and listing guests"""

    def test_guest_creation(self):
        """Test API can create a Guest (POST request)"""
        res = self.client().post('/api/guest', data=self.guest)
        self.assertEqual(res.status_code, 201)
        returned_guest = json.loads(res.data)
        self.assertEquals(returned_guest['name'], "John and Jane Doe")
        self.assertEquals(returned_guest['id'], 1)
        self.assertEquals(returned_guest['total_attendees'], 2)
        self.assertEquals(returned_guest['phone_number'], '5555555555')

    def test_api_can_get_all_guests(self):
        """Test API can get a guest (GET request)."""
        res = self.client().post('/api/guest', data=self.guest)
        self.assertEqual(res.status_code, 201)
        res = self.client().get('/api/guests')
        self.assertEqual(res.status_code, 200)
        self.assertIn('John and Jane Doe', str(res.data))

    def test_api_can_get_guest_by_id(self):
        """Test API can get a single guest by using it's id."""
        res = self.client().post('/api/guest', data=self.guest)
        self.assertEqual(res.status_code, 201)
        returned_guest = json.loads(res.data)
        result = self.client().get('/api/guest/{}'.format(returned_guest['id']))
        self.assertEqual(result.status_code, 200)
        self.assertIn('John and Jane Doe', str(result.data))

    def test_guest_can_be_edited(self):
        """Test API can edit an existing guest. (PUT request)"""
        res = self.client().post('/api/guest', data=self.guest)
        self.assertEqual(res.status_code, 201)
        returned_guest = json.loads(res.data)
        result = self.client().put('/api/guest/{}'.format(returned_guest['id']),
                                   data={
                                        "name": "Steve and Dan Testerton"
                                    })
        self.assertEqual(result.status_code, 200)
        result = self.client().get('/api/guest/{}'.format(returned_guest['id']))
        self.assertEqual(result.status_code, 200)
        self.assertIn('Steve and Dan Testerton', str(result.data))

    def test_guest_deletion(self):
        """Test API can delete an existing guest. (DELETE request)."""
        res = self.client().post('/api/guest', data=self.guest)
        self.assertEqual(res.status_code, 201)
        returned_guest = json.loads(res.data)
        result = self.client().delete('/api/guest/{}'.format(returned_guest['id']))
        self.assertEqual(result.status_code, 200)
        # Test to see if it exists, should return a 404
        result = self.client().get('/api/guest/{}'.format(returned_guest['id']))
        self.assertEqual(result.status_code, 404)

    def test_guest_create_bad_data(self):
        """Test API can create a Guest (POST request)"""
        res = self.client().post('/api/guest', data=self.invalid_guest)
        self.assertEqual(res.status_code, 400)
        returned = json.loads(res.data)
        self.assertIn(returned['errors'], "Total Attendees must be an integer number")


class TwilioTestCase(ReplySiteTestCase):
    """This class tests our Twilio end points"""

    def test_save_the_date_yes(self):
        """Tests that we properly handle save the date YES SMS responses"""
        # add our guest first
        res = self.client().post('/api/guest', data=self.guest)
        self.assertEqual(res.status_code, 201)

        message_mock = MagicMock()
        with patch.object(TwilioResponseAPI, '_get_twilio_messager', return_value=message_mock) as local_mock:
            response = self.client().post('/api/sms', data={'From': "5555555555", 'Body': "Yes"})
            self.assertEqual(response.status_code, 200)
            local_mock.assert_called()
            message_mock.message.assert_called_with("Thanks for confirming, we'll be in touch with more info soon!")
            message_mock.message.assert_called_once()
        result = self.client().get('/api/guest/1')
        self.assertEqual(result.status_code, 200)
        returned_guest = json.loads(result.data)
        self.assertTrue(returned_guest['date_saved'])

    def test_save_the_date_no(self):
        """Tests that we properly handle save the date NO SMS responses"""
        # add our guest first
        res = self.client().post('/api/guest', data=self.guest)
        self.assertEqual(res.status_code, 201)

        message_mock = MagicMock()
        with patch.object(TwilioResponseAPI, '_get_twilio_messager', return_value=message_mock) as local_mock:
            response = self.client().post('/api/sms', data={'From': "5555555555", 'Body': "No"})
            self.assertEqual(response.status_code, 200)
            local_mock.assert_called()
            message_mock.message.assert_called_with("We understand life can be busy. We'll still be thinking of you "
                                                    "on our special day")
            message_mock.message.assert_called_once()
        result = self.client().get('/api/guest/1')
        self.assertEqual(result.status_code, 200)
        returned_guest = json.loads(result.data)
        self.assertFalse(returned_guest['date_saved'])

    def test_bad_phone(self):
        """Tests that we properly handle save the date NO SMS responses"""
        # add our guest first
        res = self.client().post('/api/guest', data=self.guest)
        self.assertEqual(res.status_code, 201)

        message_mock = MagicMock()
        with patch.object(TwilioResponseAPI, '_get_twilio_messager', return_value=message_mock) as local_mock:
            response = self.client().post('/api/sms', data={'From': "1234567890", 'Body': "No"})
            self.assertEqual(response.status_code, 200)
            local_mock.assert_called()
            message_mock.message.assert_called_with("I don't recognize your number or something is very broken. "
                                                    "Please reach out to Andrew or Sarah directly for help")
            message_mock.message.assert_called_once()

    def test_rsvp_yes(self):
        """Tests that we properly handle save the date NO SMS responses"""
        # add our guest first
        res = self.client().post('/api/guest', data=self.guest)
        self.assertEqual(res.status_code, 201)

        message_mock = MagicMock()
        with patch.object(TwilioResponseAPI, '_get_twilio_messager', return_value=message_mock) as local_mock:
            response = self.client().post('/api/sms', data={'From': "5555555555", 'Body': "RSVP Yes 2"})
            self.assertEqual(response.status_code, 200)
            local_mock.assert_called()
            message_mock.message.assert_called_with("We're so glad you're joining us on our special day! Remember to "
                                                    "keep up with the wedding site for any updates!")
            message_mock.message.assert_called_once()
        result = self.client().get('/api/guest/1')
        self.assertEqual(result.status_code, 200)
        returned_guest = json.loads(result.data)
        self.assertTrue(returned_guest['rsvp'])

    def test_rsvp_yes_less_people(self):
        """Tests that we properly handle RSVP Yes SMS responses"""
        # add our guest first
        res = self.client().post('/api/guest', data=self.guest)
        self.assertEqual(res.status_code, 201)

        message_mock = MagicMock()
        with patch.object(TwilioResponseAPI, '_get_twilio_messager', return_value=message_mock) as local_mock:
            response = self.client().post('/api/sms', data={'From': "5555555555", 'Body': "RSVP Yes 1"})
            self.assertEqual(response.status_code, 200)
            local_mock.assert_called()
            message_mock.message.assert_called_with("We're so glad you're joining us on our special day! Remember to "
                                                    "keep up with the wedding site for any updates!")
            message_mock.message.assert_called_once()
        result = self.client().get('/api/guest/1')
        self.assertEqual(result.status_code, 200)
        returned_guest = json.loads(result.data)
        self.assertTrue(returned_guest['rsvp'])
        self.assertEqual(returned_guest['total_attendees'], 1)

    def test_rsvp_no(self):
        """Tests that we properly handle save the date NO SMS responses"""
        # add our guest first
        res = self.client().post('/api/guest', data=self.guest)
        self.assertEqual(res.status_code, 201)

        message_mock = MagicMock()
        with patch.object(TwilioResponseAPI, '_get_twilio_messager', return_value=message_mock) as local_mock:
            response = self.client().post('/api/sms', data={'From': "5555555555", 'Body': "RSVP No"})
            self.assertEqual(response.status_code, 200)
            local_mock.assert_called()
            message_mock.message.assert_called_with("Thank you for responding. We understand life can be busy. "
                                                    "We'll be thinking of you on our special day.")
            message_mock.message.assert_called_once()
        result = self.client().get('/api/guest/1')
        self.assertEqual(result.status_code, 200)
        returned_guest = json.loads(result.data)
        self.assertFalse(returned_guest['rsvp'])

    def test_rsvp_yes_too_many_people(self):
        """Tests that we properly handle save the date NO SMS responses"""
        # add our guest first
        res = self.client().post('/api/guest', data=self.guest)
        self.assertEqual(res.status_code, 201)

        message_mock = MagicMock()
        with patch.object(TwilioResponseAPI, '_get_twilio_messager', return_value=message_mock) as local_mock:
            response = self.client().post('/api/sms', data={'From': "5555555555", 'Body': "RSVP Yes 5"})
            self.assertEqual(response.status_code, 200)
            local_mock.assert_called()
            message_mock.message.assert_called_with("I'm sorry, but we have to keep our wedding small. We ask that "
                                                    "you only bring up to 2 people. If you need extra, please reach "
                                                    "out to Andrew and Sarah and we can work with you")
            message_mock.message.assert_called_once()

    def test_stop(self):
        """Tests that we properly handle STOP SMS responses"""
        # add our guest first
        res = self.client().post('/api/guest', data=self.guest)
        self.assertEqual(res.status_code, 201)

        message_mock = MagicMock()
        with patch.object(TwilioResponseAPI, '_get_twilio_messager', return_value=message_mock) as local_mock:
            response = self.client().post('/api/sms', data={'From': "5555555555", 'Body': "Stop"})
            self.assertEqual(response.status_code, 200)
            local_mock.assert_called()
            message_mock.message.assert_called_with("We're so sorry! We won't text you again about our wedding plans.")
            message_mock.message.assert_called_once()
            result = self.client().get('/api/guest/1')
            self.assertEqual(result.status_code, 200)
            returned_guest = json.loads(result.data)
            self.assertTrue(returned_guest['stop_notifications'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
