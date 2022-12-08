import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime,timezone
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def main(msg: func.ServiceBusMessage):
    try:
        notification_id = int(msg.get_body().decode('utf-8'))
        logging.info('Python ServiceBus queue trigger processed message: %s',notification_id)
        #Get connection to database
        database_connection = psycopg2.connect(host=os.environ.get("DB_HOST"),database=os.environ.get("DB_NAME"), user=os.environ.get("DB_USER"), password=os.environ.get("DB_PASSWORD" ))
        logging.info('Database connection created succesfully')
        # TODO: Get notification message and subject from database using the notification_id
        cursor = database_connection.cursor()
        notification_select_query = "select message,subject from notification where id = {0};".format(str(notification_id))
        cursor.execute(notification_select_query)
        notification_record = cursor.fetchone()
        notification_message = notification_record[0]
        notification_subject = notification_record[1]
        logging.info(f"Notification message : {notification_message} Notification subject :{notification_subject}")
        # TODO: Get attendees email and name
        attendees_select_query = "select email,first_name,last_name from attendee;"
        cursor.execute(attendees_select_query)
        attendees_list = cursor.fetchall()
        logging.info("Total attendees "+str(len(attendees_list)))
        emails_sent_count = 0
        # TODO: Loop through each attendee and send an email with a personalized subject
        for attendee in attendees_list:
            # TODO : send an email to attendee
            attendee_email = attendee[0]
            attendee_first_name = attendee[1]
            attendee_last_name = attendee[2]
            logging.info(f"First name : {attendee_first_name} Last Name : {attendee_last_name} Email : {attendee_email}")
            email_subject='{}: {}'.format(attendee_first_name, notification_subject)
            send_email(attendee_email,email_subject,notification_message)
            emails_sent_count +=  1
        logging.info("Total {} emails sent ".format(str(emails_sent_count)))
        #Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        notification_completed_date = datetime.now(timezone.utc)
        notification_status = 'Notified {0} attendees'.format(str(emails_sent_count))
        notification_update_query = """update notification set status = %s, completed_date = %s where id = %s;"""
        cursor.execute(notification_update_query,(notification_status,notification_completed_date,str(notification_id)))
        database_connection.commit()
        logging.info('Updated the status of the notification and completed date in the notifications table')

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        # TODO: Close connection
        if database_connection:
            cursor.close()
            database_connection.close()
            logging.info('Database connection closed successfully')

def send_email(email, subject, body):
    """
    A helper method to send the email to attendee using sendgrid api
    """
    try:
        if not os.environ.get('SendGrid_API_KEY'):
            message = Mail(from_email=os.environ.get('ADMIN_EMAIL_ADDRESS'),
                        to_emails=email,
                        subject=subject,
                        plain_text_content=body)
            sg = SendGridAPIClient(os.environ.get('SendGrid_API_KEY'))
            sg.send(message)
            logging.info("Notification sent to {0}".format(email))
    except Exception as e:
                print(e.message)
