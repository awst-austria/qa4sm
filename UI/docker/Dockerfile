FROM httpd:alpine

MAINTAINER You <you@somedomain.com>

# Remove any files that may be in the public htdocs directory already.
RUN rm -r /usr/local/apache2/htdocs/*

# Copy all the files from the docker build context into the public htdocs of the apache container.
COPY ./ui /usr/local/apache2/htdocs/ui

# Enable the rewrite module in apache2.
RUN sed -i \
  's/#LoadModule rewrite_module modules\/mod_rewrite.so/LoadModule rewrite_module modules\/mod_rewrite.so/g' \
  /usr/local/apache2/conf/httpd.conf

# Append to the published directory, that we want to rewrite any request that is not an actual file
# to the index.html page.
RUN sed -i '/<Directory "\/usr\/local\/apache2\/htdocs\/ui">/a### Rewrite rule was written from the Dockerfile when building the image ###\n\
    DirectoryIndex index.html\n\
    RewriteEngine on\n\
    RewriteCond %{REQUEST_FILENAME} -s [OR]\n\
    RewriteCond %{REQUEST_FILENAME} -d\n\
    RewriteRule ^.*$ - [NC,L]\n\
    RewriteRule ^(.*) /ui/index.html [NC,L]\n' \
  /usr/local/apache2/conf/httpd.conf

# Comment out the default config that handles requests to /.htaccess and /.ht* with a special error message,
# Angular will handle all routing
RUN sed -i '/<Files "\.ht\*">/,/<\/Files>/c# This was commented out from the Dockerfile\n# <Files ".ht*">\n#     Require all denied\n# <\/Files>' \
  /usr/local/apache2/conf/httpd.conf

# TODO: Replace in httpd.conf
# ServerAdmin you@example.com
# #ServerName www.example.com:80

# Change owner of the publicly available files to root user and daemon group. Httpd threads run as daemon.
RUN chown -R root:daemon \
  /usr/local/apache2/htdocs/*

# Ensure that the files can only be read, even by the httpd server.
RUN chmod -R 440 \
  /usr/local/apache2/htdocs/*

# Ensure for all the directories created, that the files within them can be read. We need the
# execution access privilege on the directory for this. Dynamically apply this to all directories
# at least one level into the served root. (-mindepth 1, otherwise the served directory itself
# would be included - no need for that.
RUN find /usr/local/apache2/htdocs/ -mindepth 1 -type d -exec chmod +x {} \;

# Install curl, just for healthchecking, without using local cache for the package lists
RUN apk --no-cache add curl

# Define a healthcheck that tests the root URL of the site
HEALTHCHECK --interval=5s --timeout=3s CMD curl --fail http://localhost:80/ || exit 1

