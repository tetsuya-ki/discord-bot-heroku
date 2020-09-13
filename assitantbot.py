import discord
from discord.ext import commands # Bot Commands Frameworkをインポート
from cogs.modules import settings
import textwrap

import traceback # エラー表示のためインポート

# 読み込むCogの名前を格納
INITIAL_EXTENSIONS = [
    'cogs.eventcog'
    , 'cogs.messagecog'
    , 'cogs.admincog'
]

# カラー
HELP_COLOR_NORMAL = 0x0000aa
HELP_COLOR_WARN = 0xaa0000

# クラス定義。ClientのサブクラスであるBotクラスを継承。
class AssistantBot(commands.Bot):
    # AssistantBotのコンストラクタ。
    def __init__(self, command_prefix, help_command):
        # スーパークラスのコンストラクタに値を渡して実行。
        super().__init__(command_prefix, case_insensitive = True, help_command=help_command)
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

# クラス定義。HelpCommandクラスを継承。
class Help(commands.HelpCommand):

    # AssistantBotのコンストラクタ。
    def __init__(self):
        # スーパークラスのコンストラクタに値を渡して実行。
        super().__init__()
        self.no_category = 'カテゴリ未設定'
        self.command_attrs['description'] = 'コマンドリストを表示します。'
        # ここでメソッドのオーバーライドを行います。

    async def create_category_tree(self,category,enclosure):
            """
            コマンドの集まり（Group、Cog）から木の枝状のコマンドリスト文字列を生成する。
            生成した文字列は enlosure 引数に渡された文字列で囲われる。
            """
            content = ''
            command_list = category.walk_commands()
            for cmd in await self.filter_commands(command_list,sort=True):
                if cmd.root_parent:
                    # cmd.root_parent は「根」なので、根からの距離に応じてインデントを増やす
                    index = cmd.parents.index(cmd.root_parent)
                    indent = '\t' * (index + 1)
                    if indent:
                        content += f'`{indent}- {cmd.name}` → {cmd.description}\n'
                    else:
                        # インデントが入らない、つまり木の中で最も浅く表示されるのでprefixを付加
                        content += f'`{self.context.prefix}{cmd.name}` → {cmd.description}\n'
                else:
                    # 親を持たないコマンドなので、木の中で最も浅く表示する。prefixを付加
                    content += f'`{self.context.prefix}{cmd.name}` → {cmd.description}\n'

            if content == '':
                content = '＊中身なし＊'
            return enclosure + textwrap.dedent(content) + enclosure

    async def send_bot_help(self,mapping):
        embed = discord.Embed(title='＊＊コマンドリスト＊＊',color=HELP_COLOR_NORMAL)
        if self.context.bot.description:
            # もしBOTに description 属性が定義されているなら、それも埋め込みに追加する
            embed.description = self.context.bot.description
        for cog in mapping:
            if cog:
                cog_name = cog.qualified_name
            else:
                # mappingのキーはNoneになる可能性もある
                # もしキーがNoneなら、自身のno_category属性を参照する
                cog_name = self.no_category

            command_list = await self.filter_commands(mapping[cog],sort=True)
            content = ''
            for cmd in command_list:
                content += f'`{self.context.prefix}{cmd.name}`\n {cmd.description}\n'
            if content == '':
                content = '＊中身なし＊'
            embed.add_field(name=cog_name,value=content,inline=False)

        await self.get_destination().send(embed=embed)

    async def send_cog_help(self,cog):
        embed = discord.Embed(title=cog.qualified_name,description=cog.description,color=HELP_COLOR_NORMAL)
        embed.add_field(name='コマンドリスト：',value=await self.create_category_tree(cog,''))
        await self.get_destination().send(embed=embed)

    async def send_group_help(self,group):
        embed = discord.Embed(title=f'{self.context.prefix}{group.qualified_name}',
            description=group.description,color=HELP_COLOR_NORMAL)
        if group.aliases:
            embed.add_field(name='有効なエイリアス：',value='`' + '`, `'.join(group.aliases) + '`',inline=False)
        if group.help:
            embed.add_field(name='ヘルプテキスト：',value=group.help,inline=False)
        embed.add_field(name='サブコマンドリスト：',value=await self.create_category_tree(group,''),inline=False)
        await self.get_destination().send(embed=embed)

    async def send_command_help(self,command):
        params = ' '.join(command.clean_params.keys())
        embed = discord.Embed(title=f'{self.context.prefix}{command.qualified_name} {params}',
            description=command.description,color=HELP_COLOR_NORMAL)
        if command.aliases:
            embed.add_field(name='有効なエイリアス：',value='`' + '`, `'.join(command.aliases) + '`',inline=False)
        if command.help:
            embed.add_field(name='ヘルプテキスト：',value=command.help,inline=False)
        await self.get_destination().send(embed=embed)

    async def send_error_message(self, error):
        embed = discord.Embed(title='ヘルプ表示のエラー',description=error,color=HELP_COLOR_WARN)
        await self.get_destination().send(embed=embed)

    def command_not_found(self,string):
        return f'{string} というコマンドは存在しません。'

    def subcommand_not_found(self,command,string):
        if isinstance(command, commands.Group) and len(command.all_commands) > 0:
            # もし、そのコマンドにサブコマンドが存在しているなら
            return f'{command.qualified_name} に {string} というサブコマンドは登録されていません。'
        return f'{command.qualified_name} にサブコマンドは登録されていません。'

# AssitantBotのインスタンス化および起動処理。
if __name__ == '__main__':
    bot = AssistantBot(
            command_prefix = '/'
            ,help_command=Help()
        )# 大文字小文字は気にしない
    bot.run(settings.DISCORD_TOKEN)