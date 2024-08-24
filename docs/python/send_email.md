You can send email from 163 mailbox. Refer to the codes below.

```
import smtplib
from email.mime.text import MIMEText

mail_host = "smtp.163.com"
mail_user = "username"     # Your 163 mailbox username
mail_pass = "password"     # Your 163 mailbox password
sender = "username@163.com"     # Full 163 mailbox address

receivers = ["mail1@mail1", "mail2@mail2"]

for _r in receivers:
    # Messages you wanna send
    # You can send English, Chinese as well as emoji.
    message = MIMEText("Python 邮件发送测试...\n你要是收到了就吱一声。👩🤝👨", "plain", "utf-8")

    message["Subject"] = "Python 邮件测试"    # Title
    message["From"] = sender
    message["To"] = _r

    # Send email and catch exceptions
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host, 25)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, _r, message.as_string())
        smtpObj.quit()
        print("邮件发送成功")
    except smtplib.SMTPException as e:
        print("Error: 无法发送邮件", e)
```