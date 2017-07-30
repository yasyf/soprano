#!/bin/bash

nginx &
redis-server &
(cd soprano && ./node_modules/serve/bin/serve.js -s build) &
DEV=false gunicorn -b 0.0.0.0:8080 -t 90 -w 5 app:app
