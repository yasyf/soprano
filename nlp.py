def _extract_actions(speaker, phrase):
  print(speaker + ': ' + phrase)
  return []

def extract_actions(transcripts):
  actions = []

  current_words = []
  current_speaker = transcripts[0]['speaker']

  for transcript in transcripts:
    if transcript['speaker'] != current_speaker:
      phrase = ' '.join(current_words) + '.'
      actions.extend(_extract_actions(current_speaker, phrase))

      current_words = []
      current_speaker = transcript['speaker']

    current_words.extend(transcript['transcript'])

  return actions
