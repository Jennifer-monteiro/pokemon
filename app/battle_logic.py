
import random
import requests

def fetch_pokemon_data(pokemon_name):
    # Define the base URL for the PokeAPI
    base_url = 'https://pokeapi.co/api/v2/pokemon/'

    # Construct the URL for the specific Pokémon
    url = f'{base_url}{pokemon_name.lower()}'

    # Send a GET request to the API
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        return None
    
def calculate_pokemon_score(pokemon):
    # Calculate a score based on attack and defense attributes
    score = pokemon.hp + pokemon.attack - pokemon.defense
    return score

def perform_battle(user_pokemon, opponent_pokemon):
    # Calculate scores for user's and opponent's Pokémon
    user_score = calculate_pokemon_score(user_pokemon)
    opponent_score = calculate_pokemon_score(opponent_pokemon)

    # Determine the winner based on scores
    if user_score > opponent_score:
        return user_pokemon  # User wins
    elif opponent_score > user_score:
        return opponent_pokemon  # Opponent wins
    else:
        return random.choice([user_pokemon, opponent_pokemon])