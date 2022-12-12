
FROM ubuntu:22.04

ARG MAIL
ARG USER

# Install curl
RUN apt-get update && apt-get install -y \
  curl

# Install dolt
RUN curl -L https://github.com/dolthub/dolt/releases/download/v0.50.14/install.sh | bash

# Test dolt
RUN dolt version

RUN mkdir -p /app/db

RUN dolt config --global --add user.email $MAIL
RUN dolt config --global --add user.name $USER

RUN cd /app/db && dolt init

EXPOSE 3306

CMD cd /app/db && dolt sql-server --host=0.0.0.0 --user=sa_uc_1 --password=sa_uc_1_password
