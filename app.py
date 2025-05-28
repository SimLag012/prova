from flask import Flask, render_template, request, redirect, url_for, session
import os
from multiplayer_logic import (
    create_user, create_room, join_room, submit_phrase, vote_all_phrases,
    calculate_scores, all_submitted, all_voted, initialize_game_state,
    leave_room, users, rooms, room_players, room_state
)

app = Flask(__name__)
app.secret_key = 'supersecretkey'

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

@app.route('/room/<room_id>', methods=['GET', 'POST'])
def room(room_id):
    user_id = session.get('user_id')
    if not user_id or user_id not in users or room_id not in rooms:
        return redirect(url_for('lobby'))

    room = rooms[room_id]
    players = [users[uid] for uid in room_players[room_id] if uid in users]

    if room_id not in room_state:
        room_state[room_id] = initialize_game_state(players)

    state = room_state[room_id]

    if request.method == 'POST':
        if 'submit_phrase' in request.form:
            phrase = request.form['phrase']
            actual_type = request.form['actual_type']
            submit_phrase(state, user_id, phrase, actual_type)
            if all_submitted(state, players):
                state['game_state'] = 'voting'

        elif 'vote_all' in request.form:
            votes = {}
            for key in request.form:
                if key.startswith("guessed_type_"):
                    target_id = int(key.split("_")[2])
                    votes[target_id] = request.form[key]
            vote_all_phrases(state, user_id, votes)
            if all_voted(state, players):
                calculate_scores(players, state)
                room['status'] = 'finished'
                state['game_state'] = 'finished'

        elif 'restart_game' in request.form:
            if user_id == room['host_id']:
                room['status'] = 'waiting'
                for uid in room_players[room_id]:
                    if uid in users:
                        users[uid]['score'] = 0
                room_state[room_id] = initialize_game_state(players)

    return render_template('room.html', room=room, state=state, players=players, user_id=user_id)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
