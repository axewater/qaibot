import os
from flask import Flask, request, render_template, jsonify
from bot.integrations.openai_chat import ask_question
from bot.config import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    print(f"WEBUI: Received question:", request.get_json())
    try:
        data = request.get_json()
        question = data['question']
        answer = ask_question(question)
        print(f"WEBUI: Answer:", answer)
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/config')
def config():
    config_values = {key: value for key, value in globals().items() if key.isupper()}
    return render_template('config.html', config=config_values)

if __name__ == '__main__':
    FLASK_HOST = os.getenv('FLASK_HOST', '127.0.0.1')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    app.run(host=FLASK_HOST, port=FLASK_PORT)
