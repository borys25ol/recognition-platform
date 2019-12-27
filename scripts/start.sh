#!/bin/bash

DB_HOST=$(echo $DB_HOST)
CONFIG_FILE=$(echo $CONFIG_FILE)

sed -i s/localhost/$DB_HOST/ ./alembic.ini

alembic revision
make migrate

python main.py -c config/$CONFIG_FILE