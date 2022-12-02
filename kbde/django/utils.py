from django.core import mail
from django.conf import settings


VERIFICATION_CHANNEL_EMAIL = "email"
VERIFICATION_CHANNEL_SMS = "sms"

VERIFICATION_CHANNELS = [
    VERIFICATION_CHANNEL_EMAIL,
    VERIFICATION_CHANNEL_SMS
]


def get_url_host_from_request(request):
    http_origin = request.META.get("HTTP_ORIGIN")
    http_host = request.META.get("HTTP_HOST")

    scheme = "http" if "dev" in settings.APP_NAME else "https"

    return http_origin or f"{scheme}://{http_host}"


def send_email(to_email_list,
              subject,
              text_message=None,
              html_message=None,
              from_email=None,
              cc_email_list=[],
              bcc_email_list=[],
              **kwargs):
    """
    Use this if you don't want to accidentally email your production users
    Ensures that a DEBUG_EMAIL setting exists
    Modifies outbound messages to be sent to the DEBUG_EMAIL when in DEBUG mode
    """
    to_email_list = list(to_email_list)
    cc_email_list = list(cc_email_list)
    bcc_email_list = list(bcc_email_list)

    # Make sure that the DEBUG_EMAIL setting is present
    assert hasattr(settings, "DEBUG_EMAIL"), (
        "must set `DEBUG_EMAIL` in settings"
    )
    
    # If in DEBUG mode, make sure that DEBUG_EMAIL is set to something
    if settings.DEBUG:
        assert settings.DEBUG_EMAIL, (
            "Must set `DEBUG_EMAIL` when in DEBUG mode"
        )

    assert text_message is not None or html_message is not None, (
        "must pass `text_message` or `html_message`"
    )

    message = mail.EmailMultiAlternatives(**kwargs)

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

    # Modify message if in DEBUG mode
    if settings.DEBUG_EMAIL:
        message.to = [settings.DEBUG_EMAIL]

        if cc_email_list:
            message.cc = message.to

        if bcc_email_list:
            message.bcc = message.to

    message.send()

    return message


def send_verification_message(to, channel):
    """
    Uses the Twilio verification API to send a verification code through a certain channel
    https://www.twilio.com/verify/api
    """
    assert channel in VERIFICATION_CHANNELS, f"{channel} is not a valid verification channel"

    from twilio import rest as twilio_rest

    client = twilio_rest.Client(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN,
    )

    verification = client.verify.services(
        settings.TWILIO_VERIFICATION_SERVICE_SID,
    ).verifications.create(
        to=to,
        channel=channel,
    )

    return verification

def verify_verification(to, code):
    """
    Checks a verification code against the Twilio verificaton API
    """
    from twilio import rest as twilio_rest

    client = twilio_rest.Client(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN,
    )

    verificaton_check = client.verify.services(
        settings.TWILIO_VERIFICATION_SERVICE_SID,
    ).verification_checks.create(
        to=to,
        code=code,
    )

    return verificaton_check

def send_email_verification(email):
    return send_verification_message(
        get_debugged_email(email),
        VERIFICATION_CHANNEL_EMAIL
    )

def verify_email_verification(email, code):
    return verify_verification(
        get_debugged_email(email),
        code
    )

def send_sms_verification(phone_number):
    return send_verification_message(
        get_debugged_phone_number(phone_number),
        VERIFICATION_CHANNEL_SMS
    )

def verify_sms_verification(phone_number, code):
    return verify_verification(
        get_debugged_phone_number(phone_number),
        code
    )

def send_sms(to_phone_number, message, from_phone_number=None):
    """
    Sends SMS wit a "debugged_phone_number"
    """
    from twilio import rest as twilio_rest

    client = twilio_rest.Client(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN,
    )

    to_phone_number = get_debugged_phone_number(to_phone_number)

    from_phone_number = (
        from_phone_number or
        getattr(settings, "DEFAULT_SMS_FROM_PHONE_NUMBER", None)
    )

    assert from_phone_number, (
        "You must either pass `from_phone_number` to this function or set "
        "settings.DEFAULT_SMS_FROM_PHONE_NUMBER"
    )

    message = client.messages.create(
        from_=from_phone_number,
        body=message,
        to=to_phone_number,
    )

    return message

def get_debugged_value(value, setting_name):
    """
    Takes a value
    Returns the value or the debug value from the settings
    """
    assert isinstance(value, str), f"`value` must be a string {value}"

    assert hasattr(settings, setting_name), (
        f"must set `{setting_name}` in settings"
    )

    # If in DEBUG mode, make sure that DEBUG_PHONE_NUMBER is set to something
    if settings.DEBUG:
        assert getattr(settings, setting_name, None), (
            f"Must set `{setting_name}` when in DEBUG mode"
        )

    debug_value = getattr(settings, setting_name)

    if debug_value:
        assert isinstance(debug_value, str), (
           f"`settings.{setting_name}` must be a string"
        )
        value = debug_value

    return value

def get_debugged_email(email):
    return get_debugged_value(email, "DEBUG_EMAIL")

def get_debugged_phone_number(phone_number):
    return get_debugged_value(str(phone_number), "DEBUG_PHONE_NUMBER")


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
        assert not member_list[0].startswith("@"), (
            "usernames should not include `@`"
        )

    # Make sure that labels to not include the # at the beginning
    if label_list:
        assert not label_list[0].startswith("#"), (
            "labels should not include `#`"
        )

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


def get_value_from_object(obj, key):
    """
    Tries to get a value from an object's getter method "get_{key}()".

    If there is no getter function of that name, then try to get the value from
    the object's attribute of the name "key".

    If there is no attribute named "key", then try to address the object like a
    dictionary.
    """
    getter_function = getattr(obj, f"get_{key}", None)

    if getter_function is not None:
        return getter_function()

    if hasattr(obj, key):
        return getattr(obj, key)

    return obj[key]
