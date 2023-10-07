from flask import request, render_template, redirect
import requests
from app import app
from .forms import PokeForm
from .forms import SignUpForm
from .models import User

@app.route("/")
def index_html():
    return render_template('index.html', title='Home Page')

@app.route('/pokedex', methods=['GET', 'POST'])
def get_pokemon_info():
    form = PokeForm()
    error_message = None  # Initialize error_message
    
    if request.method == 'POST':
        poke_name = form.pokemon.data.lower()
        print(poke_name)
        response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{poke_name}')
        
        if response.status_code == 200:
            data = response.json()
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
            
            return render_template('Pokedex.html', poke_info=poke_info, form=form, error_message=error_message)
        else:
            # Set the error message
            error_message = "The Pokémon you entered was not found. Please check the name or number and try again."
    
    return render_template('Pokedex.html', form=form, error_message=error_message)

# Define a simple user dictionary for demonstration purposes
users = {'user1': 'password1', 'user2': 'password2'}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username and password match
        if username in users and users[username] == password:
            return "Login Successful!"  # You can redirect to a different page here
        else:
            return "Login Failed. Please check your credentials."

    return render_template('login.html')

@app.route("/login")
def login_page():
    return render_template('login.html', title='Login')

@app.route("/signup", methods=['GET', 'POST'])
def signup_page():
    form = SignUpForm()
    if request.method == 'POST':
        if form.validate():
            username =form.username.data
            email =form.email.data
            password =form.password.data

            user = User(username, email, password)
    return render_template('signup.html', title='Sign Up', form=form)