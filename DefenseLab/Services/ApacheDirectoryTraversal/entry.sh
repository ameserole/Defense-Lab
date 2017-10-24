#!/bin/sh
echo "Hello Word" > /var/www/html/index.html
cp $FILELOC/apache2.conf /etc/apache2/apache2.conf;
service apache2 restart;
apache2 -D FOREGROUND
