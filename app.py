#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#


import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import ArtistForm, VenueForm, ShowForm
from flask_migrate import Migrate
from models import db, Artist, Venue, Show
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
# db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


# def format_datetime(value, format='medium'):
#     date = dateutil.parser.parse(value)
#     if format == 'full':
#         format = "EEEE MMMM, d, y 'at' h:mma"
#     elif format == 'medium':
#         format = "EE MM, dd, y h:mma"
#     return babel.dates.format_datetime(date, format, locale='en')
def format_datetime(value, format='medium'):
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
        if format == 'full':
            format = "EEEE MMMM, d, y 'at' h:mma"
        elif format == 'medium':
            format = "EE MM, dd, y h:mma"
        return babel.dates.format_datetime(date, format, locale='en')
    else:
        date = value


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = []

    regions = Venue.query.with_entities(
        Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()

    # Looping over each location
    for region in regions:
        city = region.city
        state = region.state

        venues = Venue.query.filter_by(state=state, city=city).all()

        venues_data = []

        for venue in venues:
            venues_data.append({
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': venue.num_upcoming_shows
            })

        data.append({"city": city, "state": state, "venues": venues_data
                     })
    return render_template('pages/venues.html', areas=data)
    # TODO: replace with real venues data.


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')

    venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%'))

    data = []
    for venue in venues:
        data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": venue.num_upcoming_shows
        })

    counts = len(data)
    response = {
        "count": counts,
        "data": data
    }

    return render_template('pages/search_venues.html', results=response, search_term=search_term)
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    venue = Venue.query.get(venue_id)

    if not venue:
        flash("Venue with ID " + str(venue_id) +
              " was not found!", 'danger')
        return redirect(url_for('venues'))

    past_shows = []
    for show in venue.past_shows():
        artist = Artist.query.get(show.artist_id)
        past_shows.append({
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.start_time)
        })

    upcoming_shows = []
    for show in venue.upcoming_shows():
        artist = Artist.query.get(show.artist_id)
        upcoming_shows.append({
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.start_time)
        })

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": True if venue.seeking_talent in (True, 't', 'True', 'y') else False,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link if venue.image_link else "",
        "past_shows_count": venue.num_past_shows(),
        "upcoming_shows_count": venue.num_upcoming_shows(),
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    status = False
    try:
        form = VenueForm(request.form)

        name = form.name.data
        city = form.city.data
        state = form.state.data
        address = form.address.data
        phone = form.phone.data
        image_link = form.image_link.data
        genres = request.form.getlist('genres')
        facebook_link = form.facebook_link.data
        website = form.website_link.data
        seeking_talent = True if 'seeking_talent' in request.form else False
        seeking_description = form.seeking_description.data

        venue = Venue(name=name, city=city, state=state,  address=address, phone=phone, image_link=image_link, facebook_link=facebook_link,
                      genres=genres, website=website, seeking_talent=seeking_talent, seeking_description=seeking_description)

        db.session.add(venue)
        db.session.commit()
        status = True
    except Exception:
        db.session.rollback()
        status = False
        print(sys.exc_info())
    finally:
        db.session.close()

    if not status:
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.', 'danger')
    else:
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] +
              ' was successfully listed!', 'success')

    return redirect(url_for('index'))


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    status = False
    try:
        # remove the associated shows
        Show.query.filter_by(venue_id=venue_id).delete()

        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
        status = True
    except:
        db.session.rollback()
        status = False
        print(sys.exc_info())
    finally:
        db.session.close()

    return jsonify({'success': status})
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = Artist.query.with_entities(Artist.id, Artist.name).all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')

    artists = Artist.query.filter(Artist.name.ilike('%' + search_term + '%'))

    data = []
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": artist.num_upcoming_shows
        })

    counts = len(data)
    results = {
        "count": counts,
        "data": data
    }

    return render_template('pages/search_artists.html', results=results, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    artist = Artist.query.filter(Artist.id == artist_id).first()
    if not artist:
        flash("Artist with ID " + str(artist_id) +
              " was not found!", 'danger')
        return redirect(url_for('artists'))

    past_shows = []
    for show in artist.past_shows():
        venue = Venue.query.get(show.venue_id)
        past_shows.append({
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": str(show.start_time)
        })

    upcoming_shows = []
    for show in artist.upcoming_shows():
        venue = Venue.query.get(show.venue_id)
        upcoming_shows.append({
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": str(show.start_time)
        })

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "seeking_venue": True if artist.seeking_venue in ('y', True, 't', 'True') else False,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "facebook_link": artist.facebook_link,
        "website": artist.website,
        "past_shows_count": artist.num_past_shows(),
        "upcoming_shows_count": artist.num_upcoming_shows(),
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,

    }

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    artist = Artist.query.get(artist_id)
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.image_link.data = artist.image_link
    form.facebook_link.data = artist.facebook_link
    form.website_link.data = artist.website
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    status = False
    artist = Artist.query.get(artist_id)

    if not artist:
        flash('An error occurred. Artist with ID ' +
              str(artist_id) + ' was not found!', 'danger')
        return redirect(url_for('artists'))

    try:
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.genres = request.form.getlist('genres')
        artist.image_link = request.form['image_link']
        artist.facebook_link = request.form['facebook_link']
        artist.website = request.form['website_link']
        artist.seeking_venue = True if 'seeking_venue' in request.form else False
        artist.seeking_description = request.form['seeking_description']

        db.session.commit()
        status = True
    except:
        db.session.rollback()
        status = False
        print(sys.exc_info())
    finally:
        db.session.close()

    if not status:
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be edited.', 'danger')
        return redirect(url_for('edit_artist_submission', artist_id=artist_id))
    else:
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] +
              ' was successfully edited!', 'success')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.filter(Venue.id == venue_id).first()
    form = VenueForm()

    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.image_link.data = venue.image_link
    form.facebook_link.data = venue.facebook_link
    form.website_link.data = venue.website
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

    return render_template('forms/edit_venue.html', form=form, venue=venue)

    # TODO: populate form with values from venue with ID <venue_id>


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    status = False
    venue = Venue.query.get(venue_id)

    if not venue:
        flash('An error occurred. Venue with ID ' +
              str(venue_id) + ' was not found!', 'danger')
        return redirect(url_for('venues'))

    try:
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.genres = request.form.getlist('genres')
        venue.image_link = request.form['image_link']
        venue.facebook_link = request.form['facebook_link']
        venue.website = request.form['website_link']
        venue.seeking_talent = True if 'seeking_talent' in request.form else False
        venue.seeking_description = request.form['seeking_description']

        db.session.commit()
        status = True
    except:
        db.session.rollback()
        status = False
        print(sys.exc_info())
    finally:
        db.session.close()

    if not status:
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be edited.', 'danger')
        return redirect(url_for('edit_venue_submission', venue_id=venue_id))
    else:
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] +
              ' was successfully edited!', 'success')

    return redirect(url_for('show_venue', venue_id=venue_id))

    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes


#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form)
    status = False
    try:
        new_artist = Artist(
            name=form.name.data,
            genres=request.form.getlist('genres'),
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            facebook_link=form.facebook_link.data,
            website=form.website_link.data,
            seeking_venue=True if 'seeking_venue' in request.form else False,
            image_link=form.image_link.data,
            seeking_description=form.seeking_description.data)

        db.session.add(new_artist)
        db.session.commit()
        status = True
    except Exception:
        db.session.rollback()
        status = False
        print(sys.exc_info())
    finally:
        db.session.close()

    if not status:
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.', 'danger')
    else:
        flash('Artist ' + request.form['name'] +
              ' was successfully listed!', 'success')
    return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
    data = db.session.query(Show).join(Venue, (Venue.id == Show.venue_id)).join(Artist, (Artist.id == Show.artist_id)).with_entities(Show.venue_id, Venue.name.label(
        'venue_name'), Show.artist_id, Artist.name.label('artist_name'), Artist.image_link.label('artist_image_link'), Show.start_time).all()

    def format_data(d):
        d = dict(zip(d.keys(), d))
        d['start_time'] = str(d['start_time'])
        return d

    data = [format_data(d) for d in data]

    return render_template('pages/shows.html', shows=data)
    # displays list of shows at /shows
    # TODO: replace with real venues data.


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    venue_id = request.form.get('venue_id')
    artist_id = request.form.get('artist_id')
    start_time = request.form.get('start_time')
    status = False

    venue = Venue.query.get(venue_id)
    artist = Artist.query.get(artist_id)

    if not venue:
        flash('An error occurred. Show could not be listed. Venue ID ' +
              str(venue_id)+' is invalid!', 'danger')
        return redirect(url_for('index'))

    if not artist:
        flash('An error occurred. Show could not be listed. Artist ID ' +
              str(artist_id)+' is invalid!', 'danger')
        return redirect(url_for('index'))

    try:
        show = Show(venue_id=venue_id, artist_id=artist_id,
                    start_time=start_time)

        db.session.add(show)
        db.session.commit()
        status = True
    except:
        db.session.rollback()
        status = False
        print(sys.exc_info())
    finally:
        db.session.close()

        # on unsuccessful db insert, flash an error instead.
    if not status:
        flash('An error occurred. Show could not be listed.', 'danger')
    else:
        # on successful db insert, flash success
        flash('Show was successfully listed!', 'success')

    return redirect(url_for('index'))
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    # # on successful db insert, flash success
    # flash('Show was successfully listed!')
    # # TODO: on unsuccessful db insert, flash an error instead.
    # # e.g., flash('An error occurred. Show could not be listed.')
    # # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    # return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
