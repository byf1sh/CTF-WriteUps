#!/bin/bash
docker rm -f cmd
docker rmi -f cmd
docker build --tag=cmd .
docker run -d -p 5000:5000 --name=cmd cmd