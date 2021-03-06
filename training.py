import redis, json

class Training(object):
  def __init__(self, id):
    self.conn = redis.StrictRedis()
    self.id = id

    if not self.conn.exists(self.key('current')):
      self.conn.setnx(self.key('current'), json.dumps({}))

    if not self.conn.exists(self.key('labels')):
      self.conn.setnx(self.key('labels'), json.dumps({}))

    if not self.conn.exists(self.key('speakers')):
      self.conn.setnx(self.key('speakers'), json.dumps({}))

    if not self.conn.exists(self.key('segments')):
      self.conn.setnx(self.key('segments'), json.dumps([]))

    self.current = json.loads(self.conn.get(self.key('current')))
    self.labels = json.loads(self.conn.get(self.key('labels')))
    self.speakers = json.loads(self.conn.get(self.key('speakers')))
    self.segments = json.loads(self.conn.get(self.key('segments')))

  def key(self, path):
    return '{}/{}'.format(self.id, path)

  def add(self, labels, sequence_id):
    self.labels[self.current['email']].extend(labels)
    self.segments.append(sequence_id)

    self.conn.set(self.key('labels'), json.dumps(self.labels))
    self.conn.set(self.key('segments'), json.dumps(self.segments))

  def stop(self, email):
    self.current = {}
    labels = self.labels.pop(email)
    if labels:
      label = str(sorted(labels, key=labels.count)[-1])
      self.speakers[label] = email

    self.conn.set(self.key('current'), json.dumps(self.current))
    self.conn.set(self.key('labels'), json.dumps(self.labels))
    self.conn.set(self.key('speakers'), json.dumps(self.speakers))

  def start(self, email):
    self.current = {'email': email}
    self.labels[email] = []

    self.conn.set(self.key('current'), json.dumps(self.current))
    self.conn.set(self.key('labels'), json.dumps(self.labels))
