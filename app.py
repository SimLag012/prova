from flask import Flask, render_template, request, redirect, url_for, session
from game_logic import get_random_truth_or_meme
from multiplayer_logic import (
    create_user, create_room, join_room, submit_phrase, vote_submission, next_round,
    users, rooms, room_players, room_state
)

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necessario per sessioni

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('lobby'))
    else:
        return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        display_name = request.form['display_name']
        user = create_user(username, display_name)
        if user is None:
            error = "Username già esistente!"
        else:
            session['user_id'] = user['id']
            return redirect(url_for('lobby'))
    return render_template('register.html', error=error)

@app.route('/leave_room', methods=['POST'])
def leave_room_route():
    user_id = session.get('user_id')
    room_id = session.get('room_id')
    if user_id and room_id:
        from multiplayer_logic import leave_room
        leave_room(room_id, user_id)
        session.pop('room_id', None)
    return redirect(url_for('lobby'))



@app.route('/lobby', methods=['GET', 'POST'])
def lobby():
    user_id = session.get('user_id')
    if not user_id or user_id not in users:
        return redirect(url_for('register'))
    if request.method == 'POST':
        if 'create_room' in request.form:
            room = create_room(user_id)
            session['room_id'] = room['id']
            return redirect(url_for('room', room_id=room['id']))
        elif 'join_room' in request.form:
            room_id = request.form['room_id']
            if room_id in rooms and join_room(room_id, user_id):
                session['room_id'] = room_id
                return redirect(url_for('room', room_id=room_id))
    return render_template('lobby.html', rooms=rooms)

@app.route('/lobby/_info')
def lobby_info():
    user_id = session.get('user_id')
    if not user_id or user_id not in users:
        return {'error': 'not allowed'}
    # Includi anche i giocatori nelle stanze per aggiornamento live
    rooms_info = {}
    for room_id, room in rooms.items():
        rooms_info[room_id] = {
            'host_id': room['host_id'],
            'status': room['status'],
            'players': [users[uid]['display_name'] for uid in room_players[room_id] if uid in users]
        }
    return {'rooms': rooms_info}

@app.route('/room/<room_id>', methods=['GET', 'POST'])
def room(room_id):
    user_id = session.get('user_id')
    if not user_id or user_id not in users or room_id not in rooms:
        return redirect(url_for('lobby'))
    room = rooms[room_id]
    state = room_state[room_id]
    players = [users[uid] for uid in room_players[room_id] if uid in users]
    if request.method == 'POST':
        if 'submit_phrase' in request.form:
            phrase = request.form['phrase']
            actual_type = request.form['actual_type']
            submit_phrase(room_id, user_id, phrase, actual_type)
        elif 'vote' in request.form:
            guessed_type = request.form['guessed_type']
            vote_submission(room_id, user_id, guessed_type)
        elif 'next_round' in request.form:
            next_round(room_id)
        elif 'restart_game' in request.form:
            if user_id == room['host_id']:
                # Reset room state and scores
                room['status'] = 'waiting'
                room['current_round'] = 1
                room['submissions'] = []
                room['votes'] = []
                for uid in room_players[room_id]:
                    if uid in users:
                        users[uid]['score'] = 0
                room_state[room_id] = {
                    'game_state': 'lobby',
                    'current_submission': None,
                    'voting': False
                }
    return render_template('room.html', room=room, state=room_state[room_id], players=players, user_id=user_id)

@app.route('/room/<room_id>/_info')
def room_info_api(room_id):
    user_id = session.get('user_id')
    if not user_id or user_id not in users or room_id not in rooms:
        return {'error': 'not allowed'}
    room = rooms[room_id]
    state = room_state[room_id]
    players = [users[uid]['display_name'] for uid in room_players[room_id] if uid in users]
    return {
        'room': room,
        'state': state,
        'players': players
    }

@app.route('/play', methods=['POST'])
def play():
    choice = request.form.get('choice')
    prompt, kind = get_random_truth_or_meme()
    return render_template('result.html', prompt=prompt, kind=kind)

if __name__ == '__main__':
    app.run(debug=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)