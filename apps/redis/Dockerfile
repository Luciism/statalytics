FROM redis:8.2.1-alpine

COPY ./redis.conf /etc/redis/redis.conf
COPY ./docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]

