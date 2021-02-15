FROM httpd:2.4
RUN rm /usr/local/apache2/conf/httpd.conf
COPY ./httpd.conf /usr/local/apache2/conf/httpd.conf
COPY ./ui /usr/local/apache2/htdocs/ui
COPY ./.htaccess /usr/local/apache2/htdocs/ui/
