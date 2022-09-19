import discord
import os
import re
from discord.ext import commands  # Bot Commands Frameworkのインポート
from .modules.savefile import SaveFile
from .modules import settings
from .modules.scrapboxsidandpnames import ScrapboxSidAndPnames
from logging import getLogger

LOG = getLogger('assistantbot')

# コグとして用いるクラスを定義。
class OnMessageCog(commands.Cog, name="メッセージイベント用"):
    FILEPATH = 'modules/files/temp'

    # OnMessageCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    def __init__(self, bot):
        self.bot = bot
        self.savefile = SaveFile()
        self.scrapboxSidAndPnames = ScrapboxSidAndPnames()

    # メッセージ変更時に実行されるイベントハンドラを定義
    @commands.Cog.listener()
    async def on_message_edit(self, beforeMessage: discord.Message, afterMessage: discord.Message):
        botUser = self.bot.user
        save_file_message_target = ''

        if beforeMessage.author == botUser:# 自分は無視する
            return
        if settings.SAVE_FILE_MESSAGE:
            save_file_message_target = settings.SAVE_FILE_MESSAGE

        rePattern = re.compile(save_file_message_target)

        LOG.debug(afterMessage)
        # LOG.debug(afterMessage.clean_content)
        # LOG.debug("save_target:" + save_file_message_target)
        if not rePattern.search(afterMessage.clean_content):# 対象のメッセージでない場合、処理を中断
            return
        else:
            await self.save_message_file(afterMessage)

    # embedsを確認し、画像ならチャンネルへ添付する
    async def save_message_file(self, targetMessage: discord.Message):
        files = []
        img_url = ''

        if len(targetMessage.embeds)  == 0:
            return

        for embed in targetMessage.embeds:
            current_path = os.path.dirname(os.path.abspath(__file__))
            saved_path = ''.join([current_path, os.sep, self.FILEPATH.replace('/', os.sep)])

            if embed.image.url:
                img_url = embed.image.url

            dicted_data = embed.to_dict()
            if 'thumbnail' in dicted_data and 'url' in dicted_data['thumbnail']:
                img_url = dicted_data['thumbnail']['url']

            # LOG.debug(embed.image)
            # LOG.debug('filepath:' + saved_path)
            LOG.info(dicted_data)
            if img_url:
                path = await self.savefile.download_file_to_dir(img_url, saved_path)
                if path is not None:
                    embed_data = discord.Embed() 
                    embed_data.set_thumbnail(url=f'attachment://{path}')
                    full_path = saved_path + os.sep + path
                    files.append(discord.File(full_path, filename=path))
                    LOG.debug('save file: ' + full_path)
            else:
                LOG.debug('url is empty.')
                return

        # チャンネルにファイルを添付する(複数ある場合、filesで添付)
        if (len(files) > 1):
            await targetMessage.reply('file upload', files=files
                # channel.sendではembedsは送信できない(webhook.sendのみ)
                , mention_author=False)
        elif (len(files) == 1):
            await targetMessage.reply('file upload', file=files.pop()
                , embed=embed_data
                , mention_author=False)
        else:
            return

    # メッセージ送信時に実行されるイベントハンドラを定義
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        botUser = self.bot.user
        save_file_message_target = ''

        if message.author == botUser:# 自分は無視する
            return

        if self.scrapboxSidAndPnames.SCRAPBOX_URL_PATTERN in message.clean_content and self.scrapboxSidAndPnames.setup(message.guild):
            await self.scrapbox_url_expand(message)
        else:
            return

    # ScrapboxのURLを展開
    async def scrapbox_url_expand(self, targetMessage: discord.Message):
        if (self.scrapboxSidAndPnames.check(targetMessage)):
            embed = await self.scrapboxSidAndPnames.expand(targetMessage)
            if embed is not None:
                await targetMessage.reply(embed=embed)
        else:
            return

async def setup(bot):
    await bot.add_cog(OnMessageCog(bot)) # OnMessageCogにBotを渡してインスタンス化し、Botにコグとして登録する