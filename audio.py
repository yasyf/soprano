import speech_recognition as sr

def _transcribe(file):
  r = sr.Recognizer()
  with sr.AudioFile(file) as source:
    audio = r.record(source)
  try:
    return r.recognize_google(audio)
  except sr.UnknownValueError:
    return ''

def _detect_speakers(result):
  words = []
  for res in result['results']:
    words.extend(res['alternatives'][0]['timestamps'])

  output = []
  index = 0

  for segment in result['speaker_labels']:
    current_words = []
    end = segment['to']

    while index < len(words) and words[index][-1] <= end:
      current_words.append(words[index][0])
      index += 1

    if current_words:
      output.append({
        'speaker': segment['speaker'],
        'transcript': current_words,
        'final': segment['final']
      })

  return output

def transcribe_all(file, watson):
  result = watson.recognize(file)
  return _detect_speakers(result)
