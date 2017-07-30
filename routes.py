import uuid
from flask import request, jsonify, render_template, session, g
from app import app
from audio import transcribe_all, train, detect_speakers
from watson import Watson
from training import Training
from constants import STARTING, STOPPING
from nlp import extract_actions

def reset_session():
  session['id'] = str(uuid.uuid4())

def assign_g():
  g.training = Training(session['id'])
  g.watson = Watson(session['id'])

@app.before_request
def preprocess_request():
  if 'id' not in session:
    reset_session()
  assign_g()

@app.route('/')
def index_view():
  return render_template('index.html')

@app.route('/reset', methods=['POST'])
def reset_view():
  reset_session()
  assign_g()
  return jsonify({'training': g.training.current})

@app.route('/submit', methods=['POST'])
def submit_view():
  if g.training.current:
    labels, id_ = train(request.files['audio'], g.watson)
    g.training.add(labels, id_)
    return jsonify({'training': g.training.current})
  else:
    transcripts, id_ = transcribe_all(request.files['audio'], g.watson, g.training.speakers)
    return jsonify({'transcripts': transcripts, 'id': id_})

@app.route('/observe')
def default_observe_view():
  return observe_view(g.watson.last_sequence_id)

@app.route('/observe/<sequence_id>')
def observe_view(sequence_id):
  if not sequence_id:
    return jsonify({'error': True})
  transcripts = g.watson.observe(sequence_id)
  if transcripts.get('code') == 404:
    return jsonify({'retry': False, 'error': True, 'id': sequence_id})
  if 'speaker_labels' not in transcripts:
    return jsonify({'retry': True, 'error': False, 'id': sequence_id})
  if g.training.current or sequence_id in g.training.segments:
    return jsonify({'retry': False, 'error': False, 'training': g.training.current})
  transcripts = detect_speakers(transcripts, g.training.speakers)
  actions = extract_actions(session['id'], g.training.speakers, transcripts)
  return jsonify({'retry': False, 'error': False, 'transcripts': transcripts, 'id': sequence_id, 'actions': actions})

@app.route('/control', methods=['POST'])
def control_view():
  if request.form['status'] == STARTING:
    g.training.start(request.form['email'])
  elif request.form['status'] == STOPPING:
    g.training.stop(request.form['email'])
  return jsonify({'training': g.training.current})
