## Cron service commands

```
sudo service cron status  # show service log
sudo service cron start   # start the service 
sudo service cron stop
sudo service cron restart
```

## Set a job in crontab

Make sure that cron service is running. If not, start it.

Use `crontab -e` to open the job list. Add your new job with a new line:

```
* * * * * [command]
# {minute} {hour} {day} {month} {day of week} {your command}
# Use '*' to stand for 'any'
# Example:
#     0 0 * * 0 conda activate ex_env; python main.py
# means run "conda activate ex_env; python main.py" at 00:00 on every Sunday.
```

After that, you can use `crontab -l` to see all the jobs set in the list. And use `sudo service cron status` to see the running log.
