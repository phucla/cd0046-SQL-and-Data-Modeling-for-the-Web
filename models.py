from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime



def connect_db(app):
  app.config.from_object('config')
  db = SQLAlchemy()
  db.app = app

  db.init_app(app)
  return db
