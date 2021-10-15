from discord.ext import commands  # Bot Commands Frameworkをインポート
from discord_slash import SlashCommand
# from discord_slash.utils import manage_commands # for delete slash command
from cogs.modules import settings
from logging import basicConfig, getLogger, StreamHandler, FileHandler, Formatter, NOTSET
from datetime import timedelta, timezone

import discord, textwrap, os, datetime
# 先頭に下記を追加
import keep_alive

# 時間
JST = timezone(timedelta(hours=9), 'JST')
now = datetime.datetime.now(JST)

# ストリームハンドラの設定
stream_handler = StreamHandler()
stream_handler.setLevel(settings.LOG_LEVEL)
stream_handler.setFormatter(Formatter("%(asctime)s@ %(name)s [%(levelname)s] %(funcName)s: %(message)s"))

# 保存先の有無チェック
if not os.path.isdir('./Log'):
    os.makedirs('./Log', exist_ok=True)

# ファイルハンドラの設定
file_handler = FileHandler(
    f"./Log/log-{now:%Y%m%d_%H%M%S}.log"
)
file_handler.setLevel(settings.LOG_LEVEL)
file_handler.setFormatter(
    Formatter("%(asctime)s@ %(name)s [%(levelname)s] %(funcName)s: %(message)s")
)

# ルートロガーの設定
basicConfig(level=NOTSET, handlers=[stream_handler, file_handler])

LOG = getLogger('word_wolf')

# 読み込むCogの名前を格納
INITIAL_EXTENSIONS = [
    'cogs.gamecog'
]

# クラス定義。ClientのサブクラスであるBotクラスを継承。
class AssistantBot(commands.Bot):
    # AssistantBotのコンストラクタ。
    def __init__(self, command_prefix, intents):
        # スーパークラスのコンストラクタに値を渡して実行。
        super().__init__(command_prefix, case_insensitive = True, intents=intents, help_command=None)
        slash = SlashCommand(self, sync_commands=True) # ココにslashをおこう！(第一引数はself)
        # INITIAL_EXTENSIONに格納されている名前からCogを読み込む。
        # エラーが発生した場合、エラー内容を表示する。
        for cog in INITIAL_EXTENSIONS:
            self.load_extension(cog)
            # try:
            #     self.load_extension(cog)
            # except Exception:
            #     LOG.warning("traceback:", stack_info=True)

    # Botの準備完了時に呼び出されるイベント
    async def on_ready(self):
        LOG.info('We have logged in as {0}'.format(self.user))
        LOG.info(f"### guild num: {len(self.guilds)} ### ")

        # #### for delete slash command #####
        # guilds = [] if settings.ENABLE_SLASH_COMMAND_GUILD_ID_LIST is None else list(
        #     map(int, settings.ENABLE_SLASH_COMMAND_GUILD_ID_LIST.split(';')))
        # for guild in guilds:
        #     await manage_commands.remove_all_commands_in(self.user.id, settings.DISCORD_TOKEN, guild)
        #     LOG.info('remove all guild command for {0}.'.format(guild))

# AssitantBotのインスタンス化および起動処理。
if __name__ == '__main__':
    intents = discord.Intents.default()
    intents.members = False
    intents.typing = False
    intents.presences = False

    # start a server
    keep_alive.keep_alive()
    bot = AssistantBot(
            command_prefix = '/'
            ,intents=intents
        )# 大文字小文字は気にしない
    bot.run(settings.DISCORD_TOKEN)