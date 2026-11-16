import mailparser
import mysql.connector
import sys
import logging

def parse_email(eml_file_path):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s $(levelname)s %(message)s") 

    mail = mailparser.parse_from_file(eml_file_path)

    # obtain necessary components
    mail_attachment = mail.attachments
    mail_body = mail.body
    mail_date = mail.date
    mail_subj = mail.subject
    mail_sender = mail.from_[0][1]
    mail_recip = mail.to[0][1]
    # the parser does not consistently put the reciever domain first, might have to cut from reciever addr instead
    mail_client = mail_sender.split('@')[1]

    """
        # testing parsing
        print("Attachment: ")
        print(mail_attachment)
        print("Body: ")
        print(mail_body)
        print("Date: ")
        print(mail_date)
        print("Subject: ")
        print(mail_subj)
        print("Sender: ")
        print(mail_sender)
        print("Client: ")
        print(mail_client)
        print("To: ")
        print(mail_recip) 
    """

    # insert into db
    f = open("/run/secrets/db_root_password.txt")
    pw = f.read()

    # pw = "password"
    mail_db = mysql.connector.connect(host="db-container", password=pw, user="root", database="phishing_db")
    add_mail = ("INSERT INTO Emails (sender, recipient, body, clientID)"
                "SELECT %s, %s, %s, clientID FROM Clients WHERE email = %s")
    vals = (mail_sender, mail_recip, mail_body, mail_client)

    for i, val in enumerate(vals):
        print(f"vals[{i}] -> Value: {val}")

    mycursor = mail_db.cursor()
    mycursor.execute(add_mail, vals)
    

    mail_db.commit()
    logging.info("Inserted parsed email.")

if __name__ == "__main__":
    eml_file_path = sys.argv[1]
    parse_email(eml_file_path)
