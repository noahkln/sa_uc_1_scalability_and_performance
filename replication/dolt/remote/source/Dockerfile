ARG DOLT_USER
ARG DOLT_PWD

FROM ubuntu:22.04

ENV DOLT_USER=$DOLT_USER
ENV DOLT_PWD=$DOLT_PWD

# Install curl
RUN apt-get update && apt-get install -y \
  curl

# Install dolt
RUN curl -L https://github.com/dolthub/dolt/releases/latest/download/install.sh | bash

# Test dolt
RUN dolt version

# Configure dolt
RUN dolt config --global --add user.email "hartwig.noah@gmail.com"
RUN dolt config --global --add user.name "noahkln"

RUN mkdir /home/db
COPY ./db/.dolt/config.json /home/db/.dolt/config.json
COPY ./db/.dolt/repo_state.json /home/db/.dolt/repo_state.json
COPY ./remote/source/config.yaml /home/db/config.yaml
COPY ./remote/source/set_variables.sh /home/db/set_variables.sh
COPY ./creds.jwk /home/db/creds.jwk
RUN dolt creds import /home/db/creds.jwk && dolt creds use 61qam4knj9ds4ohar7b4vuhr2nifloe27lhq8lequn9douj33ocg

EXPOSE 3306

CMD cd /home/db && \
  dolt checkout replication && \
  ./set_variables.sh && \
  rm -f .dolt/sql-server.lock && \
  dolt sql-server --config ./config.yaml 
