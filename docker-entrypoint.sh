#!/bin/bash
set -e

# Nginx site
cp -a /boxee/boxee-site /etc/nginx/sites-available/boxee-site

if [ ! -f /etc/nginx/sites-enabled/boxee-site ]; then
    ln -s /etc/nginx/sites-available/boxee-site /etc/nginx/sites-enabled
fi

# Kill pyc's if they're around, can't chown them below
find . -name "*.pyc" -delete

# File perms for www-data user
touch /var/run/nginx.pid
chown -R www-data:www-data /var/run/nginx.pid
chown -R www-data:www-data /var/cache/nginx
chown -R www-data:www-data /boxee/

rm /etc/nginx/sites-enabled/default

mkdir -p /var/log/uwsgi
chown -R appuser:appuser /var/log/uwsgi

mkdir -p /var/log/flask/
chown -R appuser:appuser /var/log/flask

echo 'Starting uwsgi'
exec uwsgi -s /tmp/boxee.sock --mount /boxee=app:app --uid 999 --enable-threads --logto /tmp/uwsgi.log --http 0.0.0.0:8000 --master &

echo 'Starting nginx'
exec nginx -g "daemon off;"
