import imaplib
import email
from email.header import decode_header
import re
from bs4 import BeautifulSoup

# IMAP credentials change to yours
imap_server = "imap.gmail.com"
email_user = "x@gmail.com"
email_pass = "xxx xxxx xxxxr"

# connecting to the IMAP server


def connect_to_email():
    try:
        imap = imaplib.IMAP4_SSL(imap_server)
        imap.login(email_user, email_pass)
        print("Connection successful!")
        return imap
    except Exception as e:
        print(f"Error connecting to email: {e}")
        return None

# cleaning the  HTML content


def clean_html(html):
    """Strip HTML tags, extract text, remove excessive blank lines, and filter irrelevant content."""
    soup = BeautifulSoup(html, "html.parser")
    # extracting the  text from HTML
    text = soup.get_text()

    # cleaning excessive blank lines and strip leading/trailing spaces
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # filtering out irrelevant lines
    filtered_lines = [
        line for line in lines if not any(keyword in line.lower() for keyword in [
            "publicidad", "síguenos en rrss", "haga click aquí", "pulse aquí"
        ])
    ]

    return "\n".join(filtered_lines)

# fetching and parseing emails


def fetch_emails(imap):
    try:
        # selecting the Inbox
        imap.select("inbox")
        # serching all emails
        status, messages = imap.search(None, "ALL")
        email_ids = messages[0].split()

        if not email_ids:
            print("No emails found.")
            return

        print(f"Found {len(email_ids)} emails. Fetching the latest...")

        # Fetch the latest email
        latest_email_id = email_ids[-1]
        status, msg_data = imap.fetch(latest_email_id, "(RFC822)")

        for response in msg_data:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(response[1])

                # Parse email metadata
                subject = decode_header(msg["Subject"])[0][0]
                if isinstance(subject, bytes):
                    try:
                        # Default UTF-8
                        subject = subject.decode()
                    except UnicodeDecodeError:
                        subject = subject.decode(
                            'iso-8859-1')
                sender = msg.get("From")
                print(f"Subject: {subject}")
                print(f"From: {sender}")

                # Parse email body
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            try:
                                body = part.get_payload(
                                    decode=True).decode()
                                print(f"Plain Text Body: {body}")
                                extract_data(body)
                            except UnicodeDecodeError:
                                body = part.get_payload(decode=True).decode(
                                    'iso-8859-1')
                                print(f"Plain Text Body: {body}")
                                extract_data(body)
                        elif part.get_content_type() == "text/html":
                            html_body = part.get_payload(decode=True).decode()
                            plain_text = clean_html(html_body)
                            print(f"HTML to Text: {plain_text}")
                            extract_data(plain_text)
                else:
                    content_type = msg.get_content_type()
                    body = msg.get_payload(decode=True).decode()
                    if content_type == "text/html":
                        plain_text = clean_html(body)
                        print(f"HTML to Text: {plain_text}")
                        extract_data(plain_text)
                    else:
                        print(f"Plain Text Body: {body}")
                        extract_data(body)

    except Exception as e:
        print(f"Error fetching email: {e}")

# Example: Extract specific data from email body


def extract_data(body):
    # Example: Extract order number
    order_match = re.search(r"Order Number: (\d+)", body)
    if order_match:
        print(f"Extracted Order Number: {order_match.group(1)}")

    # Example: Extract dates
    date_match = re.search(r"Date: (\d{4}-\d{2}-\d{2})", body)
    if date_match:
        print(f"Extracted Date: {date_match.group(1)}")


# Main script
imap = connect_to_email()
if imap:
    fetch_emails(imap)
    imap.logout()
