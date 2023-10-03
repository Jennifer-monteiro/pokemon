from flask import request, render_template
import requests
from app import app
from .forms import PokeForm

@app.route("/")
def index_html():
    return render_template('index.html')

@app.route('/pokedex', methods =['GET', 'POST'])
def get_pokemon_info():
    form = PokeForm()
    if request.method=='POST':
        poke_name = form.pokemon.data.lower()
        print(poke_name)
        response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{poke_name}')
        data = response.json()
        
        poke_info ={
            'name':data['forms'][0]['name'],
            'ability1_name':data['abilities'][0]['ability']['name'],
           'ability2_name':data['abilities'][1]['ability']['name'],
            'base_experience':data['base_experience'],
            'sprite_frontshiny':data['sprites']['front_shiny'],
            'attack_stat':data['stats'][1]['base_stat'],
            'hp_stat':data['stats'][0]['base_stat'],
            'defense_stat':data['stats'][2]['base_stat']
        }
      
        return  render_template('Pokedex.html',poke_info=poke_info, form=form)
    else:
     return  render_template('Pokedex.html', form=form)