#!/bin/bash

if [ ! $(dolt remote | grep origin) ];
then
  dolt remote add origin noahkln/sa_uc_1_replication
fi

dolt sql -q "set @@PERSIST.dolt_replicate_heads = 'replication';"
dolt sql -q "set @@PERSIST.dolt_read_replica_remote = 'origin';"
dolt sql -q "set @@PERSIST.dolt_skip_replication_errors = 1;"