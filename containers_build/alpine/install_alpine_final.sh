#!/bin/bash
read -sp 'senha root: ' senha
# read -sp 'senha root opi-pc01: ' senha
echo ""
build="--build"
force="--force-recreate"
start="-d "
#"--no-start"
sshpass -p "$senha"  rsync -airup --progress ~/tcc-benchmark/ mzramna@192.168.0.10:~/tcc-benchmark/ --exclude=".env" --exclude="dados.json" --exclude="meuvenv"
sshpass -p  "$senha"  ssh root@192.168.0.10 "cd /home/mzramna/tcc-benchmark/containers_build/alpine && sudo docker-compose stop"
sshpass -p  "$senha"  ssh root@192.168.0.10 "cd /home/mzramna/tcc-benchmark/containers_build/alpine && rsync -airup ./alpine/alpine_postgres/config /media/docker_mount/testes_tcc/postgres/config && rsync -airup ./alpine/alpine_mariadb/config /media/docker_mount/testes_tcc/mariadb/config"
sshpass -p  "$senha"  ssh root@192.168.0.10  "sudo rm -rf /media/docker_mount/testes_tcc/*/data /media/docker_mount/testes_tcc/*/logs"
sshpass -p  "$senha"  ssh root@192.168.0.10  "sudo mkdir /media/docker_mount/testes_tcc/postgres/data/ /media/docker_mount/testes_tcc/postgres/logs/ /media/docker_mount/testes_tcc/mariadb/data/ /media/docker_mount/testes_tcc/mariadb/logs/ "
echo  "cd /home/mzramna/tcc-benchmark/containers_build/alpine && sudo docker-compose up $start $build $force"
sshpass -p  "$senha"  ssh root@192.168.0.10 "cd /home/mzramna/tcc-benchmark/containers_build/alpine && sudo docker-compose up $start $build $force"

#read -sp 'senha root server-testes: ' senha
#echo ""
sshpass -p "$senha"  rsync -airup --progress ~/tcc-benchmark/ mzramna@192.168.0.20:~/tcc-benchmark/ --exclude=".env" --exclude="dados.json" --exclude="meuvenv"
sshpass -p  "$senha"  ssh root@192.168.0.20 "cd /home/mzramna/tcc-benchmark/containers_build/alpine && sudo  docker-compose stop"
sshpass -p  "$senha"  ssh root@192.168.0.20 "cd /home/mzramna/tcc-benchmark/containers_build/alpine && rsync -airup ./alpine/alpine_postgres/config /media/docker_mount/testes_tcc/postgres/config && rsync -airup ./alpine/alpine_mariadb/config /media/docker_mount/testes_tcc/mariadb/config"
sshpass -p  "$senha"  ssh root@192.168.0.20  "sudo rm -rf /media/docker_mount/testes_tcc/*/data /media/docker_mount/testes_tcc/*/logs"
sshpass -p  "$senha"  ssh root@192.168.0.20  "sudo mkdir /media/docker_mount/testes_tcc/postgres/data/ /media/docker_mount/testes_tcc/postgres/logs/ /media/docker_mount/testes_tcc/mariadb/data/ /media/docker_mount/testes_tcc/mariadb/logs/ "
echo "cd /home/mzramna/tcc-benchmark/containers_build/alpine && sudo docker-compose up $start $build $force "
sshpass -p  "$senha"  ssh root@192.168.0.20 "cd /home/mzramna/tcc-benchmark/containers_build/alpine && sudo docker-compose up $start $build $force "