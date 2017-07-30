from flask import request, jsonify, render_template, session
from app import app
from audio import transcribe_all, train, detect_speakers
from watson import Watson
from training import Training
from constants import STARTING, STOPPING
from nlp import extract_actions

def reset_session():
  session['watson'] = Watson()
  session['training'] = Training()

@app.before_request
def preprocess_request():
  if 'watson' not in session:
    reset_session()

@app.route('/')
def index_view():
  return render_template('index.html')

@app.route('/reset', methods=['POST'])
def reset_view():
  reset_session()
  return jsonify({'training': session['training'].current})

@app.route('/submit', methods=['POST'])
def submit_view():
  if session['training'].current:
    labels = train(request.files['audio'], session['watson'])
    session['training'].add(labels)
    return jsonify({'training': session['training'].current})
  else:
    transcripts, id_ = transcribe_all(request.files['audio'], session['watson'], session['training'].speakers)
    return jsonify({'transcripts': transcripts, 'id': id_})

@app.route('/observe')
def default_observe_view():
  if not session['watson'].last_sequence_id:
    return jsonify({'error': True})
  return observe_view(session['watson'].last_sequence_id)

@app.route('/observe/<sequence_id>')
def observe_view(sequence_id):
  transcripts = session['watson'].observe(sequence_id)
  if transcripts.get('code') == 404:
    return jsonify({'retry': False, 'error': True, 'id': sequence_id})
  if 'speaker_labels' not in transcripts:
    return jsonify({'retry': True, 'error': False, 'id': sequence_id})
  transcripts = detect_speakers(transcripts, session['training'].speakers)
  actions = extract_actions(transcripts)
  return jsonify({'retry': False, 'error': False, 'transcripts': transcripts, 'id': sequence_id, 'actions': actions})

@app.route('/control', methods=['POST'])
def control_view():
  if request.form['status'] == STARTING:
    session['training'].start(request.form['email'])
  elif request.form['status'] == STOPPING:
    session['training'].stop(request.form['email'])
  return jsonify({'training': session['training'].current})
