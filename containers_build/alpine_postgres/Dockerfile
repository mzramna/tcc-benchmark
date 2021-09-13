FROM alpine:latest

ENV PGDATA /var/lib/postgresql/data

#RUN echo "@edge http://nl.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories && \
#    apk update && \
RUN apk add su-exec wget tzdata libpq postgresql-client postgresql postgresql-contrib && \
    mkdir /docker-entrypoint-initdb.d && \
    rm -rf /var/cache/apk/*

VOLUME /var/lib/postgresql/data

ENV PGDATA /var/lib/postgresql/data
ENV LANG en_US.utf8

RUN mkdir /run/postgresql/ && chown -R postgres:postgres /var/lib/postgresql/data && chown -R postgres:postgres /run/postgresql/

COPY files/docker-entrypoint.sh /

ENTRYPOINT ["/docker-entrypoint.sh"]

EXPOSE 5432
CMD ["postgres"]
