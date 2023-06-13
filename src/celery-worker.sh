#!/bin/sh
sleep 5

celery -A make_celery worker -B -l info -c 4
