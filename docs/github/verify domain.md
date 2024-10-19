
- Go to Github user Settings - Code, planning, and automation - Pages
- Click "Add a domain"
- A TXT record `<_github-xxx>.yourwebsite.com` and a value `<TXT_value>` will be generated. Please copy then and goto your hostname manager (next step).
- Add a DNS TXT record (use Namesilo as an example):
  - Go to "Domain Manager"
  - Create a `TXT/SPF` record:
    - Paste `<_github-xxx>` to "HOSTNAME" box
    - Paste `<TXT_value>` to "TEXT" box
    - Click "SUBMIT"
- Go back to Github "Add a verified domain" page. Wait for minutes to hours for the DNS configuration changes.
- Click "Verify".