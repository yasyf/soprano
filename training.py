class Training(object):
  def __init__(self):
    self.current = None
    self.labels = {}
    self.speakers = {}

  def start(self, email):
    self.current = email
    self.labels[email] = []

  def add(self, labels):
    self.labels[self.current].extend(labels)

  def stop(self, email):
    self.current = None
    labels = self.labels.pop(email)
    label = sorted(labels, key=labels.count)[-1]
    self.speakers[label] = email
