FROM alpine:3.12

ENV LANG en_US.utf8
ENV PGDATA /var/lib/postgresql/data

#RUN echo "@edge http://nl.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories && \
#    apk update && \
RUN apk add --upgrade --update su-exec wget tzdata libpq postgresql-client postgresql postgresql-contrib && \
    mkdir /docker-entrypoint-initdb.d && \
    rm -rf /var/cache/apk/* && mkdir /scripts

VOLUME /var/lib/postgresql/data

VOLUME /var/log/postgresql

RUN mkdir -p /run/postgresql/ && mkdir -p /var/lib/postgresql/data && chown -R postgres:postgres /var/lib/postgresql/data && chown -R postgres:postgres /run/postgresql/

COPY files/docker-entrypoint.sh /

ENTRYPOINT ["/docker-entrypoint.sh"]

COPY files/docker-healthcheck /usr/local/bin/

HEALTHCHECK CMD ["docker-healthcheck"]

EXPOSE 5432

CMD ["postgres", "-c", "log_statement=all"]