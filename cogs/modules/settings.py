import os
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), 'files' + os.sep + '.env')
load_dotenv(dotenv_path)
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
IS_DEBUG = os.environ.get('IS_DEBUG')
REACTION_CHANNELER_100 = int(os.environ.get('REACTION_CHANNELER_100'))
REACTION_CHANNELER_BELL = int(os.environ.get('REACTION_CHANNELER_BELL'))
REACTION_CHANNELER_FLAG = int(os.environ.get('REACTION_CHANNELER_FLAG'))
AUDIT_LOG_SEND_CHANNEL = int(os.environ.get('AUDIT_LOG_SEND_CHANNEL'))