#!/bin/bash

redis-server &
(cd soprano && npm start) &
gunicorn -b 0.0.0.0:5000 -t 90 -w 5 app:app
