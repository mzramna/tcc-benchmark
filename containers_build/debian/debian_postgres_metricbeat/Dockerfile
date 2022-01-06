FROM postgres:bullseye

#RUN echo "@edge http://nl.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories && \
#    apk update && \
RUN apt update && apt install sudo wget tzdata libpq5 gnupg2  -y 
RUN wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
RUN apt install apt-transport-https -y
RUN echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-7.x.list
RUN apt update && sudo apt-get install metricbeat && \
    apt clean

VOLUME /var/lib/postgresql/data
VOLUME /var/log/postgresql

ENV PGDATA /var/lib/postgresql/data
ENV LANG en_US.utf8
ENV PGDATA=/var/lib/postgresql/data

#RUN mkdir /run/postgresql/ && chown -R postgres:postgres /var/lib/postgresql/data && chown -R postgres:postgres /run/postgresql/

COPY files/docker-entrypoint.sh docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]

EXPOSE 5432

CMD ["postgres"]
