FROM ubuntu:18.04
RUN apt-get update && apt-get -y upgrade && apt-get -y install apt-utils nano
RUN apt-get -y install curl gfortran libgeos-dev build-essential qt5-default rsync libproj-dev wget git
RUN git clone -b dockerize --single-branch https://github.com/awst-austria/qa4sm.git /tmp/qa4sm-git
COPY install.sh /tmp/qa4sm-git/docker/qa4sm-webapp/install.sh
COPY settings.py /tmp/qa4sm-git/docker/qa4sm-webapp/settings.py
COPY settings_conf.py /tmp/qa4sm-git/docker/qa4sm-webapp/settings_conf.py
RUN bash /tmp/qa4sm-git/docker/qa4sm-webapp/install.sh
COPY entrypoint.sh /usr/local/bin/
RUN ln -s usr/local/bin/entrypoint.sh /entrypoint.sh # backwards compat
ENTRYPOINT ["entrypoint.sh"]
