#!/bin/bash

if [ $(dolt remote | grep standby) ];
then
  dolt remote remove standby
fi

dolt remote add standby http://dd_standby:50000/db