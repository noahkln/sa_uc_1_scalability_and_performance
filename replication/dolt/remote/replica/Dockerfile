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

RUN cd /home && dolt clone noahkln/sa_1_scalability_and_performance db
COPY ./remote/replica/config.yaml /home/db/config.yaml
COPY ./remote/replica/set_variables.sh /home/db/set_variables.sh
COPY ./creds.jwk /home/db/creds.jwk
RUN dolt creds import /home/db/creds.jwk && dolt creds use 61qam4knj9ds4ohar7b4vuhr2nifloe27lhq8lequn9douj33ocg

# Configure dolt
RUN dolt config --global --add user.email "hartwig.noah@gmail.com"
RUN dolt config --global --add user.name "noahkln"

EXPOSE 3306

CMD cd /home/db && \
  dolt checkout replication && \
  ./set_variables.sh && \
  rm -f .dolt/sql-server.lock && \
  dolt sql-server --config ./config.yaml
