FROM ubuntu:18.04
RUN apt-get update && apt-get -y upgrade && apt-get -y install curl apache2 apache2-dev libapache2-mod-wsgi-py3 git gfortran libgeos-dev build-essential qt5-default rsync libproj-dev wget git postgresql-client
RUN update-rc.d apache2 disable
RUN git clone -b dockerize --single-branch https://github.com/awst-austria/qa4sm.git /tmp/qa4sm-git
RUN bash /tmp/qa4sm-git/docker/qa4sm-webapp/install.sh