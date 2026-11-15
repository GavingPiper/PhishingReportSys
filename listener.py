import imaplib
import tempfile
import subprocess
import os
import time
import logging

#-------------------------------------------
# Secrets
with open("/run/secrets/mail_user.txt") as f:
    MAIL_USERNAME = f.read().strip()

with open("/run/secrets/mail_password.txt") as f:
    MAIL_PASSWORD = f.read().strip()

# Server Information
with open("/run/secrets/imap_server.txt") as f:
    IMAP_SERVER = f.read().strip()
with open("/run/secrets/imap_port.txt") as f:
    IMAP_PORT = int(f.read().strip())
with open("/run/secrets/mailbox.txt") as f:
    MAILBOX = f.read().strip()

PARSER_PATH = "./parse_mail.py"
#-------------------------------------------


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)


def process_unread(mail):
    """
    Find and process all unread emails.
    """

    status, messages = mail.search(None, "UNSEEN")

    if status != "OK":
        logging.error("Failed to search mailbox")
        return

    for msg_id in messages[0].split():
        try:
            logging.info(f"Processing message {msg_id.decode()}")

            status, data = mail.fetch(msg_id, "(RFC822)")

            if status != "OK":
                continue

            raw_email = data[0][1]

            with tempfile.NamedTemporaryFile(
                suffix=".eml",
                delete=False
            ) as tmpfile:
                tmpfile.write(raw_email)
                eml_path = tmpfile.name

            subprocess.run(
                ["python3", PARSER_PATH, eml_path],
                check=True
            )

            mail.store(msg_id, "+FLAGS", "\\Seen")

            logging.info(f"Successfully processed {msg_id.decode()}")

        except Exception as e:
            logging.exception(
                f"Failed processing message {msg_id.decode()}: {e}"
            )

        finally:
            if "eml_path" in locals():
                try:
                    os.remove(eml_path)
                except Exception:
                    pass


def main():
    while True:
        try:
            logging.info("Connecting to IMAP server")

            mail = imaplib.IMAP4_SSL(
                IMAP_SERVER,
                IMAP_PORT,
                timeout=1
            )

            mail.login(MAIL_USERNAME, MAIL_PASSWORD)
            mail.select(MAILBOX)

            logging.info("Connected to IMAP server")

            # Process preexisting mail.
            process_unread(mail)

            while True:
                mail.idle()
                logging.info("Waiting for mail")

                try:
                    responses = mail.idle_check(timeout=300)

                    if responses:
                        process_unread(mail)
                        break # Start a new IDLE session.

                finally:
                    mail.idle_done()

        except Exception as e:
            logging.exception(
                f"Connection error: {e}"
            )
            time.sleep(30)


if __name__ == "__main__":
    main()
