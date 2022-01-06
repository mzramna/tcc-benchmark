FROM debian:latest

RUN apt update && \
    apt install mariadb mariadb-client mariadb-server-utils pwgen -y && \
    wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add - && \
    apt install apt-transport-https -y && \
    echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-7.x.list && \
    apt update && sudo apt-get install metricbeat && \
    mkdir /docker-entrypoint-initdb.d && \
    apt clean

ADD files/run.sh /scripts/run.sh

RUN mkdir /docker-entrypoint-initdb.d && \
    mkdir /scripts/pre-exec.d && \
    mkdir /scripts/pre-init.d && \
    chmod -R 755 /scripts

EXPOSE 3306

VOLUME /var/lib/mysql
VOLUME /var/log/mysql/

ENTRYPOINT ["/scripts/run.sh"]
