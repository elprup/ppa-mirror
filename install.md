# install guide

## initial python runtime (virtualenv if you like)
```bash
apt-get install -y liblzma-dev

pip install -r req.txt

```

## init mirror in master

modify config.json, add your config

```
python -m ppa-mirror.mirror
```

## initial nginx settings in master

```
upstream upstream_deb {
    server 127.0.0.1:5000;
}

server {
    server_name [hostname];
    root /home/www/project_root;

    location / {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_set_header X-NginX-Proxy true;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_max_temp_file_size 0;
        proxy_pass http://upstream_deb/;
        proxy_redirect off;
        proxy_read_timeout 240s;
    }
}
```
## modify /etc/host in slaves

## add apt entry
special notice: trusted is necessary

```
deb [trusted=yes] http://[hostname]/ubuntu/ main/
```

## run master server
```
export FLASK_APP=server.py; flask run
```

## run apt update in slaves
```
sudo apt-get update
```
make sure there's no errorr

## run apt-get install

```
sudo apt-get install
```