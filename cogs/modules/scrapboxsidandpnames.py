from . import settings
from logging import getLogger

import re
import discord
import aiohttp
import datetime

logger = getLogger(__name__)

class ScrapboxSidAndPname:
    def __init__(self, scrapbox_sid, scrapbox_pnames):
        self.scrapbox_sid = scrapbox_sid
        self.scrapbox_pnames = scrapbox_pnames

class ScrapboxSidAndPnames:
    def __init__(self):
        self.targets = []
        self.sbsu_err = ''
        self.target_project = ''
        self.target_sid = ''
        self.SCRAPBOX_URL_PATTERN = 'scrapbox.io/'

    def setup(self, guild:discord.Guild):
        """
        guildに紐づくか、全対象(all)の設定のものをセットアップする
        """
        if settings.SCRAPBOX_SID_AND_PROJECTNAME is not None:
            scrapbox_sid_and_pnames_list = settings.SCRAPBOX_SID_AND_PROJECTNAME.replace(' ', '').split(';')

            if scrapbox_sid_and_pnames_list is not None:
                for scrapbox_sid_and_pnames_target in scrapbox_sid_and_pnames_list:
                    splitdata = scrapbox_sid_and_pnames_target.split(':')
                    scrapbox_sid_and_pnames_sep = []
                    if str(guild.id) in splitdata[0] or ('all' in splitdata[0]):
                        scrapbox_sid_and_pnames_sep = splitdata[1].split('@')

                        if len(scrapbox_sid_and_pnames_sep) == 2:
                            scrapbox_sid = scrapbox_sid_and_pnames_sep[0]
                            scrapbox_pnames = scrapbox_sid_and_pnames_sep[1].split(',')

                            scrapboxSidAndPname = None
                            scrapboxSidAndPname = ScrapboxSidAndPname(scrapbox_sid, scrapbox_pnames)
                            self.targets.append(scrapboxSidAndPname)

            logger.debug(f'guild_id: {guild.id}\n********')
            for scrapboxSidAndPname in self.targets:
                logger.debug(f'sid: {scrapboxSidAndPname.scrapbox_sid}')
                for project_name in scrapboxSidAndPname.scrapbox_pnames:
                    logger.debug(f'project_name: {project_name}')

            if len(self.targets) > 0:
                return True

        self.sbsu_err = '展開対象のSCRAPBOXのSID、プロジェクトが登録されていません。'
        return False

    def check(self, message:discord.Message):
        """
        メッセージが展開対象のScrapbox Projectかチェック
        """
        for scrapboxSidAndPnamesTarget in self.targets:
            for project_name in scrapboxSidAndPnamesTarget.scrapbox_pnames:
                if project_name in message.clean_content:
                    self.target_project = project_name
                    self.target_sid = scrapboxSidAndPnamesTarget.scrapbox_sid
                    return True
        return False
    
    async def expand(self, message:discord.Message):
        rurl = r'https://' + self.SCRAPBOX_URL_PATTERN + self.target_project + '/([\w/:%#$&?\(\)~\.=\+-]+)'
        cookies={"connect.sid" : self.target_sid}

        regex = re.compile(rurl)
        mo = regex.search(message.clean_content)

        json = None
        target_url = ''
        if mo is not None:
            if mo.group(1): 
                target_url = 'https://scrapbox.io/api/pages/'+ self.target_project + '/' + mo.group(1)

                async with aiohttp.ClientSession(cookies=cookies) as session:
                    async with session.get(target_url) as r:
                        if r.status == 200:
                            json = await r.json()

                if json is not None:
                    embed = discord.Embed(title = json['title'], description = " ".join(json['descriptions']), url=mo.group(0), type='rich')
                    embed.set_author(name=json['user']['displayName'], icon_url=json['user']['photo'])

                    if json['image']:
                        embed.set_thumbnail(url=json['image'])

                    updated = datetime.datetime.fromtimestamp(json['updated'])
                    embed.add_field(name='Updated', value=updated.strftime('%Y/%m/%d(%a) %H:%M:%S'))

                    return embed

