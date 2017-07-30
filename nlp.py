from simple_nlu.nlu import tag_speech, ExecutiveSummaryEvent
import redis, redis_lock, pickle

conn = redis.StrictRedis()

def _extract_actions(id, speakers, speaker, phrase):
  with redis_lock.Lock(conn, '{}/{}/lock'.format(id, 'summary')):
    key = '{}/{}'.format(id, 'summary')
    if conn.exists(key):
      summary = pickle.loads(conn.get(key))
    else:
      summary = ExecutiveSummaryEvent(speakers)

    res = tag_speech(speaker, summary, speakers, phrase)
    conn.set(key, pickle.dumps(summary))
    return res

def extract_actions(id, speakers, transcripts):
  actions = []

  if not transcripts:
    return actions

  current_words = []
  current_speaker = transcripts[0]['username']

  for transcript in transcripts:
    if transcript['username'] != current_speaker:
      actions.extend(_extract_actions(id, speakers, current_speaker, ' '.join(current_words) + '.'))

      current_words = []
      current_speaker = transcript['username']

    current_words.extend(transcript['transcript'])

  actions.extend(_extract_actions(id, speakers, current_speaker, ' '.join(current_words) + '.'))
  return actions


