
FROM ubuntu:22.04

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
COPY ./direct/primary/config.yaml /app/config.yaml
COPY ./direct/primary/add_remotes.sh /app/add_remotes.sh

RUN dos2unix /app/add_remotes.sh

EXPOSE 3306

CMD cd /app/db && \
  /app/add_remotes.sh && \
  dolt sql-server --config /app/config.yaml
