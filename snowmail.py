#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Snowmail ServiceNow Email Helper

Usage:
    snowmail.py
    snowmail.py create (--name <NAME> --email <EMAIL> --phone <PHONE> --subject <SUBJECT> --body <BODY>)
    snowmail.py update (--incident <INC#> --name <NAME> --email <EMAIL> --phone <PHONE> --subject <SUBJECT> --body <BODY>)
    snowmail.py status (--incident <INC#> --name <NAME> --email <EMAIL> --phone <PHONE>)

Arguments:
    crete           Create new incident.
    update          Update an existing incident.
    status          Check the status of an existing incident.

Options:
    -h --help       Show this screen.
    --version       Show version.
    --incident      Incident number.
    --name          Sender full name.
    --email         Sender Email.
    --phone         Phone Number.
    --subject       Email Subject.
    --body          Email body.
'''

# Libs & Modules
import _config as cfg
import configparser
import pysnow
import re
import os
import sys
import textwrap
import json
import logging.handlers

from loguru import logger
from pygments import highlight, lexers, formatters
from configparser import ExtendedInterpolation
from docopt import docopt
from SMTPEmail import SMTP
from deep_translator import (GoogleTranslator,
                             MicrosoftTranslator,
                             PonsTranslator,
                             LingueeTranslator,
                             MyMemoryTranslator,
                             YandexTranslator,
                             DeepL,
                             QCRI,
                             single_detection,
                             batch_detection)


# Read config paramaters from config.ini file using configparser

# Prepare the config file reference
CONFIG = configparser.ConfigParser(interpolation=ExtendedInterpolation())
CONFIG.read(cfg.__config_file__)

# App Settings
RUN_MODE = CONFIG['App Settings']['run_mode']
LOG_LEVEL = CONFIG['App Settings']['log_level']

# Syslog
SYSLOG_HOST = CONFIG['Syslog']['host']
SYSLOG_PORT = CONFIG['Syslog']['port']

# SMTP Settings
AWS_SES_USER = CONFIG['SMTP']['aws_ses_user']
SMTP_SERVER = CONFIG['SMTP']['smtp_server']
SMTP_USER = CONFIG['SMTP']['smtp_user']
SMTP_PASSWORD = CONFIG['SMTP']['smtp_password']
SMTP_NAME = CONFIG['SMTP']['smtp_name']
SMTP_SENDER = CONFIG['SMTP']['smtp_sender']

# ServiceNow API Details
SNOW_DEV_INSTANCE = CONFIG['SNOW API']['dev_instance']
SNOW_PROD_INSTANCE = CONFIG['SNOW API']['prod_instance']
SNOW_API_USER = CONFIG['SNOW API']['user']
SNOW_API_PASSWORD = CONFIG['SNOW API']['password']
# Tables
INCIDENT = CONFIG['SNOW Tables']['incident']

# Incident Details
COMPANY = CONFIG['SNOW Incident Details']['company']
CALLER = CONFIG['SNOW Incident Details']['caller_id']
OPENED_BY = CONFIG['SNOW Incident Details']['opened_by']
CONTACT_TYPE = CONFIG['SNOW Incident Details']['contact_type']
CATEGORY = CONFIG['SNOW Incident Details']['category']
AE = CONFIG['SNOW Incident Details']['u_account_executive']

# Translation Settings
TRANSLATION_ENGINE = CONFIG['Translator Settings']['translator']
TO_LANG = CONFIG['Translator Settings']['to_lang']
# Detect Language
DETECT_LANG_API_KEY = CONFIG['Detect Language']['api_key']
# DeepL
# DEEPL_API_KEY = CONFIG['DeepL']['api_key']


@logger.catch
def main():
    """Things start here."""
    # Set log file
    set_log_level(LOG_LEVEL)
    arguments = docopt(
        __doc__, version=cfg.__description__ + " - " + cfg.__version__)
    logger.trace(arguments)
    if arguments['create']:
        # BUG: Comment out the following line and added get_body function as a workaround for multi-line variables which are unable to be passed from the batch file wrapper
        # create(arguments['<NAME>'], arguments['<EMAIL>'], arguments['<PHONE>'], arguments['<SUBJECT>'], arguments['<BODY>'])
        EMAIL_BODY = get_body()
        create(arguments['<NAME>'], arguments['<EMAIL>'],
               arguments['<PHONE>'], arguments['<SUBJECT>'], EMAIL_BODY)
    elif arguments['update']:
        # BUG: Comment out the following line and added get_body function as a workaround for multi-line variables which are unable to be passed from the batch file wrapper
        # update(arguments['<INC#>'], arguments['<NAME>'], arguments['<EMAIL>'], arguments['<PHONE>'], arguments['<SUBJECT>'], arguments['<BODY>'])
        EMAIL_BODY = get_body()
        update(arguments['<INC#>'], arguments['<NAME>'], arguments['<EMAIL>'],
               arguments['<PHONE>'], arguments['<SUBJECT>'], EMAIL_BODY)
    elif arguments['status']:
        status(arguments['<INC#>'], arguments['<NAME>'],
               arguments['<EMAIL>'], arguments['<PHONE>'])
    else:
        print(arguments)
        exit("{0} is not a command. \
          See 'snowmail.py --help'.".format(arguments['<command>']))
    exit(0)


@logger.catch
def get_body():
    # BUG: Added this function to read body from body.tmp as a workaround for windows bug where python env needs to be setup and requires a batch file wrapper to do so
    # TODO: Work on a fix for the batch file wrapper and refactor and cleanup code
    # Open text file in read mode
    text_file = open(cfg.__body_temp_file__, "r")
    # Read whole file to a string
    data = text_file.read()
    # Close file
    text_file.close()
    # Remove empty lines and print output
    data = os.linesep.join([s for s in data.splitlines() if s])
    logger.info(data)
    # Remove temp file
    os.remove(cfg.__body_temp_file__)
    return(data)


@logger.catch
def create(sender_name, sender_email, sender_phone, short_description, long_description):
    email_check(sender_email)
    sender_lang = detect_lang(short_description, long_description)
    logger.debug(sender_lang)
    english_translation = native2english(*sender_lang)
    incident = create_inc(sender_name, sender_email,
                          sender_phone, *english_translation)
    logger.debug(incident)
    ack = prepare_ack(sender_name, sender_email, sender_phone, incident, native_lang,
                      short_description, long_description, *english_translation)
    logger.debug(ack)
    send_ack(sender_name, sender_email, *ack)


@logger.catch
def update(inc_number, sender_name, sender_email, short_description, long_description):
    # TODO: Update function
    logger.debug("Update function")
    email_check(sender_email)
    update_inc(sender_name, sender_email, inc_number, long_description)


@logger.catch
def status(inc_number, sender_name, sender_email):
    # TODO: Status function
    logger.debug("Status function")
    email_check(sender_email)
    inc_status = status_inc(inc_number)
    if (LOG_LEVEL == "TRACE") or (LOG_LEVEL == "DEBUG"):
        print_json(inc_status)
    send_status(sender_name, sender_email, inc_number, inc_status)


@logger.catch
def print_json(json_data):
    formatted_json = json.dumps(json_data, sort_keys=True, indent=4)
    colorful_json = highlight(
        formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter())
    print(colorful_json)


@logger.catch
def set_log_level(log_level):
    if log_level == "DEBUG":
        log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level>  | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    else:
        log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level>  | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

    logger.remove()
    # Log to console
    logger.add(sys.stderr, colorize=True, format=log_format, level=log_level)
    # Log to log file
    logger.add(cfg.__log_files__ +
               "\snowmail_{time:YYYY_MM_DD}.log", level=log_level, rotation="100 MB")
    # Log to syslog
    handler = logging.handlers.SysLogHandler(
        address=(str(SYSLOG_HOST), int(SYSLOG_PORT)))
    logger.add(handler)

    if log_level == "QUIET":
        logger.disable("")
    else:
        logger.enable("")


@logger.catch
def email_check(sender_email):
    logger.info("Validating Email")
    valid_email_regex = re.compile(
        r'^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$')
    if not valid_email_regex.match(str(sender_email)):
        logger.error("Invalid Email")
        exit(1)
    else:
        logger.info("Valid Email")


# Function to detect sender native language
@logger.catch
def detect_lang(short_description, long_description):
    # Detect language with Detect Language API
    short_desc_native_lang = single_detection(
        short_description, api_key=DETECT_LANG_API_KEY)
    long_desc_native_lang = single_detection(
        long_description, api_key=DETECT_LANG_API_KEY)
    global native_lang
    native_lang = long_desc_native_lang
    logger.info('Detected Short Desc Lang: ' + str(short_desc_native_lang))
    logger.info('Detected Long Desc Lang: ' + str(long_desc_native_lang))
    return(short_description, long_description, short_desc_native_lang, long_desc_native_lang)


# Function to translate from native language to english
@logger.catch
def native2english(short_description, long_description, short_desc_native_lang, long_desc_native_lang):
    if TRANSLATION_ENGINE == "GoogleTranslator":
        short_eng_desc = GoogleTranslator(
            source='auto', target=TO_LANG).translate(text=short_description)
        long_eng_desc = GoogleTranslator(
            source='auto', target=TO_LANG).translate(text=long_description)
    elif TRANSLATION_ENGINE == "MyMemoryTranslator":
        short_eng_desc = MyMemoryTranslator(
            source=short_desc_native_lang, target=TO_LANG).translate(short_description)
        long_eng_desc = MyMemoryTranslator(
            source=long_desc_native_lang, target=TO_LANG).translate(long_description)
    else:
        logger.error("Invalid translator!")
    logger.info('Translated Short Description: ' + short_eng_desc)
    logger.info('Translated Long Description: ' + long_eng_desc)
    return(short_eng_desc, long_eng_desc)


# Function to translate form english to native language
@logger.catch
def prepare_ack(sender_name, sender_email, sender_phone, incident, native_lang, short_description, long_description, short_eng_desc, long_eng_desc):
    # TODO: Add parsed phone number(s)
    logger.info("english2native")
    ack_subject = 'MSA SmartTech Support Incident {incident} Created'.format(
        incident=incident)
    ack_native_message = textwrap.dedent('''\
                            \n
                            Hello {sender_name}, we have received your email requesting assistance with your MSA SmartTech device.\n
                            A support incident has been created with the following details:
                            Incident Number: {incident}
                            Sender Name: {sender_name}
                            Sender Email: {sender_email}
                            Sender Phone Number: {sender_phone}
                            Native Language: {native_lang}
                            Subject ({native_lang}): {short_description}
                            Message ({native_lang}): {long_description}\
                            ''').format(sender_name=sender_name, sender_email=sender_email, sender_phone=sender_phone, incident=incident, native_lang=native_lang, short_description=short_description, long_description=long_description)
    ack_en_message = textwrap.dedent('''\
                            \n
                            English Translation:
                            Subject: {short_eng_desc}
                            Message: {long_eng_desc}\
                            ''').format(short_eng_desc=short_eng_desc, long_eng_desc=long_eng_desc)
    ack_subject = GoogleTranslator(
        source='auto', target=native_lang).translate(text=ack_subject)
    ack_native_message = GoogleTranslator(
        source='auto', target=native_lang).translate(text=ack_native_message)
    logger.info('Subject: ' + ack_subject)
    logger.info('Message: ' + ack_native_message)
    return(ack_subject, ack_native_message, ack_en_message)


@logger.catch
def send_ack(sender_name, sender_email, ack_subject, ack_native_message, ack_en_message):
    ack_message = (ack_native_message + ack_en_message)
    logger.debug(ack_subject)
    logger.debug(ack_message)
    smtp(sender_name, sender_email, ack_subject, ack_message)


@logger.catch
def priority_lookup(argument):
    logger.debug(argument)
    switcher = {
        0: "Catastrophic",
        1: "High",
        2: "Medium",
        3: "Low"
    }
    p = switcher.get(argument, "Invalid priority")
    logger.debug(p)
    return (p)


@logger.catch
def send_status(sender_name, sender_email, incident, status):
    subject = 'MSA SmartTech Support Incident {incident} Status'.format(
        incident=incident)
    message_dict = status
    incident_number = (message_dict['number'])
    p = priority_lookup(int(message_dict['priority']))
    u_msa_status = (message_dict['u_msa_status'])
    opened_at = (message_dict['opened_at'])
    short_description = (message_dict['short_description'])
    description = (message_dict['description'])
    u_fedex_caller = (message_dict['u_fedex_caller'])
    u_msa_caller_email = (message_dict['u_msa_caller_email'])
    u_callers_phone_number = (message_dict['u_callers_phone_number'])
    message = textwrap.dedent('''\
                            \n
                            Incident Number: {incident_number}
                            Priority: {priority}
                            Status: {u_msa_status}
                            Opened: {opened_at}
                            Short Description: {short_description}
                            Description: {description}
                            Contact Name: {u_fedex_caller}
                            Contact Email: {u_msa_caller_email}
                            Contact Phone Number: {u_callers_phone_number}\
                            ''').format(incident_number=incident_number, priority=p, u_msa_status=u_msa_status, opened_at=opened_at, short_description=short_description, description=description, u_fedex_caller=u_fedex_caller, u_msa_caller_email=u_msa_caller_email, u_callers_phone_number=u_callers_phone_number)

    # TODO: Parse JSON and format status response email
    smtp(sender_name, sender_email, subject, message)


def smtp(name, email, subject, message):
    client = SMTP(
        SMTP_server=SMTP_SERVER,
        SMTP_account=SMTP_USER,
        SMTP_password=SMTP_PASSWORD
    )
    client.create_mime(
        recipient_email_addr=email,
        sender_email_addr=SMTP_SENDER,
        subject=subject,
        sender_display_name=SMTP_NAME,
        recipient_display_name=name,
        content_text=message
    )
    client.send_msg()


@logger.catch
def snow_incident_client():
    # Determine run mode
    if (RUN_MODE == "PROD"):
        SNOW_INSTANCE = SNOW_PROD_INSTANCE
    elif (RUN_MODE == "DEV"):
        SNOW_INSTANCE =- SNOW_DEV_INSTANCE
    else:
        (logger.error("Invaid Run Mode"))
    # Create incident client object
    c = pysnow.Client(instance=(SNOW_INSTANCE), user=(
        SNOW_API_USER), password=(SNOW_API_PASSWORD))
    # Define a resource, here we'll use the incident table API
    incident = c.resource(api_path=INCIDENT)
    return(incident)


@logger.catch
def create_inc(sender_name, sender_email, sender_phone, short_description, long_description):
    # Create client object
    incident = snow_incident_client()

    # Set the payload
    new_record = {
        'company': COMPANY,
        'caller_id': CALLER,
        'opened_by': OPENED_BY,
        'contact_type': CONTACT_TYPE,
        'category': CATEGORY,
        'u_account_executive': AE,
        'u_fedex_caller': sender_name,
        'u_msa_caller_email': sender_email,
        'u_callers_phone_number': sender_phone,
        'short_description': short_description,
        'description': long_description
    }

    # Create a new incident record
    logger.debug(new_record)
    if RUN_MODE == "LOCAL_TEST":
        inc_number = "LOCAL_TEST"
    else:
        result = incident.create(payload=new_record)
        inc_number = (result.__getitem__('number'))
    logger.info('Incident Number: ' + inc_number)
    return (inc_number)


@logger.catch
def update_inc(sender_name, sender_email, inc_number, comment):
    # TODO: Create SNOW update function
    # TODO: Translation services
    logger.info("Incident update")

    # Create client object
    incident = snow_incident_client()

    # Set the payload
    update = {"comments": comment}

    # Update 'short_description' and 'state' for 'INC012345'
    # updated_record = incident.update(payload=update)
    incident.update(query={'number': inc_number}, payload=update)


@logger.catch
def status_inc(inc_number):
    # TODO: Create SNOW status function
    # TODO: Translation services
    logger.info("Incident status")

    # Create client object
    incident = snow_incident_client()

    # Query for incident with number INC#
    response = incident.get(query={'number': inc_number})

    # Print out the matching record
    return(response.one())


if __name__ == "__main__":
    main()
