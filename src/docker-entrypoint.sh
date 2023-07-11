#!/bin/sh

./update.sh
if [ $? -ne 0 ]
then
  echo "Application update error"
  exit $?
else
  /usr/bin/supervisord -c supervisord.conf
fi
