FROM ubuntu:18.04

RUN mkdir /opt/mycroft
COPY . /opt/mycroft
CMD tail -f /dev/null
