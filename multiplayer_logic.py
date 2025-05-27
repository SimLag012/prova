# multiplayer_logic.py
# Logica multiplayer ispirata a TruthMemeMaker, adattata per Flask
import random
import string
from collections import defaultdict

# In-memory storage (puoi sostituire con un database in futuro)
rooms = {}
users = {}
room_players = defaultdict(list)  # room_id -> list of user_ids
room_state = {}  # room_id -> dict con stato partita


def generate_room_id(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def create_user(username, display_name):
    user_id = len(users) + 1
    users[user_id] = {'id': user_id, 'username': username, 'display_name': display_name, 'score': 0}
    return users[user_id]

def create_room(host_id, max_rounds=5):
    room_id = generate_room_id()
    rooms[room_id] = {
        'id': room_id,
        'host_id': host_id,
        'status': 'waiting',
        'current_player': host_id,
        'current_round': 1,
        'max_rounds': max_rounds,
        'submissions': [],
        'votes': []
    }
    room_players[room_id].append(host_id)
    room_state[room_id] = {
        'game_state': 'lobby',
        'current_submission': None,
        'voting': False
    }
    return rooms[room_id]

def join_room(room_id, user_id):
    if user_id not in room_players[room_id]:
        room_players[room_id].append(user_id)
    return True

def submit_phrase(room_id, user_id, phrase, actual_type):
    submission = {
        'player_id': user_id,
        'phrase': phrase,
        'actual_type': actual_type,
        'votes': []
    }
    rooms[room_id]['submissions'].append(submission)
    room_state[room_id]['current_submission'] = submission
    room_state[room_id]['voting'] = True
    return submission

def vote_submission(room_id, voter_id, guessed_type):
    submission = room_state[room_id]['current_submission']
    is_correct = guessed_type == submission['actual_type']
    submission['votes'].append({'voter_id': voter_id, 'guessed_type': guessed_type, 'is_correct': is_correct})
    # Aggiorna punteggio
    if is_correct:
        users[voter_id]['score'] += 1
    return is_correct

def next_round(room_id):
    rooms[room_id]['current_round'] += 1
    room_state[room_id]['voting'] = False
    room_state[room_id]['current_submission'] = None
    if rooms[room_id]['current_round'] > rooms[room_id]['max_rounds']:
        rooms[room_id]['status'] = 'finished'
        room_state[room_id]['game_state'] = 'results'
    else:
        room_state[room_id]['game_state'] = 'playing'

def remove_empty_rooms():
    to_remove = [room_id for room_id, players in room_players.items() if len(players) == 0]
    for room_id in to_remove:
        rooms.pop(room_id, None)
        room_players.pop(room_id, None)
        room_state.pop(room_id, None)

def leave_room(room_id, user_id):
    if user_id in room_players[room_id]:
        room_players[room_id].remove(user_id)
    remove_empty_rooms()
    return True
