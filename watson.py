import requests, os

class Watson(object):
  API_ROOT = 'https://stream.watsonplatform.net/speech-to-text/api/v1'
  USERNAME = os.getenv('IBM_USERNAME')
  PASSWORD = os.getenv('IBM_PASSWORD')

  @classmethod
  def api_path(cls, path):
    return '{root}/{p}'.format(root=cls.API_ROOT, p=path)

  def __init__(self):
    self.session = requests.Session()
    self.urls = self.post(self.api_path('sessions'))
    self._sequence_id = 0

  def post(self, path, params=None, data=None, headers=None):
    return self.session.post(
      path,
      params=(params or {}),
      auth=(self.USERNAME, self.PASSWORD),
      headers=(headers or {}),
      data=data,
    ).json()

  @property
  def sequence_id(self):
    self._sequence_id += 1
    return self._sequence_id

  def recognize(self, file):
    return self.post(
      self.urls['recognize'],
      {
        'sequence_id': self.sequence_id,
        'speaker_labels': True,
        'smart_formatting': True,
        'inactivity_timeout': -1,
      },
      file,
      {'Content-Type': 'audio/wav'}
    )
