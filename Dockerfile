FROM ubuntu:focal


WORKDIR /kbde

ADD . /kbde/

RUN bash -c 'cd .. && ./kbde/scripts/bootstrap.bash'
