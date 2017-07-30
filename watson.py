import requests, os, redis, json

class Watson(object):
  API_ROOT = 'https://stream.watsonplatform.net/speech-to-text/api/v1'
  USERNAME = os.getenv('IBM_USERNAME')
  PASSWORD = os.getenv('IBM_PASSWORD')

  @classmethod
  def api_path(cls, path):
    return '{root}/{p}'.format(root=cls.API_ROOT, p=path)

  def __init__(self, id):
    self.conn = redis.StrictRedis()
    self.session = requests.Session()
    self.id = id

    if not self.conn.exists(self.key('urls')):
      self.conn.setnx(self.key('urls'), json.dumps(self.post(self.api_path('sessions'))))
    self.urls = json.loads(self.conn.get(self.key('urls')))

  def key(self, path):
    return '{}/{}'.format(self.id, path)

  def post(self, path, params=None, data=None, headers=None):
    return self.session.post(
      path,
      params=(params or {}),
      auth=(self.USERNAME, self.PASSWORD),
      headers=(headers or {}),
      data=data,
    ).json()

  def get(self, path, params=None, headers=None):
    return self.session.get(
      path,
      params=(params or {}),
      auth=(self.USERNAME, self.PASSWORD),
      headers=(headers or {}),
    ).json()

  @property
  def last_sequence_id(self):
    return self.conn.get(self.key('sequence_id')) or 0

  @property
  def next_sequence_id(self):
    return self.conn.incr(self.key('sequence_id'))

  def observe(self, sequence_id):
    return self.get(self.urls['observe_result'], {'sequence_id': sequence_id, 'interim_results': False})

  def recognize(self, file):
    id = self.next_sequence_id
    return self.post(
      self.urls['recognize'],
      {
        'sequence_id': id,
        'speaker_labels': True,
        'smart_formatting': True,
        'inactivity_timeout': -1,
      },
      file,
      {'Content-Type': 'audio/wav'}
    ), id
