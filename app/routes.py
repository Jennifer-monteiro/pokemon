from app import app,db
import requests
from flask import redirect, render_template, request, url_for, flash
from .forms import PokeForm
from .forms import SignUpForm
from .models import User, PokemonCapture
from .forms import LoginForm, ProfileForm
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime
import random

@app.route("/")
def index_html():
    return render_template('index.html', title='Home Page')

@app.route('/pokedex', methods=['GET', 'POST'])
def get_pokemon_info():
    form = PokeForm()
    error_message = None
    
    if request.method == 'POST' and form.validate_on_submit():  # Validate the form on submit
        poke_name = form.pokemon.data.lower()
        response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{poke_name}')
        
        if response.status_code == 200:
            data = response.json()
            try:
                poke_info = {
                    'name': data['forms'][0]['name'],
                    'ability1_name': data['abilities'][0]['ability']['name'],
                    'ability2_name': data['abilities'][1]['ability']['name'],
                    'base_experience': data['base_experience'],
                    'sprite_frontdefault': data['sprites']['other']['official-artwork']['front_default'],
                    'attack_stat': data['stats'][1]['base_stat'],
                    'hp_stat': data['stats'][0]['base_stat'],
                    'defense_stat': data['stats'][2]['base_stat']
                }
            except (IndexError, KeyError):
                error_message = "The Pokémon number doesn't exist. Try a lower number"
                return render_template('Pokedex.html', form=form, error_message=error_message)
            
            return render_template('Pokedex.html', poke_info=poke_info, form=form, error_message=error_message)
        else:
            error_message = "The Pokémon you entered was not found. Please check the name or number and try again."
    
    return render_template('Pokedex.html', form=form, error_message=error_message)



@app.route("/signup", methods=['GET', 'POST'])
def signup_page():
    form = SignUpForm()
    if request.method == 'POST':
        if form.validate():
            fullname = form.fullname.data
            username = form.username.data
            email = form.email.data
            password = form.password.data

            # Check if the email already exists in the database
            existing_email_user = User.query.filter_by(email=email).first()
            existing_username_user = User.query.filter_by(username=username).first()

            if existing_email_user:
                flash("Email already exists. Please choose another one.", "error")
            elif existing_username_user:
                flash("Username already exists. Please choose another one.", "error")
            else:
                user = User(
                    fullname=fullname,
                    username=username,
                    email=email,
                    password=password
                )

                db.session.add(user)
                db.session.commit()
                flash("Sign up successful!", "success")
                return redirect(url_for("login_page"))
        else:
            flash("Form is invalid. Please check the fields.", "error")

    return render_template('signup.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    error_message = None  # Initialize error message

    if request.method == 'POST':
        if form.validate():
            username = form.username.data
            password = form.password.data

            user = User.query.filter_by(username=username).first()
            if user:
                if user.password == password:
                    login_user(user)
                    return redirect(url_for('user_page'))
                else:
                    error_message = 'Incorrect password'
            else:
                error_message = 'User does not exist'
        else:
            error_message = 'Invalid form data'

    return render_template('login.html', title='Login', form=form, error_message=error_message)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login_page'))

@app.route('/profile')
def profile():
    form = ProfileForm()
    return render_template('profile.html', title='Profile Page', form=ProfileForm())


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required  # Make sure the user is logged in to access this page
def edit_profile():
    return render_template('profile.html')

@app.route('/update_username', methods=['POST'])
@login_required
def update_username():
    new_username = request.form.get('new_username')
    if new_username:
        current_user.username = new_username
        db.session.commit()
        flash('Username updated successfully', 'success')
    else:
        flash('Please provide a valid username', 'danger')
    return redirect(url_for('profile'))

@app.route('/update_email', methods=['POST'])
@login_required
def update_email():
    new_email = request.form.get('new_email')
    if new_email:
        current_user.email = new_email
        db.session.commit()
        flash('Email updated successfully', 'success')
    else:
        flash('Please provide a valid email address', 'danger')
    return redirect(url_for('profile'))

@app.route('/catch_pokemon', methods=['GET', 'POST'])
def catch_pokemon():
    action = request.form.get('action')
    pokemon_info = None
    max_pokemon_reached = False  # Initialize max_pokemon_reached to False
    
    if action == 'catch':
        if current_user.is_authenticated:
            # Check if the user has already caught 5 Pokémon
            if PokemonCapture.query.filter_by(user_id=current_user.id).count() >= 5:
                max_pokemon_reached = True  # Set max_pokemon_reached to True
                flash("Your Pokédex is full! You cannot catch more Pokémon.", 'error')
            else:
                random_pokemon_id = random.randint(1, 1000)  # Adjust the range based on your preference
                response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{random_pokemon_id}')
                
                if response.status_code == 200:
                    data = response.json()
                    pokemon_name = data['forms'][0]['name']  # Get the name of the captured Pokémon
                    # Create a new PokemonCapture instance for the user
                    new_pokemon_capture = PokemonCapture(
                        pokemon_name=pokemon_name,
                        user_id=current_user.id
                    )
                    db.session.add(new_pokemon_capture)
                    db.session.commit()
                    flash(f"You caught a {pokemon_name}!", 'success')  # Set a success flash message
                    pokemon_info = {
                        'name': pokemon_name,
                        'sprite_frontdefault': data['sprites']['other']['official-artwork']['front_default']
                    }
                else:
                    flash("Failed to catch a Pokémon. Try again.", 'error')
        else:
            flash("You must be logged in to catch Pokémon.", 'error')
    
    # Generate a random Pokémon if it's not a "Catch" action or after a successful capture
    if action == 'skip' or pokemon_info is None:
        random_pokemon_id = random.randint(1, 1000)  # Adjust the range based on your preference
        response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{random_pokemon_id}')
        if response.status_code == 200:
            data = response.json()
            pokemon_info = {
                'name': data['forms'][0]['name'],
                'sprite_frontdefault': data['sprites']['other']['official-artwork']['front_default']
            }
    
    return render_template('catch_pokemon.html', pokemon_info=pokemon_info, max_pokemon_reached=max_pokemon_reached)







@app.route('/user_page', methods=['GET', 'POST'])
@login_required
def user_page():
    captured_pokemon = PokemonCapture.query.filter_by(user_id=current_user.id).all()

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'delete':
            pokemon_name_to_delete = request.form.get('pokemon_name')
            if current_user.delete_captured_pokemon(pokemon_name_to_delete):
                flash(f"Deleted {pokemon_name_to_delete} from your collection.", 'success')
            else:
                flash(f"{pokemon_name_to_delete} not found in your collection.", 'danger')
            return redirect(url_for('user_page'))

    return render_template('user_page.html', captured_pokemon=captured_pokemon)



@app.route('/battle', methods=['GET'])
@login_required
def battle():
    # Get all users except the current user
    users = User.query.filter(User.id != current_user.id).all()
    return render_template('battle.html', users=users)