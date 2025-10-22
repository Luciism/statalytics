#!/bin/sh
# Copy template to a writable location inside the container
cp /etc/redis/redis.conf /tmp/redis.conf

# Replace placeholder in the copy
sed -i "s|__REDIS_PASSWORD__|$REDIS_PASSWORD|g" /tmp/redis.conf

# Start Redis with the writable config
exec redis-server /tmp/redis.conf

