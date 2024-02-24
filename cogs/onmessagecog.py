import discord
import os
import re
import aiohttp
import locale
import datetime
from discord.ext import commands  # Bot Commands Frameworkのインポート
from logging import getLogger
from datetime import timedelta, timezone
from .modules.savefile import SaveFile
from .modules import settings
from .modules.scrapboxsidandpnames import ScrapboxSidAndPnames

LOG = getLogger('assistantbot')

# コグとして用いるクラスを定義。
class OnMessageCog(commands.Cog, name="メッセージイベント用"):
    FILEPATH = 'modules/files/temp'
    TWITTER_URL = 'https://twitter.com/'
    TWITTER_OR_X_URL = 'https://(?:(?:twitter)|x)\.com/'
    TWITTER_STATUS_URL = TWITTER_OR_X_URL + '.+?/status/(\d+)'
    TWITTER_EXPAND_URL = 'https://cdn.syndication.twimg.com/tweet-result?token=x&id='
    TWIMG_URL = '(https://pbs.twimg.com/media/.+)'
    JST = timezone(timedelta(hours=9), 'JST')

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

        embeds = []
        before_embeds_url = ''
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
            if img_url is not None and before_embeds_url != img_url:
                path = await self.savefile.download_file_to_dir(img_url, saved_path)
                before_embeds_url = img_url.replace(':large','')
                if path is not None:
                    embed_data = discord.Embed(url='https://discord.com')
                    embed_data.set_image(url=f'attachment://{path}')
                    embeds.append(embed_data)
                    full_path = saved_path + os.sep + path
                    files.append(discord.File(full_path, filename=path))
                    LOG.debug('save file: ' + full_path)
            else:
                LOG.debug('url is empty.')
                continue

        # チャンネルにファイルを添付する
        if (len(files) > 0):
            await targetMessage.reply(
                'file upload',
                files=files,
                embeds=embeds,
                mention_author=False,
                silent=True)
        else:
            return

    # メッセージ送信時に実行されるイベントハンドラを定義
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        botUser = self.bot.user

        if message.author == botUser:# 自分は無視する
            return

        # Twitter展開機能(デフォルト:TRUE)
        if settings.USE_TWITTER_EXPANDED:
            # Twitter展開(対象あり、かつ、embedsがない(Discordによる展開がない)->うまく動いていない模様...)
            reSearch = re.compile(self.TWITTER_STATUS_URL).search(message.clean_content)
            if reSearch is not None and len(reSearch.groups()) > 0 and len(message.embeds) == 0:
                if type(reSearch.group(1)) is str:
                    await self.twitter_url_expand(message, reSearch.group(1))

        if self.scrapboxSidAndPnames.SCRAPBOX_URL_PATTERN in message.clean_content and self.scrapboxSidAndPnames.setup(message.guild):
            await self.scrapbox_url_expand(message)
        else:
            return

    # ScrapboxのURLを展開
    async def scrapbox_url_expand(self, targetMessage: discord.Message):
        if (self.scrapboxSidAndPnames.check(targetMessage)):
            embed = await self.scrapboxSidAndPnames.expand(targetMessage)
            if embed is not None:
                await targetMessage.reply(embed=embed, mention_author=False, silent=True)
        else:
            return

    # TwitterのURLを展開
    async def twitter_url_expand(self, targetMessage: discord.Message, twitter_status_id: str):
        url = self.TWITTER_EXPAND_URL + twitter_status_id
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                LOG.debug(url)
                LOG.debug(r.status)
                if r.status == 200:
                    data = await r.json()
                    LOG.info(await r.text())

                    # 画像の保存
                    files = []
                    embeds = []
                    image_paths = []
                    thumbnail_url = None

                    # 通常
                    if data.get('__typename') != 'TweetTombstone':
                        if data.get('mediaDetails') is not None:
                            for media in data.get('mediaDetails'):
                                if media.get('media_url_https') is not None:
                                    thumbnail_url = media.get('media_url_https')
                                    current_path = os.path.dirname(os.path.abspath(__file__))
                                    saved_path = ''.join([current_path, os.sep, self.FILEPATH.replace('/', os.sep)])
                                    path = await self.savefile.download_file_to_dir(thumbnail_url, saved_path)
                                    if path is not None:
                                        full_path = saved_path + os.sep + path
                                        files.append(discord.File(full_path, filename=path))
                                        image_paths.append(path)

                        screen_name = data.get('user').get('screen_name')
                        title_text = f'''{data.get('user').get('name')}(id:{data.get('user').get('id_str')}) by Twitter'''
                        description_text = data.get('text')
                        target_url = f'''{self.TWITTER_URL}{screen_name}/status/{twitter_status_id}'''
                        twitter_profile_url = self.TWITTER_URL + screen_name

                        # debug
                        list = [screen_name,title_text,description_text,target_url,twitter_profile_url]
                        for item in list:
                            LOG.info(item)

                        embed = discord.Embed(
                            title=title_text
                            , color=0x1da1f2
                            , description=description_text
                            , url=target_url
                            )
                        embed.set_author(
                            name=screen_name
                            , url=twitter_profile_url
                            , icon_url=data.get('user').get('profile_image_url_https')
                            )
                        if thumbnail_url is not None:
                            embed.set_thumbnail(url=thumbnail_url)
                            embed.set_image(url=f'''attachment://{image_paths[0]}''')
                        embed.add_field(name='投稿日付',value=self.iso8601_to_jst_text(data.get('created_at')))
                        embed.add_field(name='お気に入り数',value=data.get('favorite_count'))
                        embed.set_footer(
                            text='From Twitter'
                            , icon_url='https://i.imgur.com/NRad4mF.png')

                        for image_path in image_paths:
                            embed_data = discord.Embed(url=target_url)
                            embed_data.set_image(url=f'''attachment://{image_path}''')
                            embeds.append(embed_data)
                        else:
                            if len(embeds) > 0:
                                embeds[0] = embed
                            else:
                                embeds.append(embed)

                        # 画像あり
                        if len(files) > 0:
                            await targetMessage.reply(
                                'Twitter Expanded',
                                files=files,
                                embeds=embeds,
                                mention_author=False,
                                silent=True)
                        else:
                            await targetMessage.reply(
                                'Twitter Expanded',
                                embeds=embeds,
                                mention_author=False,
                                silent=True)
                    # 墓場行きは画像だけ助ける
                    else:
                        LOG.info('This URL is TweetTombstone.')
                        await self.save_twimg_file(targetMessage, 'TweetTombstone')

    # twimgなURLを確認し、画像ならチャンネルへ添付する
    async def save_twimg_file(self, targetMessage: discord.Message, text: str=''):
        files = []
        img_url = ''

        twimg_list = re.compile(self.TWIMG_URL).findall(targetMessage.clean_content)
        if len(twimg_list) == 0:
            return

        LOG.info(twimg_list)
        before_img_url = ''
        for img_url in twimg_list:
            current_path = os.path.dirname(os.path.abspath(__file__))
            saved_path = ''.join([current_path, os.sep, self.FILEPATH.replace('/', os.sep)])

            img_url = img_url.replace(':large','').replace('>','')
            LOG.debug(img_url)
            LOG.debug('filepath:' + saved_path)
            if img_url is not None and before_img_url != img_url:
                before_img_url = img_url.replace(':large','')
                path = await self.savefile.download_file_to_dir(img_url, saved_path)
                if path is not None:
                    full_path = saved_path + os.sep + path
                    files.append(discord.File(full_path, filename=path, spoiler=True))
                    LOG.info('save file: ' + full_path)
            else:
                LOG.info('url is empty.')
                continue

        # チャンネルにファイルを添付する
        if (len(files) > 0):
            message = text + ': file upload' if text is not None else 'file upload'
            await targetMessage.reply(
                message,
                files=files,
                mention_author=False,
                silent=True)
        else:
            return

    def iso8601_to_jst_text(self, iso8601:str):
        dt_utc = datetime.datetime.fromisoformat(iso8601.replace('Z', '+00:00')) # python3.11から不要だが...
        locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
        return dt_utc.astimezone(self.JST).strftime('%Y/%m/%d(%a) %H:%M:%S')

async def setup(bot):
    await bot.add_cog(OnMessageCog(bot)) # OnMessageCogにBotを渡してインスタンス化し、Botにコグとして登録する