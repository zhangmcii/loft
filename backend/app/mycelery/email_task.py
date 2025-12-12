import logging

from celery import shared_task
from flask import render_template
from flask_mail import Message

from .. import mail


# @shared_task(ignore_result=False)
# def auth_email(to, subject, template, **kwargs):
#     try:
#         message = Message(subject=subject, recipients=[to])
#         message.html = render_template(template, **kwargs)
#         mail.send(message)
#     except Exception as e:
#         logging.error(f"发送失败:{e}")


@shared_task(ignore_result=False)
def message_email(to, subject, template, **kwargs):
    try:
        message = Message(subject=subject, recipients=[to])
        message.html = render_template(template, **kwargs)
        mail.send(message)
    except Exception as e:
        logging.error(f"发送失败:{e}")
