# Reverse Proxy with apache2
Some notes taken while configuring a HTTPS reverse proxy for streamlit with apache2.
Access only possible after authentication.

Some notes:
```
cl@ubuntu:/etc/apache2/sites-available$ sudo a2enmod proxy
Enabling module proxy.
To activate the new configuration, you need to run:
  systemctl restart apache2
cl@ubuntu:/etc/apache2/sites-available$ sudo a2enmod proxy_http
Considering dependency proxy for proxy_http:
Module proxy already enabled
Enabling module proxy_http.
To activate the new configuration, you need to run:
  systemctl restart apache2
cl@ubuntu:/etc/apache2/sites-available$
```

To see a summary of the virtual host configuration:
```
sudo apache2ctl -t -D DUMP_VHOSTS
```
