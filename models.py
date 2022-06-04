from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
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
    image_link = db.Column(db.String)
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String)
    seeking_talent = db.Column(db.Boolean, default=False)
    shows = db.relationship('Show', backref='venues',
                            lazy=False, cascade='all, delete-orphan')
    genres = db.Column(ARRAY(String()))
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

    def __repr__(self):
        return f'<Venue ID: {self.id}, name: {self.name}>'

    def upcoming_shows(self):
        upcoming_shows = [
            show for show in self.shows if show.start_time > datetime.now()]
        return upcoming_shows

    def num_upcoming_shows(self):
        return len(self.upcoming_shows())

    def past_shows(self):
        past_shows = [
            show for show in self.shows if show.start_time < datetime.now()]
        return past_shows

    def num_past_shows(self):
        return len(self.past_shows())

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String)
    genres = db.Column(ARRAY(String()))
    image_link = db.Column(db.String)
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artists',
                            lazy=True, cascade='all, delete-orphan')
    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, city, state, phone, image_link, facebook_link, website, seeking_venue, genres, seeking_description):
        self.name = name
        self.city = city
        self.state = state
        self.phone = phone
        self.image_link = image_link
        self.facebook_link = facebook_link
        self.website = website
        self.seeking_venue = seeking_venue
        self.seeking_description = seeking_description
        self.genres = genres

    def __repr__(self):
        return f'<ARTIST ID: {self.id}, name: {self.name}>'

    def upcoming_shows(self):
        upcoming_shows = [
            show for show in self.shows if show.start_time > datetime.now()]
        return upcoming_shows

    def num_upcoming_shows(self):
        return len(self.upcoming_shows())

    def past_shows(self):
        past_shows = [
            show for show in self.shows if show.start_time < datetime.now()]
        return past_shows

    def num_past_shows(self):
        return len(self.past_shows())

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
    venue = db.relationship(
        'Venue', backref=db.backref('showss', cascade='all, delete'))

    def __repr__(self):
        return f'<Show ID: {self.id}, venue_id: {self.venue_id}, artist_id: {self.artist_id}>'
