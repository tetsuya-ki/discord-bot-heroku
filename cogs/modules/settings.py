import os
from os.path import join, dirname
from dotenv import load_dotenv

def if_env(str):
    if str == 'True':
        return True
    else:
        return False

load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), 'files' + os.sep + '.env')
load_dotenv(dotenv_path)

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
IS_DEBUG = if_env(os.environ.get('IS_DEBUG'))
AUDIT_LOG_SEND_CHANNEL = os.environ.get('AUDIT_LOG_SEND_CHANNEL')
IS_HEROKU = if_env(os.environ.get('IS_HEROKU'))