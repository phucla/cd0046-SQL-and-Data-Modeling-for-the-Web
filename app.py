#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    url_for
)
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from forms import *
from sqlalchemy.exc import SQLAlchemyError
from collections import OrderedDict
from models import connect_db,Venue, Artist, Show
from utils import format_datetime
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
db = connect_db(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.all()
  order = OrderedDict()
  for venue in venues:
    order.setdefault((venue.city, venue.state), list()).append({
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': venue.num_upcoming_shows()
    })
  data = [{'city': k[0], 'state': k[1], 'venues': venues} for k, venues in order.items()]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  query = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike(f'%{query}%')).all()
  response = {
    "count": len(venues),
    "data": [{
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': venue.num_upcoming_shows(),
    } for venue in venues]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = Venue.query.get_or_404(venue_id)
  data.genres = json.loads(data.genres) if data.genres else []
  data.get_shows()
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(meta={'csrf': False})
  if not form.validate():
    message = []
    for field, errors in form.errors.items():
      for error in errors:
        message.append(f"{field}: {error}")
    flash('Errors: ' + ', '.join(message))
    return render_template('forms/new_venue.html', form=form)

  try:
    venue = Venue(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      address=form.address.data,
      phone=form.phone.data,
      genres=json.dumps(form.genres.data),
      image_link=form.image_link.data,
      facebook_link=form.facebook_link.data,
      website_link=form.website_link.data,
      seeking_talent=form.seeking_talent.data,
      seeking_description=form.seeking_description.data
    )

    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + venue.name + ' was successfully created!')
  except SQLAlchemyError:
    print(sys.exc_info())
    db.session.rollback()
    flash(
      'Error: ' +
      form.name.data +
      ' could not be insert.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

# @app.route('/venues/<venue_id>', methods=['DELETE'])
# def delete_venue(venue_id):
#   # TODO: Complete this endpoint for taking a venue_id, and using
#   # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

#   # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
#   # clicking that button delete it from the db then redirect the user to the homepage
#   return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.with_entities(Artist.id, Artist.name).all()
  data=[{'id': artist.id, 'name': artist.name} for artist in artists]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  query = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{query}%')).all()
  response = {
    "count": len(artists),
    "data": [{
      'id': artist.id,
      'name': artist.name,
      'num_upcoming_shows': artist.num_upcoming_shows(),
    } for artist in artists]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  data = Artist.query.get_or_404(artist_id)
  data.genres = json.loads(data.genres) if data.genres else []
  data.query_shows()
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get_or_404(artist_id)
  artist.genres = json.loads(artist.genres) if artist.genres else []
    # form = ArtistForm(obj=artist)
  # TODO: populate form with fields from artist with ID <artist_id>

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get_or_404(artist_id)
  form = ArtistForm(meta={'csrf': False})

  if not form.validate():
    message = []
    for field, errors in form.errors.items():
      for error in errors:
        message.append(f"{field}: {error}")
    flash('Errors: ' + ', '.join(message))
    return render_template(
      'forms/edit_artist.html',
      form=form,
      artist=artist)

  try:
    form.populate_obj(artist)
    artist.genres = json.dumps(form.genres.data)
    db.session.commit()
    flash('Artist ' + artist.name + ' was successfully updated!')
  except SQLAlchemyError:
    print(sys.exc_info())
    db.session.rollback()
    flash(
      'Artist ' +
      artist.name +
      ' could not updated.')
    return render_template(
      'forms/edit_artist.html',
      form=form,
      artist=artist)
  finally:
      db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get_or_404(venue_id)
  venue.genres = json.loads(venue.genres) if venue.genres else []
  form = VenueForm(obj=venue)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get_or_404(venue_id)
  form = VenueForm(meta={'csrf': False})

  if not form.validate():
    message = []
    for field, errors in form.errors.items():
      for error in errors:
        message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))
    return render_template('forms/edit_venue.html', form=form, venue=venue)

  try:
    form.populate_obj(venue)
    venue.genres = json.dumps(form.genres.data)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully updated!')
  except SQLAlchemyError:
    print(sys.exc_info())
    db.session.rollback()
    flash('An error occurred. Venue ' + venue.name + ' could not updated.')
    return render_template('forms/edit_venue.html', form=form, venue=venue)
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  form = ArtistForm(meta={'csrf': False})
    # DONE: insert form data as a new Venue record in the db, instead
    # DONE: modify data to be the data object returned from db insertion
  if not form.validate():
    message = []
    for field, errors in form.errors.items():
      for error in errors:
        message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))
    return render_template('forms/new_artist.html', form=form)

  try:
    artist = Artist(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      phone=form.phone.data,
      genres=json.dumps(form.genres.data),
      image_link=form.image_link.data,
      facebook_link=form.facebook_link.data,
      website_link=form.website_link.data,
      seeking_venue=form.seeking_venue.data,
      seeking_description=form.seeking_description.data
    )

    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + artist.name + ' was successfully created!')
  except SQLAlchemyError:
    print(sys.exc_info())
    db.session.rollback()
    flash(
      'An error occurred. Artist ' +
      form.name.data +
      ' could not be listed.')
    return render_template('forms/new_artist.html', form=form)
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = db.session.query(Show, Venue, Artist).join(Venue).join(Artist)
  data = [{
    "venue_id": venue.id,
    "venue_name": venue.name,
    "artist_id": artist.id,
    "artist_name": artist.name,
    "artist_image_link": artist.image_link,
    "start_time": str(show.start_time)
  } for show, venue, artist in shows]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  form = ShowForm(meta={'csrf': False})

  if not form.validate():
    message = []
    for field, errors in form.errors.items():
      for error in errors:
        message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))
    return render_template('forms/new_show.html', form=form)

  try:
    show = Show(
      artist_id=form.artist_id.data,
      venue_id=form.venue_id.data,
      start_time=form.start_time.data
    )

    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except SQLAlchemyError:
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
    db.session.rollback()
    return render_template('forms/new_show.html', form=form)
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
  return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
  return render_template('errors/500.html'), 500


if not app.debug:
  file_handler = FileHandler('error.log')
  file_handler.setFormatter(
      Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
