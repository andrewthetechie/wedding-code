from functools import wraps
from cerberus import Validator
from flask import abort, current_app
from flask import request, Response
from flask_restful import Resource
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse


# https://www.twilio.com/docs/guides/how-to-secure-your-flask-app-by-validating-incoming-twilio-requests#disable-request-validation-during-resting
def validate_twilio_request(f):
    """Validates that incoming requests genuinely originated from Twilio"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
        # if we're in testing mode, just dont validate anything
        if current_app.config['TESTING']:
            return f(*args, **kwargs)
        # Create an instance of the RequestValidator class
        validator = RequestValidator(current_app.config['TWILIO_AUTH_TOKEN'])

        # Validate the request using its URL, POST data,
        # and X-TWILIO-SIGNATURE header
        request_valid = validator.validate(
            request.url,
            request.form,
            request.headers.get('X-TWILIO-SIGNATURE', ''))

        # Continue processing the request if it's valid (or if DEBUG is True)
        # and return a 403 error if it's not
        if request_valid or current_app.debug:
            return f(*args, **kwargs)
        else:
            return abort(403)
    return decorated_function


# https://flask-restful.readthedocs.io/en/latest/extending.html#resource-method-decorators
class TwilioResource(Resource):
    """Used to validate all incoming request to twilio resources"""
    method_decorators = [validate_twilio_request]


class GuestsResource(Resource):
    def __init__(self, **kwargs):
        self.Guest = kwargs['guest_object']

    @staticmethod
    def str2bool(v):
        return v.lower() in ("yes", "true", "t", "1")


class GuestsList(GuestsResource):
    def get(self):
        if request.query_string is not None:
            try:
                guest_filter = request.args['guest_filter'].lower()
                if guest_filter == "all_contacts":
                    our_list = self.Guest.get_all_contacts()
                else:
                    guest_filter_value = request.args['guest_filter_value'].lower()
                    if guest_filter_value == "none" or guest_filter_value == "null":
                        guest_filter_value = None
                    else:
                        guest_filter_value = self.str2bool(guest_filter_value)
                    if guest_filter == "std" or guest_filter == "savethedate":
                        our_list = self.Guest.get_std_list(guest_filter_value)
                    elif guest_filter == "rsvp":
                        our_list = self.Guest.get_rsvp_list(guest_filter_value)
                    else:
                        our_list = self.Guest.get_all()
            except KeyError:
                our_list = self.Guest.get_all()

        to_return = []
        for guest in our_list:
            to_return.append(guest.to_json())
        return to_return, 200


class GuestsAPI(GuestsResource):
    def get(self, guest_id):
        guest = self.Guest.query.filter_by(id=guest_id).first_or_404()
        return guest.to_json(), 200

    def post(self):
        # this logic is so the post can handle form posts AND json posts
        # form posts everything is a string, so we have to do some interpretation before validating
        if request.headers['Content-Type'].lower() == "application/json":
            data = request.json
        else:
            data = request.form.to_dict()
            try:
                data['total_attendees'] = int(data['total_attendees'])
            except ValueError:
                return {"errors": "Total Attendees must be an integer number"}, 400
            except KeyError:
                pass

        validator = Validator(schema=self.Guest.SCHEMA)
        if not validator.validate(data):
            return {"errors": validator.errors}, 400

        guest = self.Guest(**data)
        guest.save()

        return guest.to_json(), 201

    def delete(self, guest_id):
        guest = self.Guest.query.filter_by(id=guest_id).first_or_404()
        guest.delete()
        return 200

    def put(self, guest_id):
        guest = self.Guest.query.filter_by(id=guest_id).first_or_404()
        # this logic is so the post can handle form posts AND json posts
        # form posts everything is a string, so we have to do some interpretation before validating
        if request.headers['Content-Type'].lower() == "application/json":
            data = request.json
        else:
            data = request.form.to_dict()
            try:
                data['total_attendees'] = int(data['total_attendees'])
            except ValueError:
                return {"errors": "Total Attendees must be an integer number"}, 400
            except KeyError:
                pass

            try:
                data['date_saved'] = self.str2bool(data['date_saved'])
            except KeyError:
                pass

            try:
                data['rsvp'] = self.str2bool(data['rsvp'])
            except KeyError:
                pass

            try:
                data['stop_notifications'] = self.str2bool(data['stop_notifications'])
            except KeyError:
                pass

        validator = Validator(schema=self.Guest.PUT_SCHEMA)

        if not validator.validate(data):
            return {"errors": validator.errors}, 400

        for key, value in data.items():
            setattr(guest, key, value)
        guest.save()

        return guest.to_json(), 200


class TwilioResponseAPI(TwilioResource):

    def __init__(self, **kwargs):
        self.Guest = kwargs['guest_object']

    @staticmethod
    def _get_twilio_messager():
        return MessagingResponse()

    def post(self):
        rsvp_help_msg = "Sorry, but I couldn't understand that. To RSVP, use RSVP Yes/No #of attendees. " \
                            "Examples: RSVP yes 2 or RSVP no."

        resp = self._get_twilio_messager()

        from_number = request.values.get('From', None).strip("+1")
        body = request.values.get('Body', None).lower()

        guest = self.Guest.query.filter_by(phone_number=from_number).first()
        if guest is None:
            current_app.logger.debug("Invalid response number {} - body {}".format(from_number, body))
            resp.message("I don't recognize your number or something is very broken. "
                         "Please reach out to Andrew or Sarah directly for help")
            return Response(str(resp), status=200, mimetype="application/xml")

        if body[:3] == "yes":
            # We have a keeper! Update their confirmation status
            guest.date_saved = True
            guest.save()
            resp.message("Thanks for confirming, we'll be in touch with more info soon!")
            return Response(str(resp), status=200, mimetype="application/xml")

        if body[:2] == "no":
            # declined guest
            guest.date_saved = False
            guest.save()
            resp.message("We understand life can be busy. We'll still be thinking of you on our special day")
            return Response(str(resp), status=200, mimetype="application/xml")

        if body[:4] == "rsvp":
            # we have an rsvp
            split_body = body.split()
            total_attendees = guest.total_attendees
            if split_body[1].lower()[:3] == "yes":
                # We gave an rsvp!
                response = "We're so glad you're joining us on our special day! " \
                           "Remember to keep up with the wedding site for any updates!"
                rsvp = True
                try:
                    responded_attendees = int(split_body[2])
                except ValueError:
                    resp.message(rsvp_help_msg)
                    return Response(str(resp), status=200, mimetype="application/xml")
                # check that they're not trying to bring the whole town with them
                if responded_attendees > total_attendees:
                    response = "I'm sorry, but we have to keep our wedding small. We ask that you only bring up to " \
                               "{} people. If you need extra, please reach out to Andrew and Sarah and we can work " \
                               "with you".format(total_attendees)
                    resp.message(response)
                    return Response(str(resp), status=200, mimetype="application/xml")
                total_attendees = responded_attendees
                note = " ".join(split_body[3:])
            elif split_body[1].lower()[:3] == "no":
                response = "Thank you for responding. We understand life can be busy. We'll be thinking of you on " \
                           "our special day."
                rsvp = False
                total_attendees = 0
                note = body
            else:
                resp.message(rsvp_help_msg)
                return Response(str(resp), status=200, mimetype="application/xml")
            resp.message(response)
            guest.total_attendees = total_attendees
            guest.rsvp = rsvp
            if guest.rsvp_notes is None:
                guest.rsvp_notes = note
            else:
                guest.rsvp_notes += "\n" + note
            guest.save()
            return Response(str(resp), status=200, mimetype="application/xml")

        if body[:4] == "stop":
            # they dont want texts
            resp.message("We're so sorry! We won't text you again about our wedding plans.")
            guest.stop_notifications = True
            guest.rsvp_notes = body
            guest.save()
            return Response(str(resp), status=200, mimetype="application/xml")

