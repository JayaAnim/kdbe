from django.core import mail
from django.conf import settings


def send_email(to_email_list,
               from_email,
               subject,
               body,
               attachment_list=[],
               bcc_email_list=[]):
    message = mail.EmailMessage()
    message.content_subtype = "html"

    message.to = to_email_list
    message.from_email = from_email
    message.subject = subject
    message.body = body
    message.attachments = attachment_list
    message.bcc = bcc_email_list

    if settings.DEBUG_EMAIL:
        message.to = [settings.DEBUG_EMAIL]
        if bcc_email_list:
            message.bcc = message.to

    message.send()

    return message
