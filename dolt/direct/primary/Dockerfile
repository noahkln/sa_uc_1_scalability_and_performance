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
COPY ./direct/primary/config.yaml /home/db/config.yaml
COPY ./direct/primary/add_remotes.sh /home/db/add_remotes.sh

EXPOSE 3306

CMD cd /home/db && \
  ./add_remotes.sh && \
  dolt sql-server --config ./config.yaml
