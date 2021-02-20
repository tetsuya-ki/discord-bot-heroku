import os
from os.path import join, dirname
from dotenv import load_dotenv
from logging import DEBUG, INFO, WARN, ERROR

def if_env(str):
    if str is None or str.upper() != 'TRUE':
        return False
    else:
        return True

def get_log_level(str):
    if str is None:
        return WARN
    upper_str = str.upper()
    if upper_str == 'DEBUG':
        return DEBUG
    elif upper_str == 'INFO':
        return INFO
    elif upper_str == 'ERROR':
        return ERROR
    else:
        return WARN

def num_env(param):
    if str is None or not str(param).isdecimal():
        return 5
    else:
        return int(param)

load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), 'files' + os.sep + '.env')
load_dotenv(dotenv_path)

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
LOG_LEVEL = get_log_level(os.environ.get('LOG_LEVEL'))
AUDIT_LOG_SEND_CHANNEL = os.environ.get('AUDIT_LOG_SEND_CHANNEL')
IS_HEROKU = if_env(os.environ.get('IS_HEROKU'))
SAVE_FILE_MESSAGE = os.environ.get('SAVE_FILE_MESSAGE')
FIRST_REACTION_CHECK = if_env(os.environ.get('FIRST_REACTION_CHECK'))
SCRAPBOX_SID_AND_PROJECTNAME = os.environ.get('SCRAPBOX_SID_AND_PROJECTNAME')
COUNT_RANK_SETTING = num_env(os.environ.get('COUNT_RANK_SETTING'))
PURGE_TARGET_IS_ME_AND_BOT = if_env(os.environ.get('PURGE_TARGET_IS_ME_AND_BOT'))
OHGIRI_JSON_URL = os.environ.get('OHGIRI_JSON_URL')
REACTION_CHANNELER_PERMIT_WEBHOOK_ID = os.environ.get('REACTION_CHANNELER_PERMIT_WEBHOOK_ID')