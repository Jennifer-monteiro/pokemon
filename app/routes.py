from app import app
import requests
from flask import redirect, render_template, request, url_for
from .forms import PokeForm
from .forms import SignUpForm
from .models import db, User
from .forms import LoginForm
from flask_login import login_user, logout_user, current_user, login_required


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
            username =form.username.data
            email =form.email.data
            password =form.password.data

            user = User(username, email, password)

            db.session.add(user)
            db.session.commit()
        else:
            print("FORM INVALID!")
            print(form.errors)

    return render_template('signup.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate():
            username =form.username.data
            password =form.password.data

            #look database for use with the username
             #if match log in

            user = User.query.filter_by(username=username).first()
            if user:
                if user.password == password:
                    login_user(user)
                else:
                    print('User doesnt exist')
                
            else:
                print("FORM INVALID!")
        return redirect(url_for('index_html'))
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login_page'))