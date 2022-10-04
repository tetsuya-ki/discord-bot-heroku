import discord, asyncio, datetime, logging.handlers, os
from discord.ext import commands  # Bot Commands Frameworkをインポート
from cogs.modules import settings
from logging import basicConfig, getLogger, StreamHandler, FileHandler, Formatter, NOTSET
from datetime import timedelta, timezone

# ストリームハンドラの設定
stream_handler = StreamHandler()
stream_handler.setLevel(settings.LOG_LEVEL)
stream_handler.setFormatter(Formatter("%(asctime)s@ %(name)s [%(levelname)s] %(funcName)s: %(message)s"))

# 保存先の有無チェック
if not os.path.isdir('./Log'):
    os.makedirs('./Log', exist_ok=True)

# ファイルハンドラの設定
file_handler = logging.handlers.RotatingFileHandler(
    filename=f'./Log/assistbot.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=30,  # Rotate through 30 files
)
file_handler.setLevel(settings.LOG_LEVEL)
file_handler.setFormatter(
    Formatter("%(asctime)s@ %(name)s [%(levelname)s] %(funcName)s: %(message)s")
)
# ルートロガーの設定
basicConfig(level=NOTSET, handlers=[stream_handler, file_handler])

LOG = getLogger('assistantbot')

# 読み込むCogの名前を格納
INITIAL_EXTENSIONS = [
    'cogs.messagecog'
    , 'cogs.admincog'
    , 'cogs.reactionchannelercog'
    , 'cogs.onmessagecog'
    , 'cogs.gamecog'
]

# クラス定義。ClientのサブクラスであるBotクラスを継承。
class AssistantBot(commands.Bot):
    # AssistantBotのコンストラクタ。
    def __init__(self, command_prefix, intents, application_id):
        # スーパークラスのコンストラクタに値を渡して実行。
        super().__init__(command_prefix, case_insensitive = True, help_command=None, intents=intents, application_id=application_id) # application_idが必要

    async def setup_hook(self):
        # INITIAL_EXTENSIONに格納されている名前からCogを読み込む。
        for cog in INITIAL_EXTENSIONS:
            await self.load_extension(cog) # awaitが必要

        # テスト中以外は環境変数で設定しないことを推奨(環境変数があれば、ギルドコマンドとして即時発行される)
        if settings.ENABLE_SLASH_COMMAND_GUILD_ID is not None and len(settings.ENABLE_SLASH_COMMAND_GUILD_ID) > 0:
            LOG.info(settings.ENABLE_SLASH_COMMAND_GUILD_ID)
            for guild in settings.ENABLE_SLASH_COMMAND_GUILD_ID:
                LOG.info(guild)
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
        else:
            await self.tree.sync() # グローバルコマンドとして発行(使用できるまで、最大1時間程度かかる)

async def main():
    # Botの起動
    async with bot:
        await bot.start(settings.DISCORD_TOKEN)
        LOG.info('We have logged in as {0}'.format(bot.user))

# AssistantBotのインスタンス化および起動処理。
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
        )
    asyncio.run(main())