from flask import request, jsonify, render_template, session
from app import app
from audio import transcribe_all, train
from watson import Watson
from training import Training
from constants import STARTING, STOPPING

@app.before_request
def preprocess_request():
  if 'watson' not in session:
    session['watson'] = Watson()
    session['training'] = Training()

@app.route('/')
def index_view():
  return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_view():
  if session['training'].current:
    labels = train(request.files['audio'], session['watson'])
    session['training'].add(labels)
    return jsonify({'training': session['training'].current})
  else:
    transcripts = transcribe_all(request.files['audio'], session['watson'], session['training'].speakers)
    return jsonify({'transcripts': transcripts})

@app.route('/observe/<sequence_id>')
def observe_view(sequence_id):
  return jsonify({'transcripts': session['watson'].observe(sequence_id)})

@app.route('/control', methods=['POST'])
def control_view():
  if request.form['status'] == STARTING:
    session['training'].start(request.form['email'])
  elif request.form['status'] == STOPPING:
    session['training'].stop(request.form['email'])
  return jsonify({'training': session['training'].current})
