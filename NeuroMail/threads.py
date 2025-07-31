import threading


class EmailSendThread(threading.Thread):
    def __init__(
        self,
        emailMethod,
        subject,
        body,
        email,
        password,
        recipients,
        attachments,
        email_id,
    ) -> None:
        self.emailMethod = emailMethod
        self.subject = subject
        self.body = body
        self.email = email
        self.password = password
        self.recipients = recipients
        self.attachments = attachments
        self.email_id = email_id

        threading.Thread.__init__(self)

    def run(self) -> None:
        self.emailMethod(
            self.subject,
            self.body,
            self.email,
            self.password,
            self.recipients,
            self.attachments,
            self.email_id,
        )


class InboxRecieverThread(threading.Thread):
    def __init__(self, inboxMethod, mailbox, user) -> None:
        self.inboxMethod = inboxMethod
        self.mailbox = mailbox
        self.user = user

        threading.Thread.__init__(self)

    def run(self) -> None:
        self.inboxMethod(self.mailbox, self.user)
