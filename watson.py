import requests, os, redis, json, redis_lock

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

    if not self.conn.exists(self.key('cookies')):
      self.conn.setnx(self.key('cookies'), json.dumps({}))

    for name, value in json.loads(self.conn.get(self.key('cookies'))).items():
      self.session.cookies.set(name, value)

  def key(self, path):
    return '{}/{}'.format(self.id, path)

  def post(self, path, params=None, data=None, headers=None):
    res = self.session.post(
      path,
      params=(params or {}),
      auth=(self.USERNAME, self.PASSWORD),
      headers=(headers or {}),
      data=data,
      cookies=self.cookies,
    ).json()

    cookies = requests.utils.dict_from_cookiejar(self.session.cookies)
    self.conn.set(self.key('cookies'), json.dumps(cookies))

    return res

  def get(self, path, params=None, headers=None):
    res = self.session.get(
      path,
      params=(params or {}),
      auth=(self.USERNAME, self.PASSWORD),
      headers=(headers or {}),
      cookies=self.cookies,
    ).json()

    cookies = requests.utils.dict_from_cookiejar(self.session.cookies)
    self.conn.set(self.key('cookies'), json.dumps(cookies))

    return res

  @property
  def cookies(self):
    return requests.utils.cookiejar_from_dict(json.loads(self.conn.get(self.key('cookies')) or '{}'))

  @property
  def urls(self):
    return json.loads(self.conn.get(self.key('urls')))

  @property
  def last_sequence_id(self):
    return int(self.conn.get(self.key('sequence_id')) or 0)

  def next_sequence_id(self):
    return int(self.conn.incr(self.key('sequence_id')))

  def observe(self, sequence_id):
    return self.get(self.urls['observe_result'], {'sequence_id': sequence_id, 'interim_results': False})

  def recognize(self, file):
    with redis_lock.Lock(self.conn, 'recognize/lock'):
      id = self.next_sequence_id()
      result = self.post(
        self.urls['recognize'],
        {
          'sequence_id': id,
          'speaker_labels': True,
          'smart_formatting': True,
          'inactivity_timeout': -1,
        },
        file,
        {'Content-Type': 'audio/wav'}
      )
      return result, id
