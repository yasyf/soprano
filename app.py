import os
from flask import Flask

app = Flask(__name__)
app.secret_key = os.environ.get('SK')
dev = bool(os.environ.get('DEV', True))
app.debug = dev

from routes import *

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=dev)
