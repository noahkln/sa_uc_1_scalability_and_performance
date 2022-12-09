#!/bin/bash

if [ $(dolt remote | grep standby_1) ];
then
  dolt remote remove standby_1
fi


if [ $(dolt remote | grep standby_2) ];
then
  dolt remote remove standby_2
fi


if [ $(dolt remote | grep standby_3) ];
then
  dolt remote remove standby_3
fi

dolt remote add standby_1 http://standby_1:50000/db
dolt remote add standby_2 http://standby_2:50000/db
dolt remote add standby_3 http://standby_3:50000/db