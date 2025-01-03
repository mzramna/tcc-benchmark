#!/bin/bash
read -sp 'senha root: ' senha
# read -sp 'senha root opi-pc01: ' senha
echo ""
build="--build"
force="--force-recreate"
sshpass -p "$senha"  rsync -airup --progress ~/tcc-benchmark/ mzramna@192.168.0.10:~/tcc-benchmark/ --exclude=".env" --exclude="dados.json" --exclude="meuvenv"
sshpass -p  "$senha"  ssh root@192.168.0.10 "cd /home/mzramna/tcc-benchmark/containers_build/alpine_no_daemon && sudo docker-compose stop"
sshpass -p  "$senha"  ssh root@192.168.0.10  "sudo rm -rf /media/docker_mount/testes_tcc/*/data/* /media/docker_mount/testes_tcc/*/data/*"
sshpass -p  "$senha"  ssh root@192.168.0.10 "cd /home/mzramna/tcc-benchmark/containers_build/alpine_no_daemon && sudo docker-compose up $build $force -d --no-start"

#read -sp 'senha root server-testes: ' senha
#echo ""
sshpass -p "$senha"  rsync -airup --progress ~/tcc-benchmark/ mzramna@192.168.0.20:~/tcc-benchmark/ --exclude=".env" --exclude="dados.json" --exclude="meuvenv"
sshpass -p  "$senha"  ssh root@192.168.0.20 "cd /home/mzramna/tcc-benchmark/containers_build/alpine_no_daemon && sudo  docker-compose stop"
sshpass -p  "$senha"  ssh root@192.168.0.20  "sudo rm -rf /media/docker_mount/testes_tcc/*/data/* /media/docker_mount/testes_tcc/*/data/*"
sshpass -p  "$senha"  ssh root@192.168.0.20 "cd /home/mzramna/tcc-benchmark/containers_build/alpine_no_daemon && sudo docker-compose up $build $force -d --no-start"