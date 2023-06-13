#!/bin/sh

NC='\033[0m'
GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'

echo "${CYAN}Running database migrations${NC}"

alembic upgrade head
if [ $? -eq 0 ]
then
  echo "${GREEN}Database migrations succeeded${NC}"

  sleep 10

  echo  "${CYAN}Running elasticsearch migrations${NC}"

  elastic-migrations --direction forwards

  if [ $? -eq 0 ]
  then
    echo "${GREEN}Elasticsearch migrations succeeded${NC}"
  else
    echo "${RED}Failed to run elasticsearch migrations${NC}"
  fi
else
  echo "${RED}Failed to run database migrations${NC}"
fi
