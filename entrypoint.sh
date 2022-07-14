#!/bin/sh

echo "Waiting for postgres..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "PostgreSQL started"

echo "Waiting for rabbitmq..."
while ! (telnet rabbitmq 5672 2>&1 < /dev/null | grep "Connected to rabbitmq"); do
  sleep 0.1
done
echo "Rabbitmq started"


python manage.py flush --no-input
python manage.py migrate

exec "$@"