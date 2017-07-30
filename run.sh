#!/bin/bash

redis-server &
(cd soprano && npm start) &
gunicorn -b 127.0.0.1:5000 -t 90 -w 5 app:app
