import discord
import random
import os
from discord import app_commands
from discord.ext import commands  # Bot Commands Frameworkのインポート
from typing import Literal
from .modules.readjson import ReadJson
from logging import getLogger
from .modules.coyote import Coyote, CoyoteStart
from .modules.ohgiri import Ohgiri, OhrgiriStart
from os.path import join, dirname
from .modules import settings
from .modules.savefile import SaveFile
from .modules.members import Members
from .modules import games
from logging import getLogger
LOG = getLogger('assistantbot')

POLL_CHAR = ['🇦','🇧','🇨','🇩','🇪','🇫','🇬','🇭','🇮','🇯','🇰','🇱','🇲','🇳','🇴','🇵','🇶','🇷','🇸','🇹']

# コグとして用いるクラスを定義。
class GameCog(commands.Cog, name='ゲーム用'):
    """
    ゲーム機能のカテゴリ。
    """
    guilds = []
    MAX_TIME = 10
    DEFAULT_TIME = 2
    SHOW_ME = '自分のみ'
    SHOW_ALL = '全員に見せる'

    # GameCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    def __init__(self, bot):
        self.bot = bot
        self.coyoteGames = {}
        self.CoyoteStart = None
        self.ohgiriGames = {}
        self.ohgiriStart = None
        self.wordWolfJson = None
        self.ngWordGameJson = None
        self.savefile = SaveFile()
        self.ww_members = {}
        self.ng_members = {}
        self.cy_members = {}
        self.oh_members = {}

    # cogが準備できたら読み込みする
    @commands.Cog.listener()
    async def on_ready(self):
        self.ohgiriGames['default'] = Ohgiri()
        await self.ohgiriGames['default'].on_ready()
        await self.wordWolf_setting()
        await self.ngWordGame_setting()

    async def wordWolf_setting(self):
        wordWolf_filepath = join(dirname(__file__), 'modules' + os.sep + 'files' + os.sep + 'temp' + os.sep + 'wordwolf.json')
        if not os.path.exists(wordWolf_filepath) or \
            (not settings.USE_IF_AVAILABLE_FILE and settings.WORDWOLF_JSON_URL ):
            wordWolf_filepath = await self.json_setting(settings.WORDWOLF_JSON_URL, 'wordwolf.json')
        # ファイルを読み込み、ワードウルフ用のデータを作成
        read_json = ReadJson()
        read_json.readJson(wordWolf_filepath)
        self.wordWolfJson = read_json

    async def ngWordGame_setting(self):
        ngWordGame_filepath = join(dirname(__file__), 'modules' + os.sep + 'files' + os.sep + 'temp' + os.sep + 'ngword_game.json')
        if not os.path.exists(ngWordGame_filepath) or \
            (not settings.USE_IF_AVAILABLE_FILE and settings.NGWORD_GAME_JSON_URL ):
            ngWordGame_filepath = await self.json_setting(settings.NGWORD_GAME_JSON_URL, 'ngword_game.json')
        # ファイルを読み込み、NGワードゲーム用のデータを作成
        read_json = ReadJson()
        read_json.readJson(ngWordGame_filepath)
        self.ngWordGameJson = read_json

    async def json_setting(self, json_url=None, file_name='no_name.json'):
        json_path = join(dirname(__file__), 'modules' + os.sep + 'files' + os.sep + 'temp' + os.sep + file_name)
        # URLが設定されている場合はそちらを使用
        if json_url:
            file_path = await self.savefile.download_file(json_url,  json_path)
            LOG.info(f'JSONのURLが登録されているため、JSONを保存しました。\n{file_path}')
            return file_path

    # ワードウルフ機能
    @app_commands.command(
        name='start-word-wolf',
        description='ワードウルフ機能(少数派のワードを与えられた人を当てるゲーム)')
    @app_commands.describe(
        answer_minutes='投票開始までの時間（3などの正数。単位は「分」）を与えることができます。デフォルトは2分です')
    async def wordWolf(self, interaction: discord.Interaction, answer_minutes: app_commands.Range[int, 1, 10] = 2):
        """
        コマンド実行者が参加しているボイスチャンネルでワードウルフ始めます（BOTからDMが来ますがびっくりしないでください）
        引数(answer_minutes)として投票開始までの時間（3などの正数。単位は「分」）を与えることができます。デフォルトは2分です。
        3人増えるごとにワードウルフは増加します(3−5人→ワードウルフは1人、6−8人→ワードウルフは2人)
        """
        if answer_minutes is None:
            answer_minutes = self.DEFAULT_TIME

        # もう入力できない想定
        if answer_minutes > self.MAX_TIME:
            msg = f'ワードウルフはそんなに長い時間するものではないです(現在、{answer_minutes}分を指定しています。{self.MAX_TIME}分以内にして下さい)'
            await interaction.response.send_message(msg, ephemeral=True)
            return

        # このコマンドが実行された時点でギルドごとのメンバーが設定されていなければ、作っておく
        if not interaction.guild_id in self.ww_members:
            self.ww_members[interaction.guild_id] = Members()
        self.ww_members[interaction.guild_id].set_minutes(answer_minutes)

        msg =   'ワードウルフを始めます(3人以上必要です)！  この中に、**ワードウルフ**が紛れ込んでいます(本人も知りません！/3人増えるごとに1人がワードウルフです)。\n'\
                'DMでお題が配られますが、**ワードウルフだけは別のお題**が配られます(お題は2種類あります)。会話の中で不審な言動を察知し、みごとに'\
                '投票でワードウルフを当てることができたら、市民の勝ち。**間違えて「市民をワードウルフ」だと示してしまった場合、ワードウルフの勝ち**です！！\n'\
                '参加する場合、以下のボタンを押してください。'
        view = games.WordwolfStart(self.ww_members, self.wordWolfJson, msg)
        await interaction.response.send_message(msg, view=view)

    # NGワードゲーム機能
    @app_commands.command(
        name='start-ng-word-game',
        description='NGワードゲーム機能(禁止された言葉を喋ってはいけないゲーム)')
    @app_commands.describe(
        answer_minutes='投票開始までの時間（3などの正数。単位は「分」）を与えることができます。デフォルトは2分です')
    async def ngWordGame(self, interaction: discord.Interaction, answer_minutes: app_commands.Range[int, 1, 10] = 2):
        """
        コマンド実行者が参加しているボイスチャンネルでNGワードゲームを始めます（BOTからDMが来ますがびっくりしないでください）
        引数(answer_minutes)として終了までの時間（3などの正数。単位は「分」）を与えることができます。デフォルトは2分です。
        """
        if answer_minutes is None:
            answer_minutes = self.DEFAULT_TIME

        # このコマンドが実行された時点でギルドごとのメンバーが設定されていなければ、作っておく
        if not interaction.guild_id in self.ng_members:
            self.ng_members[interaction.guild_id] = Members()
        self.ng_members[interaction.guild_id].set_minutes(answer_minutes)

        # もう入力できない想定
        if answer_minutes > self.MAX_TIME:
            msg = f'NGワードゲームはそんなに長い時間するものではないです(現在、{answer_minutes}分を指定しています。{self.MAX_TIME}分以内にして下さい)'
            await interaction.response.send_message(msg, ephemeral=True)
            return

        msg =   'NGワードゲームを始めます(2人以上必要です)！  これからDMでそれぞれのNGワードを配ります！(**自分のNGワードのみ分かりません**)\n'\
                '配られた後に**雑談し、誰かがNGワードを口走ったら、「ドーン！！！」と指摘**してください。すぐさまNGワードが妥当か話し合いください(カッコがある場合は、どちらもNGワードです)。\n'\
                '妥当な場合、NGワード発言者はお休みです。残った人で続けます。**最後のひとりになったら勝利**です！！\n'\
                '参加する場合、以下のボタンを押してください。'
        # await interaction.channel.send(msg)
        view = games.NgWordGameStart(self.ng_members, self.ngWordGameJson, msg)
        await interaction.response.send_message(msg, view=view)

    @app_commands.command(
        name='start-coyote-game',
        description='コヨーテ機能(場にある数値の合計を推測しつつ遊ぶゲーム)')
    @app_commands.describe(
        description='コヨーテを始める際の説明(デフォルトは普通) ')
    async def start(self, interaction: discord.Interaction, description: Literal['普通', '詳しく', '無し'] = '普通'):
        if description  == '詳しく':
            description = Coyote.DESCRPTION_ALL
        elif description == '無し':
            description = Coyote.DESCRPTION_NOTHING
        else:
            description = Coyote.DESCRPTION_NORMAL
        msg = 'コヨーテを始めます(2人以上必要です)！\n参加する場合、以下のボタンを押してください。'
        self.coyoteGames[interaction.guild_id] = Coyote()
        self.cy_members[interaction.guild_id] = Members()
        self.coyoteGames[interaction.guild_id].set_deck_flg = False
        self.coyoteGames[interaction.guild_id].start_description = description
        self.CoyoteStart = CoyoteStart(self.cy_members, self.coyoteGames, msg, description)
        await interaction.response.send_message(msg, view=self.CoyoteStart)

    @app_commands.command(name='roll', description='ダイスを振る(さいころを転がす)')
    @app_commands.describe(dice_and_num='「/roll 1d6」のように、左側にダイスの数、右側にダイスの種類(最大値)を指定')
    @app_commands.describe(reply_is_hidden='Botの実行結果を全員に見せるどうか(デフォルトは全員に見せる)')
    async def roll(self, interaction: discord.Interaction, dice_and_num: str, reply_is_hidden: Literal['自分のみ', '全員に見せる'] = SHOW_ME):
        """
        ダイスを振る(さいころを転がす)コマンド
        - `/roll 1d6`のように、左側にダイスの数、右側にダイスの種類(最大値)を指定してください
        """
        hidden = True if reply_is_hidden == self.SHOW_ME else False
        default_error_msg = '`/roll 1d6`のように指定してください。'
        LOG.debug(f'dice_and_num:{dice_and_num}')
        if dice_and_num is None:
            await interaction.response.send_message(default_error_msg, ephemeral=True)
            return
        dice_and_num = str(dice_and_num).lower()
        if 'd' not in dice_and_num:
            msg = 'dが必ず必要です。'
            await interaction.response.send_message(msg + default_error_msg, ephemeral=True)
            return
        list = str(dice_and_num).split('d')
        if len(list) != 2:
            await interaction.response.send_message(default_error_msg, ephemeral=True)
            return
        elif len(list) == 2:
            msg = ''
            sum = 0
            # ダイスの数、ダイスの最大値についてのチェックと数値化
            if list[0].isdecimal():
                dice_num = int(list[0])
            else:
                msg = 'dの左側が数字ではありません。'
                await interaction.response.send_message(msg + default_error_msg, ephemeral=True)
                return
            if list[1].isdecimal():
                max_num = int(list[1])
            else:
                msg = 'dの右側が数字ではありません。'
                await interaction.response.send_message(msg + default_error_msg, ephemeral=True)
                return
            if max_num < 1 or dice_num < 1:
                msg = 'dの左右は1以上である必要があります。'
                await interaction.response.send_message(msg + default_error_msg, ephemeral=True)
                return
            for i in range(dice_num):
                value = random.randint(1, max_num)
                msg += f' {value}'
                sum += value
            else:
                if dice_num > 1:
                    msg += f' → {sum}'
                await interaction.response.send_message(msg, ephemeral=hidden)

    @app_commands.command(
        name='start-ohgiri-game',
        description='大喜利を開始(親が好みのネタをカードから選んで優勝するゲーム)')
    @app_commands.describe(
        win_point='勝利扱いとするポイント(デフォルトは3ポイント)')
    async def start_ohgiriGame(self, interaction: discord.Interaction, win_point: app_commands.Range[int, 1, 20] = 3):
        """
        大喜利を開始
        - win_point: 勝利扱いとするポイント(デフォルトは3ポイント)
        """
        self.ohgiriGames[interaction.guild_id] = Ohgiri()
        self.ohgiriGames[interaction.guild_id].file_path = self.ohgiriGames['default'].file_path
        self.ohgiriGames[interaction.guild_id].win_point = win_point
        self.oh_members[interaction.guild_id] = Members()

        msg =   '大喜利を始めます(2人以上必要です)！\n参加する場合、以下のボタンを押してください。'
        self.ohgiriStart = OhrgiriStart(self.oh_members, self.ohgiriGames, msg)
        await interaction.response.send_message(msg, view=self.ohgiriStart)

    # poll機能
    @app_commands.command(
        name='simple-poll',
        description='簡易的な投票機能です(/で分割されます。「/がない」場合と「/がある」場合で動作が変わります)')
    @app_commands.describe(
        poll_message='タイトル/回答1/回答2/...のスタイルで入力ください(タイトルのみの場合、Yes/Noで投票されます)')
    async def poll(self, interaction: discord.Interaction, poll_message: str):
        """
        このコマンドを実行すると、リアクションを利用し簡易的な投票ができます。
        ＊1人1票にはできません。リアクションの制限で20を超える設問は不可能です。
        """
        usage = '/simple-pollの使い方\n複数選択（1〜20まで）: \n `/simple-poll 今日のランチは？/お好み焼き/カレーライス`\n Yes/No: \n`/poll 明日は晴れる？`'
        args_all = poll_message.split('/')
        msg = f'🗳 **{args_all[0]}**'
        await interaction.response.send_message('投票開始')
        channel = interaction.channel
        if len(args_all)  == 1:
            message = await channel.send(msg)
            await message.add_reaction('⭕')
            await message.add_reaction('❌')
        elif len(args_all) > 21:
            await interaction.response.send_message(f'複数選択の場合、引数は1〜20にしてください。（{len(args_all)-1}個与えられています。）')
        else:
            args = args_all[1:]
            embed = discord.Embed()
            for  emoji, arg in zip(POLL_CHAR, args):
                embed.add_field(name=emoji, value=arg) # inline=False
            message = await channel.send(msg, embed=embed)

            for  emoji, arg in zip(POLL_CHAR, args):
                await message.add_reaction(emoji)

async def setup(bot):
    await bot.add_cog(GameCog(bot)) # GameCogにBotを渡してインスタンス化し、Botにコグとして登録する