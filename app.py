from flask import Flask, render_template, request
import random
import os
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
