import tempfile
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
  file, path = tempfile.mkstemp()
  request.files['audio'].save(path)
  transcripts = transcribe_all(path, session['watson'])
  return jsonify({'transcripts': transcripts})
