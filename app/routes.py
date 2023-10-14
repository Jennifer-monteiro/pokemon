from app import app,db
import requests
from flask import redirect, render_template, request, url_for, flash, session
from .forms import PokeForm
from .forms import SignUpForm
from .models import User, PokemonCapture, BattleResult
from .forms import LoginForm, ProfileForm
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime
import random
from .battle_logic import fetch_pokemon_data, calculate_pokemon_score, perform_battle


@app.route("/")
def index_html():
    return render_template('index.html', title='Home Page')

@app.route('/pokedex', methods=['GET', 'POST'])
def get_pokemon_info():
    form = PokeForm()
    error_message = None
    
    if request.method == 'POST':
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
    max_pokemon_reached = False

    if 'current_pokemon' not in session or action == 'skip':
        # Generate a new Pokémon for the display if none is in the session or if 'Skip' is clicked
        random_pokemon_id = random.randint(1, 1016)
        response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{random_pokemon_id}')

        if response.status_code == 200:
            data = response.json()
            pokemon_info = {
                'name': data['forms'][0]['name'],
                'sprite_frontdefault': data['sprites']['other']['official-artwork']['front_default']
            }

            # Check if the user has already caught the current Pokémon
            if current_user.is_authenticated:
                user_id = current_user.id
                if not PokemonCapture.query.filter_by(user_id=user_id, pokemon_name=pokemon_info['name']).first():
                    # Store the current Pokémon in the session
                    session['current_pokemon'] = pokemon_info
                else:
                    flash(f"You've already caught {pokemon_info['name']}! Try again.", 'error')
                    pokemon_info = None
            else:
                flash("You must be logged in to catch Pokémon.", 'error')
        else:
            flash("Failed to fetch a Pokémon. Try again later.", 'error')
            pokemon_info = None
    else:
        # Use the current Pokémon stored in the session
        pokemon_info = session['current_pokemon']

    if action == 'catch':
        if current_user.is_authenticated:
            if 'current_pokemon' in session:
                current_pokemon = session['current_pokemon']

                # Check if the user already has 5 Pokémon
                user_id = current_user.id
                if PokemonCapture.query.filter_by(user_id=user_id).count() >= 5:
                    flash("Your Pokédex is full! You cannot catch more Pokémon.", 'error')
                    max_pokemon_reached = True
                else:
                    # Capture the current Pokémon
                    new_pokemon_capture = PokemonCapture(
                        pokemon_name=current_pokemon['name'],
                        user_id=current_user.id
                    )
                    db.session.add(new_pokemon_capture)
                    db.session.commit()
                    flash(f"You caught a {current_pokemon['name']}!", 'success')  # Display a success message
                    del session['current_pokemon']  # Remove the current Pokémon from the session

                    # Generate a new Pokémon for the display
                    random_pokemon_id = random.randint(1, 1000)
                    response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{random_pokemon_id}')

                    if response.status_code == 200:
                        data = response.json()
                        pokemon_info = {
                            'name': data['forms'][0]['name'],
                            'sprite_frontdefault': data['sprites']['other']['official-artwork']['front_default']
                        }
                    else:
                        flash("Failed to fetch a Pokémon. Try again later.", 'error')
            else:
                flash("No Pokémon to catch. Click 'Catch' again.", 'error')
        else:
            flash("You must be logged in to catch Pokémon.", 'error')

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

    # Fetch and add additional data from the API for each captured Pokémon
    for pokemon in captured_pokemon:
        pokemon_name = pokemon.pokemon_name
        pokemon_data = fetch_pokemon_data(pokemon_name)

        if pokemon_data:
            pokemon.sprite_frontdefault = pokemon_data['sprites']['other']['official-artwork']['front_default']
            pokemon.type = pokemon_data['types'][0]['type']['name']
            pokemon.ability1_name = pokemon_data['abilities'][0]['ability']['name']

            # Check if there is a second ability before accessing it
            if len(pokemon_data['abilities']) > 1:
                pokemon.ability2_name = pokemon_data['abilities'][1]['ability']['name']
            else:
                pokemon.ability2_name = "N/A"  # Set a default value when the second ability doesn't exist

            pokemon.base_experience = pokemon_data['base_experience']
            pokemon.attack_stat = pokemon_data['stats'][1]['base_stat']
            pokemon.hp_stat = pokemon_data['stats'][0]['base_stat']
            pokemon.defense_stat = pokemon_data['stats'][2]['base_stat']

    return render_template('user_page.html', captured_pokemon=captured_pokemon)




@app.route('/battle', methods=['GET'])
@login_required
def battle():
    # Verify that the user is logged in (current_user is available)
    if current_user.is_authenticated:
        # Query the database to get a list of users, excluding the current user
        users = User.query.filter(User.id != current_user.id).all()

        # Initialize an empty list to store user and Pokémon data
        user_pokemon_data = []

        for user in users:
            # Fetch Pokémon data for each user from the Pokédex API
            user_pokemon = PokemonCapture.query.filter_by(user_id=user.id).all()

            user_data = {
                'username': user.username,
                'pokemon': []
            }

            for pokemon in user_pokemon:
                # You can fetch Pokémon data from the Pokédex API based on the Pokémon name
                pokemon_name = pokemon.pokemon_name
                pokemon_data = fetch_pokemon_data(pokemon_name)

                if pokemon_data:
                    # Construct Pokémon data as needed, e.g., 'pokemon_data['sprites']['front_default']' for the sprite URL
                    pokemon_info = {
                        'name': pokemon_name,
                        'sprite_url': pokemon_data['sprites']['other']['official-artwork']['front_default']
                    }

                    user_data['pokemon'].append(pokemon_info)

            user_pokemon_data.append(user_data)

        return render_template('battle.html', user_pokemon_data=user_pokemon_data)
    else:
        flash("Please log in to access the battle page.", "error")
        return redirect(url_for('login_page'))




@app.route('/battle_result', methods=['POST'])
@login_required
def battle_result():
    if request.method == 'POST':
        # Get the opponent's username from the form
        opponent_username = request.form['opponent_username']

        # Retrieve the logged-in user and opponent's Pokemon from the database
        user = User.query.filter_by(username=current_user.username).first()
        
        if user is None:
            print(f"User with username {current_user.username} not found.")
        else:
            opponent = User.query.filter_by(username=opponent_username).first()

            # Initialize variables to keep track of wins
            user_wins = 0
            opponent_wins = 0

            # Iterate through the user's Pokémon and perform battles with the opponent's Pokémon
            for user_pokemon in user.captured_pokemon:
                # Select a random Pokémon from the opponent
                opponent_pokemon = random.choice(opponent.captured_pokemon)

                # You should add your battle logic here to determine the winner
                winner_user = perform_battle(user_pokemon, opponent_pokemon)

                # Update user and opponent's wins based on the battle result
                if winner_user == user:
                    user_wins += 1
                else:
                    opponent_wins += 1

            if user is not None:
                user.wins += user_wins
                # Commit the changes to the database
                db.session.commit()

            # Render the battle results page with winner 
            return render_template('battle_results.html', user=user, opponent=opponent, user_wins=user_wins, opponent_wins=opponent_wins)

    #  show the list of users for the logged-in user to choose an opponent
    users = User.query.filter(User.username != current_user.username).all()
    return render_template('battle.html', users=users)
