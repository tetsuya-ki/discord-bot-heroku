import asyncio
import random
import discord
from discord.ext import commands # Bot Commands Frameworkのインポート
from .modules.grouping import MakeTeam
from .modules.readjson import ReadJson

# コグとして用いるクラスを定義。
class GameCog(commands.Cog, name='ゲーム用'):
    """
    ゲーム機能のカテゴリ。
    """
    MAX_TIME = 10
    DEFAULT_TIME = 2

    # GameCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    def __init__(self, bot):
        self.bot = bot

    # ワードウルフ機能
    @commands.command(aliases=['word','ww'], description='ワードウルフ機能(少数派のワードを当てるゲーム)')
    async def wordWolf(self, ctx, answer_minutes=None):
        """
        コマンド実行者が参加しているボイスチャンネルでワードウルフ始めます（BOTからDMが来ますがびっくりしないでください）
        引数(answer_minutes)として投票開始までの時間（3などの正数。単位は「分」）を与えることができます。デフォルトは2分です。
        """
        make_team = MakeTeam()
        make_team.my_connected_vc_only_flg = True
        await make_team.get_members(ctx)

        if make_team.mem_len < 3:
            msg = f'ワードウルフを楽しむには3人以上のメンバーが必要です(現在、{make_team.mem_len}人しかいません)'
            await ctx.send(msg)
            return

        if answer_minutes is None:
            answer_minutes = self.DEFAULT_TIME
        elif answer_minutes.isdecimal():
            answer_minutes = int(answer_minutes)
        else:
            answer_minutes = self.DEFAULT_TIME

        if answer_minutes > self.MAX_TIME:
            msg = f'ワードウルフはそんなに長い時間するものではないです(現在、{answer_minutes}分を指定しています。{self.MAX_TIME}分以内にして下さい)'
            await ctx.send(msg)
            return

        # ファイルを読み込み、ワードウルフ用のデータを作成
        read_json = ReadJson()
        read_json.readJson()

        #　お題の選定
        choiced_item = random.choice(read_json.list)
        odai = read_json.dict[choiced_item]
        citizen_odai, wolf_odai = random.sample(odai, 2)

        # ワードウルフの数設定
        wolf_numbers = make_team.mem_len // 3
        msg =   f'ワードウルフを始めます！　この中に、**{wolf_numbers}人のワードウルフ**が紛れ込んでいます。\n'\
                f'投票でワードウルフを当てることができたら、市民の勝ち。間違えて「市民をワードウルフ」だと示してしまった場合、ワードウルフの勝ちです！！\n'\
                f'DMに送られたお題を確認し、**{answer_minutes}分話し合いののち、投票を実施**してください！！　今から開始します！'
        await ctx.send(msg)

        # メンバーをシャッフル
        random.shuffle(make_team.vc_members)
        netabare_msg = f'**ワードウルフのお題は||「{wolf_odai}」||**でした！\nワードウルフは'

        # それぞれに役割をDMで送信
        for player in make_team.vc_members:
            if wolf_numbers > 0:
                player_odai = wolf_odai
                wolf_numbers = wolf_numbers - 1
                netabare_msg += f'||{player.display_name}||さん '
            else:
                player_odai = citizen_odai
            dm = await player.create_dm()
            await dm.send(f'{player.mention}さんのワードは**「{player_odai}」**です！')

        netabare_msg += 'でした！　お疲れ様でした！'

        # ワードウルフのネタバレメッセージを作成し、チャンネルに貼り付け
        await asyncio.sleep(answer_minutes * 60)
        await ctx.send(netabare_msg)

    @wordWolf.error
    async def wordWolf_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            print(error)
            await ctx.send(error)

def setup(bot):
    bot.add_cog(GameCog(bot)) # GameCogにBotを渡してインスタンス化し、Botにコグとして登録する