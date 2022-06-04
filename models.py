from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default=False)
    shows = db.relationship('Show', backref='venues', lazy=False)
    genres = db.Column(db.PickleType, default=[])
    seeking_description = db.Column(db.Text)

    def __init__(self, name, city, state, address, phone, image_link, facebook_link, website, seeking_talent, genres, seeking_description):
        self.name = name
        self.city = city
        self. address = address
        self.state = state
        self.phone = phone
        self.image_link = image_link
        self.facebook_link = facebook_link
        self.website = website
        self.seeking_talent = seeking_talent
        self.seeking_description = seeking_description
        self.genres = genres

    # @property
    # def upcoming_shows(self):
    #     upcoming_shows = [
    #         show for show in self.shows if show.start_time > datetime.now()]
    #     return upcoming_shows

    # @property
    # def num_upcoming_shows(self):
    #     return len(self.upcoming_shows)

    # @property
    # def past_shows(self):
    #     past_shows = [
    #         show for show in self.shows if show.start_time < datetime.now()]
    #     return past_shows

    # @property
    # def num_past_shows(self):
    #     return len(self.past_shows)

    # @property
    # def serialize_with_upcoming_shows_count(self):
    #      return {'id': self.id,
    #             'name': self.name,
    #             'city': self.city,
    #             'state': self.state,
    #             'phone': self.phone,
    #             'address': self.address,
    #             'image_link': self.image_link,
    #             'facebook_link': self.facebook_link,
    #             'seeking_talent': self.seeking_talent,
    #             'seeking_description': self.seeking_description,
    #             'website': self.website,
    #             'num_shows': Show.query.filter(Show.start)

    @property
    def serialize_with_shows_details(self):
        return {'id': self.id,
                'name': self.name,
                'city': self.city,
                'state': self.state,
                'phone': self.phone,
                'address': self.address,
                'image_link': self.image_link,
                'facebook_link': self.facebook_link,
                'seeking_talent': self.seeking_talent,
                'seeking_description': self.seeking_description,
                'website': self.website,
                'upcoming_shows': [show for show in self.shows if show.start_time > datetime.now()(

                    Show.venue_id == self.id).all()],
                'past_shows': [show for show in self.shows if show.start_time < datetime.now()(

                    Show.venue_id == self.id).all()],
                'upcoming_shows_count': len(Show.query.filter(
                    Show.start_time > datetime.datetime.now(),
                    Show.venue_id == self.id).all()),
                'past_shows_count': len(Show.query.filter(
                    Show.start_time < datetime.datetime.now(),
                    Show.venue_id == self.id).all())
                }

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artists', lazy=True)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def upcoming_shows(self):
        upcoming_shows = [
            show for show in self.shows if show.start_time > datetime.now()]
        return upcoming_shows

    @property
    def num_upcoming_shows(self):
        return len(self.upcoming_shows)

    @property
    def past_shows(self):
        past_shows = [
            show for show in self.shows if show.start_time < datetime.now()]
        return past_shows

    @property
    def num_past_shows(self):
        return len(self.past_shows)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venues.id'), nullable=False)
