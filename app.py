from flask import Flask, render_template, request, redirect, url_for
import random
from game_logic import get_random_truth_or_meme

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/play', methods=['POST'])
def play():
    choice = request.form.get('choice')
    prompt, kind = get_random_truth_or_meme()
    return render_template('result.html', prompt=prompt, kind=kind)

if __name__ == '__main__':
    app.run(debug=True)
