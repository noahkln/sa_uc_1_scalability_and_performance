#!/bin/bash

if [ ! $(dolt remote | grep origin) ];
then
  dolt remote add origin https://doltremoteapi.dolthub.com/noahkln/sa_uc_1_replication
fi

dolt sql -q "set @@PERSIST.dolt_replicate_to_remote = 'origin';"
dolt sql -q "set @@PERSIST.dolt_replicate_heads = 'replication';"
dolt sql -q "set @@PERSIST.dolt_transaction_commit = 1;"
dolt sql -q "set @@PERSIST.dolt_skip_replication_errors = 1;"