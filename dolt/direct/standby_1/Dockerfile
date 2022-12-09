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
COPY ./direct/standby_1/config.yaml /home/db/config.yaml

EXPOSE 3306

CMD cd /home/db && dolt sql-server --config ./config.yaml
