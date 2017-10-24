#!/bin/sh

cp $FILELOC/login.php /var/www/html/login.php

./db_gen.sh
service apache2 restart;
apache2 -D FOREGROUND
