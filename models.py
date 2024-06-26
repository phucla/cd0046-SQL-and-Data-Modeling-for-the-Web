from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# connect database
#----------------------------------------------------------------------------#
def connect_db(app):
  app.config.from_object('config')
  db.app = app
  db.init_app(app)
  return db


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
  __tablename__ = 'Venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  website_link = db.Column(db.String(120))
  seeking_talent = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String(500))
  created_date = db.Column(db.DateTime)
  genres = db.Column(db.String(500))
  shows = db.relationship(
    'Show',
    backref='Venue',
    lazy='joined',
    cascade='all, delete')
  def num_upcoming_shows(self):
    return db.session.query(Show) .filter(
      Show.venue_id == self.id,
      Show.start_time > datetime.now()) .count()
  def get_shows(self):
    now = datetime.now()
    upcoming_shows = db.session.query(Show, Artist).join(Artist)\
      .filter(Show.venue_id == self.id, Show.start_time > now)\
      .all()
    past_shows = db.session.query(Show, Artist).join(Artist)\
      .filter(Show.venue_id == self.id, Show.start_time <= now)\
      .all()
    self.upcoming_shows = [{
      'start_time': str(show.start_time),
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
    } for show, artist in upcoming_shows]
    self.past_shows = [{
      'start_time': str(show.start_time),
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
    } for show, artist in past_shows]
    self.upcoming_shows_count = db.session.query(Show)\
      .filter(Show.venue_id == self.id, Show.start_time > now)\
      .count()
    self.past_shows_count = db.session.query(Show)\
      .filter(Show.venue_id == self.id, Show.start_time <= now)\
      .count()

class Artist(db.Model):
  __tablename__ = 'Artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website_link = db.Column(db.String(120))
  seeking_venue = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String(500))
  created_date = db.Column(db.DateTime)
  shows = db.relationship(
    'Show',
    backref='Artist',
    lazy='joined',
    cascade='all, delete')
  def num_upcoming_shows(self):
    return db.session.query(Show) .filter(
      Show.venue_id == self.id,
      Show.start_time > datetime.now()) .count()
  
  def query_shows(self):
    now = datetime.now()
    upcoming_shows = db.session.query(Show, Venue).join(Venue)\
      .filter(Show.artist_id == self.id, Show.start_time > now)\
      .all()
    past_shows = db.session.query(Show, Venue).join(Venue)\
      .filter(Show.artist_id == self.id, Show.start_time <= now)\
      .all()
    self.upcoming_shows = [{
      'start_time': str(show.start_time),
      'venue_id': venue.id,
      'venue_name': venue.name,
      'venue_image_link': venue.image_link,
    } for show, venue in upcoming_shows]
    self.past_shows = [{
      'start_time': str(show.start_time),
      'venue_id': venue.id,
      'venue_name': venue.name,
      'venue_image_link': venue.image_link,
    } for show, venue in past_shows]
    self.upcoming_shows_count = db.session.query(Show)\
      .filter(Show.artist_id == self.id, Show.start_time > now)\
      .count()
    self.past_shows_count = db.session.query(Show)\
      .filter(Show.artist_id == self.id, Show.start_time <= now)\
      .count()
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(
    db.Integer,
    db.ForeignKey('Artist.id'),
    nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)