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

  current_speaker = None

  for segment in result['speaker_labels']:
    current_words = []
    end = segment['to']

    while index < len(words) and words[index][-1] <= end:
      current_words.append(words[index][0])
      index += 1

    if current_words:
      output.append({
        'new': segment['speaker'] != current_speaker,
        'last': current_speaker,
        'speaker': speakers.get(current_speaker, 'SPEAKER_{}'.format(segment['speaker'])),
        'transcript': current_words,
        'final': segment['final'],
      })

    current_speaker = segment['speaker']

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
  result, _ = watson.recognize(file)
  if 'speaker_labels' not in result:
    return []
  return map(lambda l: l['speaker'], result['speaker_labels'])
