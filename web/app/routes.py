from app import app, db, queue_client,redis_connection
from datetime import datetime
from app.models import Attendee, Conference, Notification
from flask import render_template, session, request, redirect, url_for, flash, make_response, session
from azure.servicebus import Message
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import logging
import redis


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/Registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        attendee = Attendee()
        attendee.first_name = request.form['first_name']
        attendee.last_name = request.form['last_name']
        attendee.email = request.form['email']
        attendee.job_position = request.form['job_position']
        attendee.company = request.form['company']
        attendee.city = request.form['city']
        attendee.state = request.form['state']
        attendee.interests = request.form['interest']
        attendee.comments = request.form['message']
        attendee.conference_id = app.config.get('CONFERENCE_ID')

        try:
            db.session.add(attendee)
            db.session.commit()
            user_message = 'Thank you, {} {}, for registering!'.format(attendee.first_name, attendee.last_name)
            redis_connection.set('message',user_message)
            logging.info('A key message with {} is inserted into the redis cache'.format(user_message))
            return redirect('/Registration')
        except:
            logging.error('Error occured while saving your information')

    else:
        user_message = redis_connection.get('message')
        logging.info('Value for the key message is {}'.format(user_message))
        if user_message:
            redis_connection.delete('message')
            logging.info('Key message deleted from cache')
            return render_template('registration.html', message=user_message)
        else:
             return render_template('registration.html')

@app.route('/Attendees')
def attendees():
    attendees = Attendee.query.order_by(Attendee.submitted_date).all()
    return render_template('attendees.html', attendees=attendees)


@app.route('/Notifications')
def notifications():
    notifications = Notification.query.order_by(Notification.id).all()
    return render_template('notifications.html', notifications=notifications)

@app.route('/Notification', methods=['POST', 'GET'])
def notification():
    if request.method == 'POST':
        notification = Notification()
        notification.message = request.form['message']
        notification.subject = request.form['subject']
        notification.status = 'Notifications submitted'
        notification.submitted_date = datetime.utcnow()

        try:
            db.session.add(notification)
            db.session.commit()
            #notification.completed_date = datetime.utcnow()
            #notification.status = 'Notified {} attendees'.format(len(attendees))
            # TODO Call servicebus queue_client to enqueue notification ID
            notification_message = Message(str(notification.id))
            queue_sender = queue_client.get_sender()
            sender_response = queue_sender.send(notification_message)
            logging.info('queue_sender response :',sender_response)

            return redirect('/Notifications')
        except :
            logging.error('log unable to save notification')

    else:
        return render_template('notification.html')



def send_email(email, subject, body):
    if not app.config.get('SENDGRID_API_KEY'):
        message = Mail(
            from_email=app.config.get('ADMIN_EMAIL_ADDRESS'),
            to_emails=email,
            subject=subject,
            plain_text_content=body)

        sg = SendGridAPIClient(app.config.get('SENDGRID_API_KEY'))
        sg.send(message)
