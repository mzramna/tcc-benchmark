FROM alpine:latest

RUN apk add --upgrade --update --no-cache mariadb mariadb-client mariadb-server-utils pwgen && \
    rm -f /var/cache/apk/* && mkdir /scripts

ADD files/run.sh /run.sh
RUN mkdir /docker-entrypoint-initdb.d && \
    mkdir /scripts/pre-exec.d && \
    mkdir /scripts/pre-init.d && \
    chmod -R 755 /scripts

EXPOSE 3306

VOLUME /var/lib/mysql

VOLUME /var/log/mysql/

ENTRYPOINT ["/run.sh"]

COPY files/docker-healthcheck /usr/local/bin/

HEALTHCHECK CMD ["docker-healthcheck"]