FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get -y install apt-utils nano
RUN apt-get -y upgrade && apt-get -y install curl apache2 apache2-dev libapache2-mod-wsgi-py3 git gfortran libgeos-dev build-essential qt5-default rsync libproj-dev wget git postgresql-client
RUN update-rc.d apache2 disable
RUN git clone -b master --single-branch https://github.com/awst-austria/qa4sm.git /tmp/qa4sm-git
RUN bash /tmp/qa4sm-git/docker/webapp/install.sh
COPY entrypoint.sh /usr/bin/entrypoint.sh
COPY entrypoint.sh /usr/local/bin/
RUN ln -s usr/local/bin/entrypoint.sh /entrypoint.sh # backwards compat
ENTRYPOINT ["entrypoint.sh"]
