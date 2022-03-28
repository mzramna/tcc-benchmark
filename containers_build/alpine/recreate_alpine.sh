#!/bin/bash
read -sp 'senha root: ' senha
sshpass -p "$senha"  rsync -airup --progress ~/tcc-benchmark/containers_build/ mzramna@192.168.0.100:/media/hd_servidor500gb/codigos/tcc-benchmark/containers_build
sshpass -p  "$senha"  ssh root@192.168.0.100 "cd /media/hd_servidor500gb/codigos/tcc-benchmark/containers_build/alpine && docker-compose stop"
sshpass -p  "$senha"  ssh root@192.168.0.100  " rm -rf /media/hd_servidor500gb/config/testes_tcc/*/*/* "
sshpass -p  "$senha"  ssh root@192.168.0.100  " rsync -airup /media/hd_servidor500gb/codigos/tcc-benchmark/containers_build/alpine/alpine_mariadb/config/dados.json /media/mergerfs_raid0/config/testes_tcc/mariadb/config/ &&  rsync -airup /media/hd_servidor500gb/codigos/tcc-benchmark/containers_build/alpine/alpine_postgres/config/dados.json /media/mergerfs_raid0/config/testes_tcc/postgres/config/ && chown mzramna -R /media/mergerfs_raid0/config/testes_tcc/"
sshpass -p  "$senha"  ssh root@192.168.0.100 "cd /media/hd_servidor500gb/codigos/tcc-benchmark/containers_build/alpine && docker-compose up --build --force-recreate -d"