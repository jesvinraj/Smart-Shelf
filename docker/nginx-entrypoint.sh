#!/bin/sh
set -e

# Generate a self-signed certificate on first start so HTTPS works out of the
# box. Replace /etc/nginx/certs/server.{crt,key} with your real certificate
# for production.
if [ ! -f /etc/nginx/certs/server.crt ]; then
    echo "[nginx] generating self-signed certificate..."
    mkdir -p /etc/nginx/certs
    openssl req -x509 -newkey rsa:2048 -nodes -days 365 \
        -subj "/CN=localhost" \
        -keyout /etc/nginx/certs/server.key \
        -out /etc/nginx/certs/server.crt
fi

exec nginx -g 'daemon off;'