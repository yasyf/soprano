import os, tempfile
from flask import Flask
from flask_session import Session

SESSION_TYPE = 'filesystem'
SESSION_FILE_DIR = tempfile.mkdtemp()

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = os.environ.get('SK')
dev = bool(os.environ.get('DEV', True))
app.debug = dev

Session(app)

from routes import *

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=dev)
