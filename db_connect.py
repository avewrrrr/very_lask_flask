from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def connect_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = ( 'postgresql://postgres:admin@localhost:4444/oris_very_last_projectFLASK' )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
