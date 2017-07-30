#!/bin/bash

redis-server &;
gunicorn -b 127.0.0.1:5000 -t 90 -w 5 --preload app:app &;
(cd soprano && npm start) &;
