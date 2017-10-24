FROM ubuntu:latest

env DEBIAN_FRONTEND="noninteractive"
RUN apt-get -y update && apt-get install -y apache2 apache2-doc apache2-utils mysql-server php libapache2-mod-php php-mcrypt php-mysql 
COPY apache2.conf /etc/apache2/
COPY index.html /var/www/html/
COPY db_gen.sh /db_gen.sh
COPY entry.sh /entry.sh

env APACHE_RUN_USER    www-data
env APACHE_RUN_GROUP   www-data
env APACHE_PID_FILE    /var/run/apache2.pid
env APACHE_RUN_DIR     /var/run/apache2
env APACHE_LOCK_DIR    /var/lock/apache2
env APACHE_LOG_DIR     /var/log/apache2

EXPOSE 80

RUN chmod 755 /db_gen.sh

ENTRYPOINT ["./entry.sh"]
