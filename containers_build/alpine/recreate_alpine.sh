#!/bin/bash
rsync -airup --progress ~/tcc-benchmark/containers_build/ mzramna@192.168.0.100:/media/hd_servidor500gb/codigos/tcc-benchmark/containers_build
ssh root@192.168.0.100 "cd /media/hd_servidor500gb/codigos/tcc-benchmark/containers_build/alpine && docker-compose stop"
ssh root@192.168.0.100 " rm -rf /media/hd_servidor500gb/config/testes_tcc/*/*/*"
ssh root@192.168.0.100 "cd /media/hd_servidor500gb/codigos/tcc-benchmark/containers_build/alpine && docker-compose up --build --force-recreate -d"