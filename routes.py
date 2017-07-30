from flask import request, jsonify, render_template, session
from app import app
from audio import transcribe_all
from watson import Watson

@app.before_request
def preprocess_request():
  if 'watson' not in session:
    session['watson'] = Watson()

@app.route('/')
def index_view():
  return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_view():
  transcripts = transcribe_all(request.files['audio'], session['watson'])
  return jsonify({'transcripts': transcripts})

@app.route('/control', methods=['POST'])
def control_view():
  pass
