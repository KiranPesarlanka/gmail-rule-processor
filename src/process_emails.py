import os
import json
import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from db_connector import DB
from gmail_client import GmailClient
from logging_conf import get_logger

logger = get_logger(__name__)

BASE_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
LABELS_URL = "https://gmail.googleapis.com/gmail/v1/users/me/labels"

def relative_datetime(value, unit):

    now = datetime.now()
    unit = unit.lower()

    if unit in ['day', 'days']:
        return now - timedelta(days=value)
    elif unit in ['hour', 'hours']:
        return now - timedelta(hours=value)
    elif unit in ['minute', 'minutes']:
        return now - timedelta(minutes=value)
    elif unit in ['second', 'seconds']:
        return now - timedelta(seconds=value)
    elif unit in ['month', 'months']:
        return now - relativedelta(months=value)
    elif unit in ['year', 'years']:
        return now - relativedelta(years=value)
    else:
        logger.error(f"Unsupported time unit: {unit}")
        raise ValueError(f"Unsupported time unit: {unit}")

def query_builder(rules):
    conditions_to_check = rules['conditions_to_check']
    conditions = rules['conditions']
    actions = rules['actions']

    coupler = 'AND' if conditions_to_check=="All" else "OR"
    
    query = "SELECT message_id FROM emails WHERE "

    for condition in conditions:
        if condition['field'].lower()=="from":
           field = "from_email"
        elif condition['field'].lower()=="to":
           field = "to"
        elif condition['field'].lower()=="subject":
           field = "subject"
        elif condition['field'].lower()=="received date/time":
           field = "received_at"
        else:
            #invalid field
            logger.error(f"Invaid field : {field}. Selection is available for From / To / Subject / Date Received ")
            break

        if condition['type'].lower()=="contains":
            query += f"{field} LIKE '%{condition['value']}%' {coupler} "
        elif condition['type'].lower()=="does not contain":
            query += f"{field} NOT LIKE '%{condition['value']}%' {coupler} "
        elif condition['type'].lower()=="equals":
            query += f"{field}='{condition['value']}' {coupler} "
        elif condition['type'].lower()=="does not equal":
            query += f"{field}!='{condition['value']}' {coupler} "
        elif condition['type'].lower()=="less than":
            new_value = relative_datetime(int(condition['value']), condition['unit'])
            query += f"{field}<'{new_value}' {coupler} "
        else:
            #invalid 
            logger.error(f"Invaid type : {condition['type']}.")
            break


    query = query.strip().strip(coupler)
    return query


def modify_message_labels(message_id: str, access_token: str, add_labels=None, remove_labels=None):
    """Generic Gmail message label modifier via Gmail REST API"""
    try:
        payload = {}
        if add_labels:
            payload["addLabelIds"] = add_labels
        if remove_labels:
            payload["removeLabelIds"] = remove_labels

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            f"{BASE_URL}/{message_id}/modify",
            headers=headers,
            json=payload
        )
        logger.info(f"modify_message_labels API is success. message_id={message_id}")
        return response
    except Exception as err:
        logger.error(f"modify_message_labels API got failed. Error: {err} , message_id={message_id}")
        pass

def update_email_label(message_id, access_token, label):
    """Moves a message to Inbox"""
    response = modify_message_labels(
        message_id=message_id,
        access_token=access_token,
        add_labels=[label],
    )
    if response.ok:
        logger.info(f"Successfully moved message to {label}!. message_id={message_id}")
    else:
        logger.error(f"Error moving message:  {response.status_code} {response.text} message_id={message_id}")


def mark_as_read(message_id, access_token):
    """Marks a message as read"""
    response = modify_message_labels(
        message_id=message_id,
        access_token=access_token,
        remove_labels=["UNREAD"]
    )
    if response.ok:
        logger.info(f"Message marked as read successfully!. message_id={message_id}")
    else:
        logger.error(f"Error marking message as read: {response.status_code} | {response.text} message_id={message_id}")

def get_available_labels(access_token):
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        response = requests.get(
            LABELS_URL,
            headers=headers,
        )
        
        resp = response.json()
        labels = {label['name'].lower(): label['id'] for label in resp['labels']}
        logger.info("Labels API is success")
        return labels
        
    except Exception as err:
        logger.error("Labels API got failed. Error: {err}")
        pass



def process_emails(creds_path, rules):
    try:
        db = DB()
        logger.info(f"Successfully established connection to DB")
        gc = GmailClient(creds_path)
        logger.info(f"GmailClient is ready to use")
        token = gc.creds.token
        query = query_builder(rules)
        email_ids = db.fetch_email_ids(query)
        logger.info(f"Emails matched for the condition : {len(email_ids)}")
        available_labels = get_available_labels(token)
        counter = 1
        for email_id in email_ids:
            for action in rules['actions']:
                if action['action']=="move message":
                    label = action['to mailbox']
                    if label.lower() not in available_labels:
                        raise Exception(f"Invalid Label: {label}")
                    label = available_labels[label.lower()]
                    update_email_label(email_id, token, label)
                elif action['action']=="mark as read":
                    mark_as_read(email_id, token)
                elif action['action']=="mark as unread":
                    update_email_label(email_id, token, "UNREAD")
            logger.info(f"Processing completed for {counter}/{len(email_ids)}")
            counter += 1
    except Exception as err:
        logger.error(f"Failed while running rules. Error : {str(err)}")
        pass

if __name__=="__main__":
    creds_path = "credentials.json"
    rules_file = "rule1.json"
    rules = json.load(open(rules_file))
    process_emails(creds_path, rules)
