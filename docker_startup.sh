#!/bin/sh

dockerize -wait tcp://$DB_HOSTNAME:3306 -timeout 25s
echo $GOOGLE_CREDENTIALS | base64 --decode > shapewatch_fcm_key.json
if [ "$NO_MIGRATE" != "1" ]; then
    python3 manage.py migrate
    echo "=== MIGRATION COMPLETE ==="
fi

echo "=== LOADING DJANGO APP === "

exec "$@"
