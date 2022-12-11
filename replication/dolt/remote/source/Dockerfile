
FROM ubuntu:22.04

ARG PUB_CRED="none"

# Install curl
RUN apt-get update && apt-get install -y \
  dos2unix \
  curl

# Install dolt
RUN curl -L https://github.com/dolthub/dolt/releases/download/v0.50.14/install.sh | bash

# Test dolt
RUN dolt version

RUN mkdir -p /app/db
RUN dolt clone noahkln/sa_uc_1_replication /app/db
COPY ./remote/source/config.yaml /app/config.yaml
COPY ./remote/source/set_variables.sh /app/set_variables.sh
COPY ./remote/creds.jwk /app/creds.jwk
RUN dolt creds import /app/creds.jwk
RUN dolt creds use $PUB_CRED

RUN dos2unix /app/set_variables.sh

EXPOSE 3306

CMD cd /app/db && \
  dolt checkout replication && \
  dolt reset --hard origin/replication && \
  /app/set_variables.sh && \
  rm -f /app/db/.dolt/sql-server.lock && \
  dolt sql-server --config /app/config.yaml 
