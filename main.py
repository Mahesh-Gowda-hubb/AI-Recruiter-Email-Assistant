"""
AI Recruiter Email Assistant

"""
from gmail.gmail_service import GmailService


def main():
    """
    Entry point of the application.
    """

    gmail_service = GmailService()

    service = gmail_service.authenticate()

    print("✅ Gmail Authentication Successful!")

    messages = gmail_service.read_messages()

    print(f"Number of messages retrieved: {len(messages)}")
    email_records = []

    for message in messages:

        full_message = gmail_service.get_message(message["id"])

        payload = full_message["payload"]

        headers = payload["headers"]

        subject = gmail_service.get_header(headers, "Subject")
        sender = gmail_service.get_header(headers, "From")
        recipient = gmail_service.get_header(headers, "To")
        date = gmail_service.get_header(headers, "Date")

        body = gmail_service.get_body(payload)

        email_record = {
            "subject": subject,
            "sender": sender,
            "recipient": recipient,
            "date": date,
            "body": body
        }

        email_records.append(email_record)

    print(f"Processed {len(email_records)} emails")

    for email in email_records:

        print("-" * 60)
        print("Subject:", email["subject"])
        print("From:", email["sender"])
        print("Date:", email["date"])

    return service

if __name__ == "__main__":
    main()