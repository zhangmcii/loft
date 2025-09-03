from threading import Thread

from flask import current_app, jsonify, render_template
from flask_mail import Message

from . import mail


def send_t(app, msg):
    with app.app_context():
        mail.send(msg)


# 发送一个html 多线程
def send_email(to, subject, template, **kwargs):
    print("to", to)
    app = current_app._get_current_object()
    try:
        message = Message(subject=subject, recipients=[to])
        message.html = render_template("code_email.html", **kwargs)
        t_mail = Thread(
            target=send_t,
            args=(
                app,
                message,
            ),
            kwargs={},
        )
        t_mail.start()
        return jsonify(data="", msg="success")
    except Exception as e:
        print(e)
        print("发送失败")
        return jsonify(data="", msg="fail")
