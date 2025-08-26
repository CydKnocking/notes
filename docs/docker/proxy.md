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

## Setting proxy for `docker build`

You can set proxy by `--build-arg` and do not forget to use `--network host` when use proxy on localhost. 不然docker会将localhost指向容器本身。
```
sudo docker build --build-arg HTTP_PROXY=http://localhost:xxxx --build-arg HTTPS_PROXY=http://localhost:xxxx --network host -t ...
```