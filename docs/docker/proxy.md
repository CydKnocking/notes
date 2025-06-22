## Setting proxy for docker

Create a configuration file for docker:
```
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo vim /etc/systemd/system/docker.service.d/http-proxy.conf
```
and input
```
[Service]
Environment="HTTP_PROXY=http://proxy.example.com:80"
Environment="HTTPS_PROXY=https://proxy.example.com:443"
```
Then reload the config file and restart docker
```
sudo systemctl daemon-reload
sudo systemctl restart docker
```