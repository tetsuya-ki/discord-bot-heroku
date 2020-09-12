from discord.ext import commands # Bot Commands Frameworkをインポート
from cogs.modules import settings

import traceback # エラー表示のためインポート

# 読み込むCogの名前を格納
INITIAL_EXTENSIONS = [
    'cogs.eventcog'
    , 'cogs.messagecog'
    , 'cogs.admincog'
]

# クラス定義。ClientのサブクラスであるBotクラスを継承。
class AssistantBot(commands.Bot):

    # AssistantBotのコンストラクタ。
    def __init__(self, command_prefix):
        # スーパークラスのコンストラクタに値を渡して実行。
        super().__init__(command_prefix, case_insensitive = True)

        # INITIAL_EXTENSIONに格納されている名前からCogを読み込む。
        # エラーが発生した場合、エラー内容を表示する。
        for cog in INITIAL_EXTENSIONS:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()

    # Botの準備完了時に呼び出されるイベント
    async def on_ready(self):
        print('We have logged in as {0}'.format(self.user))

# AssitantBotのインスタンス化および起動処理。
if __name__ == '__main__':
    bot = AssistantBot(command_prefix = '/')# 大文字小文字は気にしない
    bot.run(settings.DISCORD_TOKEN)