#!/bin/bash

if [ ! $(dolt remote | grep origin) ];
then
  dolt remote add origin https://doltremoteapi.dolthub.com/noahkln/sa_1_scalability_and_performance
fi

dolt sql -q "set @@PERSIST.dolt_replicate_heads = 'replication';"
dolt sql -q "set @@PERSIST.dolt_read_replica_remote = 'origin';"
dolt sql -q "set @@PERSIST.dolt_skip_replication_errors = 1;"