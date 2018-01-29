from datetime import date
from datetime import datetime

from app import db
from flask.json import JSONEncoder as BaseJSONEncoder


class JSONEncoder(BaseJSONEncoder):
    """
    Custom :class:`JSONEncoder` which respects objects that include the
    :class:`JsonSerializer` mixin.
    """
    def default(self, obj):
        """
        the default json encoder
        Args:
            obj (any): obj we check is a json serializer
        Returns:
            flask.json.JSONEncoder
        """
        if isinstance(obj, ModelJsonSerializer):
            return obj.to_json()
        return super(JSONEncoder, self).default(obj)


class ModelJsonSerializer(object):
    """
    A mixin that can be used to mark a SQLAlchemy model class which implements
    a :func:`to_json` method.
    The :func:`to_json` method is used in conjuction with the custom
    :class:`JSONEncoder` class.
    By default this mixin will assume all properties of the SQLAlchemy model are
    to be visible in the JSON output.
    Extend this class to customize which properties are hidden by setting
    __json_hidden__ to a list of keys
    """

    __json_hidden__ = None

    def get_field_names(self):
        """
        Generator that yields all field names of a SQLAlchemy model class
        Yields:
            str) - Field name of the SqlAlchemy model class
        """
        for p in self.__mapper__.iterate_properties:
            yield p.key

    def to_json(self):
        """
        Returns a python dict that represents a SQLAlchemy model class, hiding
        any hidden fields
        Returns:
            dict - represents a SQLAlchemy model class
        """
        hidden = self.__json_hidden__ or []

        rv = dict()
        for key in self.get_field_names():
            rv[key] = getattr(self, key)
            if isinstance(rv[key], (datetime, date)):
                rv[key] = rv[key].isoformat()
        for key in hidden:
            rv.pop(key, None)
        return rv


class Guest(ModelJsonSerializer, db.Model):
    """
    This class represents our Guest table
    """

    __tablename__ = "guests"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    total_attendees = db.Column(db.Integer, default=1)
    phone_number = db.Column(db.String(255))
    email_address = db.Column(db.String(255))
    physical_address = db.Column(db.String(255))
    date_saved = db.Column(db.Boolean, default=None)
    rsvp = db.Column(db.Boolean, default=None)
    rsvp_notes = db.Column(db.Text, default=None)
    stop_notifications = db.Column(db.Boolean, default=False)
    last_notified = db.Column(db.DateTime, default=None)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    SCHEMA = {
        'name': {'type': 'string'},
        'total_attendees': {'type': 'integer'},
        'phone_number': {'type': 'string'},
        'email_address': {'type': 'string'},
        'physcial_address': {'type': 'string'}
    }
    PUT_SCHEMA = {
        'name': {'type': 'string', 'required': False},
        'total_attendees': {'type': 'integer', 'required': False},
        'phone_number': {'type': 'string', 'required': False},
        'email_address': {'type': 'string', 'required': False},
        'physcial_address': {'type': 'string', 'required': False},
        'date_saved': {'type': 'boolean', 'required': False},
        'rsvp': {'type': 'boolean', 'required': False},
        'rsvp_notes':  {'type': 'string', 'required': False},
        'stop_notification': {'type': 'boolean', 'required': False}
    }

    def __init__(self, name: str,
                 total_attendees: int = 1,
                 phone_number: str = "",
                 email_address: str = "",
                 physical_address: str = ""):
        """
        Initializes our Guest
        Args:
            name (str): Name of guest group, i.e. John and Jane Doe
            total_attendees (int): Number of attendees in the group, i.e. for John and Jane - 2
            phone_number (str): Phone number of the attendee
            email_address (str): Email address of the attendee
            physical_address (str): Mails address of the attendee
        """
        self.name = name
        self.total_attendees = total_attendees
        self.phone_number = phone_number
        self.email_address = email_address
        self.physical_address = physical_address

    def save(self):
        """
        Saves any changes to the object

        """
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        """
        Returns all guests

        """
        return Guest.query.all()

    def delete(self):
        """
        Deletes this guest

        """
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        """
        Returns a string representation of our guest
        Returns:
            str
        """
        return "<Guest: id {} name {}>".format(self.id, self.name)
