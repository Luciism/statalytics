FROM redis:8.2.1-alpine

COPY ./redis.conf /etc/redis/redis.conf
COPY ./docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
COPY ./healthcheck.sh /usr/local/bin/healthcheck.sh

ENTRYPOINT ["docker-entrypoint.sh"]

