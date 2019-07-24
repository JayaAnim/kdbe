from .. import utils


class EmailForm:
    """
    A form which when submitted will send an email
    """
    subject = None
    to_email_list = None
    cc_email_list = []
    bcc_email_list = []
    from_email = None

    def send_email(self):
        """
        Gathers the information from the form fields to produce:
            - Subject
            - Body
            - Attachements
            - Recipients
        """
        # Subject
        subject = self.get_subject()

        # Message
        text_message = self.get_text_message()
        html_message = self.get_html_message()

        # Attachments
        attachment_list = self.get_attachments()

        # Recipients
        to_email_list = self.get_to_emails()
        cc_email_list = self.get_cc_emails()
        bcc_email_list = self.get_bcc_emails()

        from_email = self.get_from_email()

        utils.send_email(to_email_list,
                         subject,
                         text_message=text_message,
                         html_message=html_message,
                         from_email=from_email,
                         cc_email_list=cc_email_list,
                         bcc_email_list=bcc_email_list,
                         attachment_list=attachment_list)


    def get_to_emails(self):
        """
        Returns a list of email addresses to which this form will send emails
        """
        assert self.to_email_list is not None, "must define `self.to_email_list` as a list of emails"
        assert isinstance(to_email_list, (list, tuple)), "`self.to_email_list` must be an iterable"

        return self.to_email_list

    def get_cc_emails(self):
        """
        Returns a list of cc email addresses
        """
        assert isinstance(self.cc_email_list, (list, tuple)), ("`self.cc_email_list` must be an "
                                                               "iterable")

        return self.cc_email_list

    def get_bcc_emails(self):
        """
        Returns a list of bcc emails addresses
        """
        assert isinstance(self.bcc_email_list, (list, tuple)), ("`self.bcc_email_list` must be an "
                                                                "iterable")

        return self.bcc_email_list

    def get_from_email(self):
        """
        Returns the email from which this form sends emails
        If this returns None, the system default email address will be used
        """
        return self.from_email

    def get_subject(self):
        assert self.subject is not None, "must define `self.subject`"

        return self.subject

    def get_text_message(self):
        """
        Returns the email body as a string with no formatting
        Returns None if there is no text body
        """
        raise NotImplementedError

    def get_html_message(self):
        """
        Returns the email body as formatted HTML
        Returns None if there is no HTML body
        """
        raise NotImplementedError

    def get_attachments(self):
        """
        Returns an iterable of attachments
        See attachments: https://docs.djangoproject.com/en/2.2/topics/email/#emailmessage-objects
        """
        return []
