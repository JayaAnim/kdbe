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

        # From email
        from_email = self.get_from_email()

        # Recipients
        to_email_list = self.get_to_email_list()
        cc_email_list = self.get_cc_email_list()
        bcc_email_list = self.get_bcc_email_list()

        # Attachments
        attachment_list = self.get_attachment_list()

        utils.send_email(to_email_list,
                         subject,
                         text_message=text_message,
                         html_message=html_message,
                         from_email=from_email,
                         cc_email_list=cc_email_list,
                         bcc_email_list=bcc_email_list,
                         attachment_list=attachment_list)


    def get_to_email_list(self):
        """
        Returns a list of email addresses to which this form will send emails
        """
        assert self.to_email_list is not None, "must define `self.to_email_list` as a list of emails"
        assert isinstance(to_email_list, (list, tuple)), "`self.to_email_list` must be an iterable"

        return self.to_email_list

    def get_cc_email_list(self):
        """
        Returns a list of cc email addresses
        """
        assert isinstance(self.cc_email_list, (list, tuple)), ("`self.cc_email_list` must be an "
                                                               "iterable")

        return self.cc_email_list

    def get_bcc_email_list(self):
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

    def get_attachment_list(self):
        """
        Returns an iterable of attachments
        See attachments: https://docs.djangoproject.com/en/2.2/topics/email/#emailmessage-objects
        """
        return []


class SendToTrelloForm:
    """
    A form which when submitted will create a Trello card via email
    Presents the same interface as `EmailForm`
    """
    board_email = None
    title = None
    member_list = []
    label_list = []
    attachment_list = []
    
    def send_email(self):
        """
        Gathers information from the form fields to produce:
            - board_email
            - title
            - description
            - members
            - labels
        Uses the Trello "email to board" feature
        """

        board_email = self.get_board_email()
        title = self.get_title()
        description = self.get_description()

        assert isinstance(description, str), "self.get_description must return a string"

        member_list = self.get_member_list()
        label_list = self.get_label_list()
        attachment_list = self.get_attachment_list()

        utils.send_to_trello(board_email,
                             title,
                             description,
                             member_list=member_list,
                             label_list=label_list,
                             attachment_list=attachment_list)

    def get_board_email(self):
        assert self.board_email is not None, "must define self.board_email"
        
        return self.board_email

    def get_title(self):
        assert self.title is not None, "must define self.title"

        return self.title

    def get_description(self):
        """
        Returns the card description as a string. Can be Markdown formatted.
        Can return empty string if there is no description
        """
        raise NotImplementedError

    def get_member_list(self):
        """
        Returns a list of members to be added to the card
        By default, this returns self.member_list
        Note: these members should not include `@`
        """
        assert isinstance(self.member_list, (list, tuple)), "self.member_list must be an iterable"

        return self.member_list

    def get_label_list(self):
        """
        Returns a list of labels to be added to the card
        By default, this returns self.label_list
        Not: these labels should not include `#`
        """
        assert isinstance(self.label_list, (list, tuple)), "self.label_list must be an iterable"

        return self.label_list

    def get_attachment_list(self):
        """
        Returns an iterable of attachments
        See attachments: https://docs.djangoproject.com/en/2.2/topics/email/#emailmessage-objects
        """
        return []
