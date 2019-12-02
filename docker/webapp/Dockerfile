FROM ubuntu:18.04
RUN apt-get update && apt-get -y install apt-utils nano
RUN apt-get -y upgrade && apt-get -y install curl apache2 apache2-dev libapache2-mod-wsgi-py3 git gfortran libgeos-dev build-essential qt5-default rsync libproj-dev wget git postgresql-client
RUN update-rc.d apache2 disable
RUN git clone -b dockerize --single-branch https://github.com/awst-austria/qa4sm.git /tmp/qa4sm-git
COPY install.sh /tmp/qa4sm-git/docker/qa4sm-webapp/install.sh
COPY settings.py /tmp/qa4sm-git/docker/qa4sm-webapp/settings.py
COPY settings_conf.py /tmp/qa4sm-git/docker/qa4sm-webapp/settings_conf.py
COPY entrypoint.sh /usr/bin/entrypoint.sh
RUN bash /tmp/qa4sm-git/docker/qa4sm-webapp/install.sh
COPY entrypoint.sh /usr/local/bin/
RUN ln -s usr/local/bin/entrypoint.sh /entrypoint.sh # backwards compat
ENTRYPOINT ["entrypoint.sh"]
