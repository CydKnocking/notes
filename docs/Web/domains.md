# Domains

Buy and manage domains on [namesilo](https://www.namesilo.com/). After buying a domain, go to "manage domains" in namesilo:

1. Add "A" records and set Github ip:
   
   ```
   185.199.108.153
   185.199.109.153
   185.199.110.153
   185.199.111.153
   ```

2. Add "CNAME" records, set sub-domain, and set address to `username.github.io`

3. Go to "Github repository - Settings - Pages - Custom domain". Input your domain and click "save".
   
   NOTICE: It may take minutes to hours for the DNS server to refresh.
   
   After DNS checked successfully, do not forget to click "Enforce HTTPS" box.






