import speech_recognition as sr

def _transcribe(file):
  r = sr.Recognizer()
  with sr.AudioFile(file) as source:
    audio = r.record(source)
  try:
    return r.recognize_google(audio)
  except sr.UnknownValueError:
    return ''

def detect_speakers(result, speakers):
  words = []
  for res in result['results']:
    words.extend(res['alternatives'][0]['timestamps'])

  output = []
  index = 0

  last_speaker = None

  for segment in result['speaker_labels']:
    current_words = []
    end = segment['to']

    while index < len(words) and words[index][-1] <= end:
      current_words.append(words[index][0])
      index += 1

    if current_words:
      output.append({
        'new': segment['speaker'] != last_speaker,
        'last': last_speaker,
        'username': 'SPEAKER_{}'.format(segment['speaker']),
        'speaker': speakers.get(str(segment['speaker']), 'SPEAKER_{}'.format(segment['speaker'])),
        'transcript': current_words,
        'final': segment['final'],
      })

    last_speaker = segment['speaker']

  return output

def transcribe_all(file, watson, speakers):
  try:
    result, id_ = watson.recognize(file)
  except:
    return [], watson.last_sequence_id
  if 'speaker_labels' not in result:
    return [], id_
  return detect_speakers(result, speakers), id_

def train(file, watson):
  result, id_ = watson.recognize(file)
  if 'speaker_labels' not in result:
    return [], id_
  return map(lambda l: l['speaker'], result['speaker_labels']), id_
