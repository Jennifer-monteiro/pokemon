from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

teams = db.Table(
    'teams',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False),
    db.Column('pokemon_id', db.Integer, db.ForeignKey('pokemoncapture.id'), nullable=False)
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String, nullable=False)
    username = db.Column(db.String(45), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    
    # Define the relationship with PokemonCapture, using the back_populates attribute
    captured_pokemon = db.relationship('PokemonCapture', back_populates='user', secondary=teams)

    def __init__(self, fullname, username, email, password):
        self.fullname = fullname
        self.username = username
        self.email = email
        self.password = password
    
    def delete_captured_pokemon(self, pokemon_name):
        captured_pokemon = PokemonCapture.query.filter_by(
            user_id=self.id, pokemon_name=pokemon_name).first()
        if captured_pokemon:
            db.session.delete(captured_pokemon)
            db.session.commit()
            return True
        return False


class PokemonCapture(db.Model):
    __tablename__ = 'pokemoncapture'
    id = db.Column(db.Integer, primary_key=True)
    pokemon_name = db.Column(db.String(255), nullable=False)
    date_captured = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Define the relationship with User, using the back_populates attribute
    user = db.relationship('User', back_populates='captured_pokemon', secondary=teams)

    def __init__(self, pokemon_name, user_id):
        self.pokemon_name = pokemon_name
        self.user_id = user_id

    def __repr__(self):
        return f"PokemonCapture, pokemon_name={self.pokemon_name}, date_captured={self.date_captured})"

class BattleResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    winner_id = db.Column(db.Integer, nullable=False)
    loser_id = db.Column(db.Integer, nullable=False)
