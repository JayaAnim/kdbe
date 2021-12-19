FROM ubuntu:focal


ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1


WORKDIR /kbde

ADD . /kbde/

RUN bash -c 'cd .. && ./kbde/scripts/bootstrap.bash'
