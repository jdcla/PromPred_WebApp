from flask import current_app, render_template
from flask_mail import Message
from . import mail, celery


@celery.task(serializer='pickle')
def send_async_email(msg):
    mail.send(msg)

def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['PROMPRED_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
            sender=app.config['PROMPRED_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    print(msg)
    send_async_email.delay(msg)

