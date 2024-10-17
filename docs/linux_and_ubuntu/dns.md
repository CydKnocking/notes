Permanently change DNS:

1. Open resolved.conf by `vim /etc/systemd/resolved.conf`

2. Set
   ```
   # Seperate by a space
   DNS=8.8.8.8 114.114.115.115
   FallbackDNS=8.8.4.4
   ```

3. Restart systemd-resolved by `systemctl restart systemd-resolved`

4. Set auto-start by `systemctl enable systemd-resolved`

Temporarily change DNS:

- Change the file by `vim /etc/resolv.conf` and add DNS by 
  ```
  nameserver 8.8.8.8
  nameserver 8.8.4.4
  ```

