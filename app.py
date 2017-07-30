import os, tempfile
from flask import Flask
from flask_session import FileSystemSessionInterface
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = os.environ.get('SK')
dev = bool(os.environ.get('DEV', True))
app.debug = dev
app.session_interface = FileSystemSessionInterface(tempfile.mkdtemp(), 500, 0600, 'session')

CORS(app, supports_credentials=True)

from routes import *

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=dev)
