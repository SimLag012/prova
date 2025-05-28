import random

def initialize_game_state(players):
    return {
        'game_state': 'submitting',
        'submissions': [],
        'submitted': {p['id']: False for p in players},
        'votes': {p['id']: {} for p in players},
        'round': 1
    }

def submit_phrase(state, user_id, phrase, actual_type):
    state['submissions'].append({
        'user_id': user_id,
        'phrase': phrase,
        'actual_type': actual_type
    })
    state['submitted'][user_id] = True
    if all(state['submitted'].values()):
        state['game_state'] = 'voting'

def vote_on_phrases(state, voter_id, votes_dict):
    state['votes'][voter_id] = votes_dict
    all_voted = all(
        len(votes) == len(state['submissions']) - 1
        for votes in state['votes'].values()
    )
    return all_voted

def calculate_scores(players, state):
    for voter_id, guesses in state['votes'].items():
        for submission in state['submissions']:
            target_id = submission['user_id']
            if target_id != voter_id:
                guessed_type = guesses.get(target_id)
                if guessed_type == submission['actual_type']:
                    for player in players:
                        if player['id'] == voter_id:
                            player['score'] += 1
                            break
