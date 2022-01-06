FROM golang:latest

ENV GOPATH=/go
# ENV CC=arm-linux-gnueabi-gcc

ENV BEATS=filebeat,metricbeat
ENV BEATS_VERSION=7.16

COPY ./build.sh /build.sh
RUN [ "mkdir", "-p", "/go" ]
RUN [ "mkdir", "/build" ]

CMD "/build.sh"
