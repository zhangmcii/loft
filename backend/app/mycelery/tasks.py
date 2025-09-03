from celery import shared_task
from flask import render_template
from flask_mail import Message

from .. import mail


@shared_task(ignore_result=False)
def send_email(to, subject, template, **kwargs):
    try:
        message = Message(subject=subject, recipients=[to])
        message.html = render_template(template, **kwargs)
        mail.send(message)
    except Exception as e:
        print(e)
        print("发送失败")
