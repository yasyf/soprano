#!/bin/bash

redis-server &
(cd soprano && serve -s build) &
DEV=false gunicorn -b 0.0.0.0:8080 -t 90 -w 5 app:app
