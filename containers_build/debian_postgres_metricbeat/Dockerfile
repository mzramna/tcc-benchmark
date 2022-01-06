FROM alpine:latest

#RUN echo "@edge http://nl.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories && \
#    apk update && \
RUN apt update && apt install sudo wget tzdata libpq postgresql-client postgresql postgresql-contrib -y && \
    wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add - && \
    apt install apt-transport-https -y && \
    echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-7.x.list && \
    apt update && sudo apt-get install metricbeat && \
    mkdir /docker-entrypoint-initdb.d && \
    apt clean

VOLUME /var/lib/postgresql/data
VOLUME /var/log/postgresql

ENV PGDATA /var/lib/postgresql/data
ENV LANG en_US.utf8

RUN mkdir /run/postgresql/ && chown -R postgres:postgres /var/lib/postgresql/data && chown -R postgres:postgres /run/postgresql/

COPY files/docker-entrypoint.sh /

ENTRYPOINT ["/docker-entrypoint.sh"]

EXPOSE 5432
CMD ["postgres"]
