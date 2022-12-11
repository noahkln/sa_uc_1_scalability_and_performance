
FROM ubuntu:22.04

# Install curl
RUN apt-get update && apt-get install -y \
  curl

# Install dolt
RUN curl -L https://github.com/dolthub/dolt/releases/download/v0.50.14/install.sh | bash

# Test dolt
RUN dolt version

RUN mkdir -p /app/db
COPY ./direct/standby/config.yaml /app/config.yaml

EXPOSE 3306

CMD cd /app/db && dolt sql-server --config /app/config.yaml
