# bernard

Provision free subdomains easily.

## Deployment Instructions

Choose whether to use SQLite or MySQL as your database driver.

### MySQL

Create a file named `.env` and fill in the following variables. Replace the values to suit your setup.

```bash
MYSQL_PASSWORD="password"
PORT="5000"
ZONE_PATH="/etc/bind/bernard"
```

MySQL data will be stored in a Docker volume named `bernard-mysql`.

### SQLite

Create a file named `.env` and fill in the following variables. Replace the values to suit your setup.

```bash
DATABASE_PATH="/var/www/bernard/database"
DATABASE_TYPE="sqlite"
PORT="5000"
ZONE_PATH="/etc/bind/bernard"
```

## Using the scripts from docker-compose

You can run the scripts from docker-compose. Replace `docker-compose.prod.mysql.yml` with `docker-compose.prod.sqlite.yml` if you are using SQLite.

```bash
docker-compose -f docker-compose.prod.mysql.yml exec app ".venv/bin/python" "scripts/create_zone.py"
docker-compose -f docker-compose.prod.mysql.yml exec app ".venv/bin/python" "scripts/ban_ip.py"
docker-compose -f docker-compose.prod.mysql.yml exec app ".venv/bin/python" "scripts/ban_record.py"
docker-compose -f docker-compose.prod.mysql.yml exec app ".venv/bin/python" "scripts/sync.py"
```

## Updating serial number when the zone changes

You can use a simple bash script that cronjob executes every minute to increment the serial for the zone when the zone changes.

```bash
#!/bin/bash

BERNARD_ZONE="/etc/bind/bernard/<FQDN>.zone"
BERNARD_ZONE_SUM="/tmp/<FQDN>.md5sum"
ZONE="<FQDN>"
ZONE_PATH="/etc/bind/zones/db.<FQDN>"

previous_sum=$(<$BERNARD_ZONE_SUM)
new_sum=$(md5sum $BERNARD_ZONE)

refresh() {
    serial=$(rndc zonestatus $ZONE | grep serial | cut -c9-)
    new_serial=$((serial+1))

    sed -i "s/.*; Serial.*/$new_serial ; Serial/" $ZONE_PATH
    rndc reload
}

[ "$previous_sum" != "$new_sum" ] && refresh
echo "$new_sum" > $BERNARD_ZONE_SUM
```

Put this in a file and create a cronjob like this.

```cron
* * * * * /path/to/script/bernard.sh >/dev/null 2>&1
```

## Contributors ✨

Copyright (C) 2020-2021, Vilhelm Prytz, <vilhelm@prytznet.se>, et al.
