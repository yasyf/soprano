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

  current_speaker = None
  current_words = []
  current_final = False

  for segment in result['speaker_labels']:
    if segment['speaker'] != current_speaker:
      if current_words:
        output.append({
          'speaker': current_speaker,
          'transcript': current_words,
          'final': current_final
        })

      current_speaker = segment['speaker']
      current_words = []
      current_final = False

    end = segment['to']

    while index < len(words) and words[index][-1] <= end:
      current_words.append(words[index][0])
      index += 1

  return output

def transcribe_all(file, watson):
  result = watson.recognize(file)
  return _detect_speakers(result)
