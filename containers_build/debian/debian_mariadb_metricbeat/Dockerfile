FROM mariadb:latest

RUN apt update && \
    apt install pwgen wget sudo gnupg2 -y 
RUN wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add - 
RUN apt install apt-transport-https -y 
RUN echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-7.x.list 
RUN apt update && sudo apt-get install metricbeat && \
    apt clean
RUN 
#RUN mkdir /docker-entrypoint-initdb.d &&   mkdir /scripts/pre-exec.d &&   mkdir /scripts/pre-init.d &&   chmod -R 755 /scripts

EXPOSE 3306

VOLUME /var/lib/mysql
VOLUME /var/log/mysql/

COPY files/docker-entrypoint.sh docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["mariadbd"]
