import tempfile
import subprocess
import os
import ssl
import time
import logging
from imapclient import IMAPClient

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
    messages = []
    try:
        messages = mail.search(['UNSEEN'])
    except Exception as e:
        logging.error(f"Failed to search mailbox: {e}")

    if not messages:
        logging.info("No new unread mail.")
        return

    for msg_id in messages:
        try:
            logging.info(f"Processing message {msg_id}")

            response = mail.fetch([msg_id], ["RFC822"])

            if msg_id not in response:
                continue

            raw_email = response[msg_id][b'RFC822']

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

            mail.add_flags(msg_id, [b"\\Seen"])

            logging.info(f"Successfully processed {msg_id}")

        except Exception as e:
            logging.exception(
                f"Failed processing message {msg_id}: {e}"
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

            unverified_context = ssl._create_unverified_context()

            mail = IMAPClient(
                IMAP_SERVER,
                port=IMAP_PORT,
                ssl=True,
                ssl_context=unverified_context,
                timeout=100,
            )

            mail.login(MAIL_USERNAME, MAIL_PASSWORD)
            mail.select_folder(MAILBOX)

            logging.info("Connected to IMAP server")

            # Process preexisting mail.
            process_unread(mail)

            while True:
                logging.info("Waiting for mail in IDLE")
                mail.idle()
                idle = True

                try:
                    responses = mail.idle_check(timeout=300)

                    if responses:
                        logging.info(f"New mail event detected: {responses}") 
                        
                        mail.idle_done()
                        idle = False
                        process_unread(mail)
                        
                        break
                
                finally:
                    if idle:
                        try:
                            mail.idle_done()
                        except Exception:
                            pass


        except Exception as e:
            logging.exception(
                f"Connection error: {e}"
            )
            time.sleep(30)


if __name__ == "__main__":
    main()
