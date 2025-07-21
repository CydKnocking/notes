在Ubuntu使用clash classic时，如果是有UI的界面，可以直接在浏览器中访问`clash.razord.top`来选择线路。

在没有UI界面的服务器上使用clash classic传统版时，可以在本地使用yacd（web控制面板）+转发的方式设置服务器上clash的路线。

1. 服务器上，clash的config.yaml文件中找到
   `external-controller: '127.0.0.1:9090'`这一行，如果没有则需要设置。如果是`0.0.0.0:9090`则有可能需要修改ip。
2. 服务器上，启动clash。
3. 本地，去`https://github.com/haishanh/yacd`下载release的tar.xz，解压。
4. 在本地，用ssh端口转发访问服务器
   `ssh -L 19090:localhost:9090 user@your-server`，
   此时，可以通过本地`19090`端口访问服务器的`9090`端口。
5. 本地，进入刚刚解压的yacd文件夹，用python打开本地服务器
   `python -m http.server 1234`
6. 本地，浏览器打开`localhost:1234`，设置clash API地址为`http://127.0.0.1:19090`即可。
