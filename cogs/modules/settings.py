import os, discord
from os.path import join, dirname
from dotenv import load_dotenv
from logging import DEBUG, INFO, WARN, ERROR

def if_env(str):
    if str is None or str.upper() != 'TRUE':
        return False
    else:
        return True

def if_env_defalut_true(str):
    if str is None or str.upper() == 'TRUE':
        return True
    else:
        return False

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

def split_guild_env(str):
    guilds = []
    if str is None or str == '':
        pass
    elif not ';' in str:
        guilds.append(discord.Object(str))
    else:
        guilds = list(map(discord.Object, str.split(';')))
    return guilds

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
PURGE_TARGET_IS_ME_AND_BOT = if_env(os.environ.get('PURGE_TARGET_IS_ME_AND_BOT'))
OHGIRI_JSON_URL = os.environ.get('OHGIRI_JSON_URL')
REACTION_CHANNELER_PERMIT_WEBHOOK_ID = os.environ.get('REACTION_CHANNELER_PERMIT_WEBHOOK_ID')
WORDWOLF_JSON_URL = os.environ.get('WORDWOLF_JSON_URL')
NGWORD_GAME_JSON_URL = os.environ.get('NGWORD_GAME_JSON_URL')
APPLICATION_ID = os.environ.get('APPLICATION_ID')
ENABLE_SLASH_COMMAND_GUILD_ID = split_guild_env(os.environ.get('ENABLE_SLASH_COMMAND_GUILD_ID'))
USE_IF_AVAILABLE_FILE = if_env(os.environ.get('USE_IF_AVAILABLE_FILE'))
USE_TWITTER_EXPANDED = if_env_defalut_true(os.environ.get('USE_TWITTER_EXPANDED'))