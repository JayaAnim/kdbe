from django.core import mail
from django.conf import settings


def send_email(to_email_list,
               subject,
               text_message=None,
               html_message=None,
               from_email=None,
               cc_email_list=[],
               bcc_email_list=[],
               attachment_list=[]):
    """
    Use this if you don't want to accidentally email your production users
    Ensures that a DEBUG_EMAIL setting exists
    Modifies outbound messages to be sent to the DEBUG_EMAIL when in DEBUG mode
    """

    # Make sure that the DEBUG_EMAIL setting is present
    assert hasattr(settings, "DEBUG_EMAIL"), "must set `DEBUG_EMAIL` in settings"
    
    # If in DEBUG mode, make sure that DEBUG_EMAIL is set to something
    if settings.DEBUG:
        assert settings.DEBUG_EMAIL, "Must set `DEBUG_EMAIL` when in DEBUG mode"

    assert text_message is not None or html_message is not None, ("must pass `text_message` or "
                                                                  "`html_message`")

    message = mail.EmailMultiAlternatives()

    # Text message exits
    if text_message:
        message.body = text_message

    # Text message and html message
    if text_message and html_message:
        # Add an alternative content'
        message.attach_alternative(html_message, "text/html")
        
    # HTML message only
    if not text_message and html_message:
        # Change the email content_subtype to just html
        message.content_subtype = "html"
        message.body = html_message

    message.to = to_email_list
    message.subject = subject
    message.from_email = from_email or message.from_email
    message.cc = cc_email_list
    message.bcc = bcc_email_list
    message.attachments = attachment_list

    # Modify message if in DEBUG mode
    if settings.DEBUG_EMAIL:
        message.to = [settings.DEBUG_EMAIL]

        if cc_email_list:
            message.cc = message.to

        if bcc_email_list:
            message.bcc = message.to

    message.send()

    return message


def send_to_trello(board_email,
                   title,
                   description,
                   member_list=[],
                   label_list=[],
                   attachment_list=[]):
    """
    Creates a new Trello card via email
    Refer to https://help.trello.com/article/809-creating-cards-by-email
    """
    # Make sure that users do not include the @ at the beginning
    if member_list:
        assert not member_list[0].startswith("@"), "usernames should not include `@`"

    # Make sure that labels to not include the # at the beginning
    if label_list:
        assert not label_list[0].startswith("#"), "labels should not include `#`"

    # Create member and label lists
    member_list = ["@{}".format(username) for username in member_list]
    member_list = " ".join(member_list)

    label_list = ["#{}".format(label_name) for label_name in label_list]
    label_list = " ".join(label_list)

    # Create the subject line
    subject_contents = [title, member_list, label_list]
    subject_contents = [i for i in subject_contents if i]
    subject = " ".join(subject_contents)

    send_email([board_email],
               subject,
               text_message=description,
               attachment_list=attachment_list)
