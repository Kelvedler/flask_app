#!/bin/sh

celery -A make_celery worker -B -l info -c 4
