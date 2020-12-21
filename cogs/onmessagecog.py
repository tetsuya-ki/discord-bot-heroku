import discord
from discord.ext import commands # Bot Commands Frameworkのインポート
from .modules.savefile import SaveFile
from .modules import settings
import os
import re

# コグとして用いるクラスを定義。
class OnMessageCog(commands.Cog, name="メッセージイベント用"):
    FILEPATH = 'modules/files/temp'

    # OnMessageCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    def __init__(self, bot):
        self.bot = bot
        self.savefile = SaveFile()

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

        if settings.IS_DEBUG:
            print(afterMessage)
            # print(afterMessage.clean_content)
            # print("save_target:" + save_file_message_target)
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

            if settings.IS_DEBUG:
                # print(embed.image)
                # print('filepath:' + saved_path)
                print(dicted_data)
            if img_url:
                path = await self.savefile.download_file_to_dir(img_url, saved_path)
                if path is not None:
                    files.append(discord.File(path))
                    if settings.IS_DEBUG:
                        print('save file: ' + path)
            else:
                if settings.IS_DEBUG:
                    print('url is empty.')
                return

        # チャンネルにファイルを添付する(複数ある場合、filesで添付)
        if (len(files) > 1):
            await targetMessage.channel.send('file upload', files=files)
        elif (len(files) == 1):
            await targetMessage.channel.send('file upload', file=files.pop())
        else:
            return

def setup(bot):
    bot.add_cog(OnMessageCog(bot)) # OnMessageCogにBotを渡してインスタンス化し、Botにコグとして登録する