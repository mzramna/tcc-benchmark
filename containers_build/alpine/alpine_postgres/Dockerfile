FROM alpine:3.12

ENV PGDATA /var/lib/postgresql/data

#RUN echo "@edge http://nl.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories && \
#    apk update && \
RUN apk add --upgrade --update su-exec wget tzdata libpq postgresql-client postgresql postgresql-contrib gcc libc-dev linux-headers && \
    mkdir /docker-entrypoint-initdb.d && \
    rm -rf /var/cache/apk/*

VOLUME /var/lib/postgresql/data

VOLUME /var/log/postgresql

ENV PGDATA /var/lib/postgresql/data
ENV LANG en_US.utf8

RUN mkdir -p /run/postgresql/ && mkdir -p /var/lib/postgresql/data && chown -R postgres:postgres /var/lib/postgresql/data && chown -R postgres:postgres /run/postgresql/

ADD daemon/ /daemon

RUN chmod -R 755 /daemon

ADD config/ /config

RUN chmod -R 755 /config

COPY files/docker-entrypoint.sh /

VOLUME /config


ENTRYPOINT ["/docker-entrypoint.sh"]

EXPOSE 5432
CMD ["postgres", "-c", "log_statement=all"]

COPY files/docker-healthcheck /usr/local/bin/

HEALTHCHECK CMD ["docker-healthcheck"]