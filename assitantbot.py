from discord.ext import commands  # Bot Commands Frameworkをインポート
from cogs.modules import settings
from logging import basicConfig, getLogger

import discord, asyncio

basicConfig(level=settings.LOG_LEVEL)
logger = getLogger(__name__)

# 読み込むCogの名前を格納
INITIAL_EXTENSIONS = [
    # 'cogs.messagecog'
    'cogs.admincog'
    # , 'cogs.reactionchannelercog'
    # , 'cogs.onmessagecog'
    # , 'cogs.gamecog'
]

# クラス定義。ClientのサブクラスであるBotクラスを継承。
class AssistantBot(commands.Bot):
    # AssistantBotのコンストラクタ。
    def __init__(self, command_prefix, intents, application_id):
        # スーパークラスのコンストラクタに値を渡して実行。
        super().__init__(command_prefix, case_insensitive = True, help_command=None, intents=intents, application_id=application_id) # application_idが必要

    # Botの準備完了時に呼び出されるイベント
    async def on_ready(self):
        logger.info('We have logged in as {0}'.format(self.user))

    async def setup_hook(self):
        # INITIAL_EXTENSIONに格納されている名前からCogを読み込む。
        for cog in INITIAL_EXTENSIONS:
            await self.load_extension(cog) # awaitが必要

        # テスト中以外は環境変数で設定しないことを推奨(環境変数があれば、ギルドコマンドとして即時発行される)
        if settings.ENABLE_SLASH_COMMAND_GUILD_ID:
            await bot.tree.sync(guild=discord.Object(settings.ENABLE_SLASH_COMMAND_GUILD_ID))
        else:
            await bot.tree.sync() # グローバルコマンドとして発行(使用できるまで、最大1時間程度かかる)

async def main():
    async with bot:
        await bot.start(settings.DISCORD_TOKEN)

# AssitantBotのインスタンス化および起動処理。
if __name__ == '__main__':
    intents = discord.Intents.default()
    intents.members = True # このBotでは必須(特権インテントの設定が必要)
    intents.typing = False
    intents.presences = False
    intents.message_content = True # このBotでは必須(特権インテントの設定が必要)

    bot = AssistantBot(
            command_prefix = '/'
            ,intents=intents
            ,application_id=settings.APPLICATION_ID
        )# 大文字小文字は気にしない
    asyncio.run(main())