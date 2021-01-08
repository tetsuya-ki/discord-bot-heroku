from . import settings
from logging import getLogger

import discord

logger = getLogger(__name__)

class AuditLogChannel:
    def __init__(self):
        self.channel = None
        self.alc_err = ''

    async def get_ch(self, guild:discord.Guild):
        if settings.AUDIT_LOG_SEND_CHANNEL is not None:
            channel_list = settings.AUDIT_LOG_SEND_CHANNEL.replace(' ', '').split(';')
            channels = [al.split('.') for al in channel_list if str(guild.id) in al]
            channels = channels[0]

            logger.debug(f'guild_id: {guild.id}\n********')
            for ch in channel_list:
                logger.debug(ch)
            if len(channels) == 2:
                if channels[1].isdecimal():
                    self.channel = guild.get_channel(int(channels[1]))
                    logger.debug(self.channel)
                    if self.channel is not None:
                        return True
        self.alc_err = '管理用のチャンネルが登録されていません。'
        return False