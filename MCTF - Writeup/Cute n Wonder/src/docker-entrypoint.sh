#!/bin/bash

# push flag
while ! curl -s --fail "http://127.0.0.1:5000/prompt?prompt=$FLAG" > /dev/null; do sleep 1; done &

# run server
flask --app app run --host=0.0.0.0
