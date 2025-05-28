import random
import string
from collections import defaultdict

rooms = {}
users = {}
room_players = defaultdict(list)
room_state = {}

def generate_room_id(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def create_user(username, display_name):
    for u in users.values():
        if u['username'] == username:
            return None
    user_id = len(users) + 1
    users[user_id] = {'id': user_id, 'username': username, 'display_name': display_name, 'score': 0}
    return users[user_id]

def create_room(host_id):
    room_id = generate_room_id()
    rooms[room_id] = {
        'id': room_id,
        'host_id': host_id,
        'status': 'waiting'
    }
    room_players[room_id].append(host_id)
    return rooms[room_id]

def join_room(room_id, user_id):
    if user_id not in room_players[room_id]:
        room_players[room_id].append(user_id)
    return True

def initialize_game_state(players):
    return {
        'game_state': 'submission',
        'submissions': [],
        'votes': defaultdict(dict)
    }

def submit_phrase(state, user_id, phrase, actual_type):
    state['submissions'].append({
        'player_id': user_id,
        'phrase': phrase,
        'actual_type': actual_type
    })

def vote_all_phrases(state, voter_id, votes):
    state['votes'][voter_id] = votes

def all_submitted(state, players):
    return len(state['submissions']) == len(players)

def all_voted(state, players):
    return len(state['votes']) == len(players)

def calculate_scores(players, state):
    submissions = state['submissions']
    votes = state['votes']
    for voter_id, guesses in votes.items():
        for submission in submissions:
            target_id = submission['player_id']
            actual = submission['actual_type']
            guessed = guesses.get(target_id)
            if guessed == actual:
                users[voter_id]['score'] += 1

def leave_room(room_id, user_id):
    if user_id in room_players[room_id]:
        room_players[room_id].remove(user_id)
    if len(room_players[room_id]) == 0:
        del rooms[room_id]
        del room_players[room_id]
        if room_id in room_state:
            del room_state[room_id]
