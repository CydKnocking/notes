## Open SSH as server

- Install SSH server
  ```
  sudo apt update
  sudo apt install openssh-serve
  sudo systemctl status ssh  # Check ssh running status
  ```
  If SSH is running, you will see `Active: active (running)` in the output information.
- Allow SSH to go through firewall
  - Check if the firewall is activated: `sudo ufw status`. If inactivated, you will see `Status: inactivate`.
  - Allow SSH to go through firewall: `sudo ufw allow OpenSSH`
  - Activate firewall (if inactivated): `sudo ufw enable`
  - Check firewall status: `sudo ufw status`, and you will see information like `Status: active`...
- Check IP of the server. You can use anyone of the following commands:
  ```
  ifconfig
  ip addr show | grep inet
  hostname -I
  ```

## Connect the server by SSH from a client

```
ssh <username>@<server_ip_address>
```

Note that `<server_ip_address>` can be either ipv4 or ipv6.
