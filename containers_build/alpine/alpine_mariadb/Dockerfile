FROM alpine:3.12

RUN apk add --upgrade --update --no-cache mariadb mariadb-client mariadb-server-utils pwgen gcc libc-dev  linux-headers && \
    rm -f /var/cache/apk/*

ADD files/run.sh /scripts/run.sh
RUN mkdir /docker-entrypoint-initdb.d && \
    mkdir /scripts/pre-exec.d && \
    mkdir /scripts/pre-init.d && \
    chmod -R 755 /scripts

ADD daemon/ /daemon

RUN chmod -R 755 /daemon

ADD config/ /config

RUN chmod -R 755 /config

EXPOSE 3306

VOLUME /var/lib/mysql

VOLUME /var/log/mysql/

VOLUME /config

ENTRYPOINT ["/scripts/run.sh"]

COPY files/docker-healthcheck /usr/local/bin/

HEALTHCHECK CMD ["docker-healthcheck"]