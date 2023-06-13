#!/bin/sh

./update.sh
if [ $? -ne 0 ]
then
  echo "Application update error"
  exit $?
else
  ./celery-worker.sh & web-sockets & ./server-gunicorn.sh && fg
fi

#/usr/bin/supervisord -c supervisord.conf
