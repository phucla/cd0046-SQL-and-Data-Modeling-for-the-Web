from flask_sqlalchemy import SQLAlchemy

def connect_db(app):
  app.config.from_object('config')
  db = SQLAlchemy()
  db.app = app

  db.init_app(app)
  return db
