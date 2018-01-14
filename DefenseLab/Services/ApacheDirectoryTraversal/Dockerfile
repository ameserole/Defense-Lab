FROM ubuntu:latest

RUN apt update
RUN apt install -y apache2 apache2-doc apache2-utils


env APACHE_RUN_USER    www-data
env APACHE_RUN_GROUP   www-data
env APACHE_PID_FILE    /var/run/apache2.pid
env APACHE_RUN_DIR     /var/run/apache2
env APACHE_LOCK_DIR    /var/lock/apache2
env APACHE_LOG_DIR     /var/log/apache2

EXPOSE 80

COPY ./entry.sh ./entry.sh
ENTRYPOINT ["./entry.sh"]
