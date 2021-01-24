from discord.ext import commands  # Bot Commands Frameworkのインポート
from .modules.grouping import MakeTeam
from .modules.readjson import ReadJson
from logging import getLogger

import asyncio
import random
import re

logger = getLogger(__name__)

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
    @commands.command(aliases=['word','ww'], description='ワードウルフ機能(少数派のワードを与えられた人を当てるゲーム)')
    async def wordWolf(self, ctx, answer_minutes=None):
        """
        コマンド実行者が参加しているボイスチャンネルでワードウルフ始めます（BOTからDMが来ますがびっくりしないでください）
        引数(answer_minutes)として投票開始までの時間（3などの正数。単位は「分」）を与えることができます。デフォルトは2分です。
        3人増えるごとにワードウルフは増加します(3−5人→ワードウルフは1人、6−8人→ワードウルフは2人)
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
        msg =   f'ワードウルフを始めます！　この中に、**{wolf_numbers}人のワードウルフ**が紛れ込んでいます(本人も知りません！)。\n'\
                f'DMでお題が配られますが、**ワードウルフだけは別のお題**が配られます(お題は2種類あります)。会話の中で不審な言動を察知し、みごとに'\
                f'投票でワードウルフを当てることができたら、市民の勝ち。**間違えて「市民をワードウルフ」だと示してしまった場合、ワードウルフの勝ち**です！！\n'\
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

        voting_msg = '投票の時間が近づいてきました。下記のメッセージで投票をお願いします。\n'\
                    '`/poll 誰がワードウルフ？'
        for player in make_team.vc_members:
            voting_msg += f' {player.display_name}'
        voting_msg += '`'

        # 投票のお願いメッセージを作成し、チャンネルに貼り付け
        voting_time = answer_minutes * 50
        await self.delayedMessage(ctx, voting_msg, voting_time)

        # ワードウルフのネタバレメッセージを作成し、チャンネルに貼り付け
        await self.delayedMessage(ctx, netabare_msg, (answer_minutes * 60) - voting_time)

    # NGワードゲーム機能
    @commands.command(aliases=['ngword','ngw','ngwg', 'ngg'], description='NGワードゲーム機能(禁止された言葉を喋ってはいけないゲーム)')
    async def ngWordGame(self, ctx, answer_minutes=None):
        """
        コマンド実行者が参加しているボイスチャンネルでNGワードゲームを始めます（BOTからDMが来ますがびっくりしないでください）
        引数(answer_minutes)として終了までの時間（3などの正数。単位は「分」）を与えることができます。デフォルトは2分です。
        """
        make_team = MakeTeam()
        make_team.my_connected_vc_only_flg = True
        await make_team.get_members(ctx)

        if make_team.mem_len < 2:
            msg = f'NGワードゲームを楽しむには2人以上のメンバーが必要です(現在、{make_team.mem_len}人しかいません)'
            await ctx.send(msg)
            return

        if answer_minutes is None:
            answer_minutes = self.DEFAULT_TIME
        elif answer_minutes.isdecimal():
            answer_minutes = int(answer_minutes)
        else:
            answer_minutes = self.DEFAULT_TIME

        if answer_minutes > self.MAX_TIME:
            msg = f'NGワードゲームはそんなに長い時間するものではないです(現在、{answer_minutes}分を指定しています。{self.MAX_TIME}分以内にして下さい)'
            await ctx.send(msg)
            return

        # ファイルを読み込み、NGワードゲーム用のデータを作成(ワードウルフの語彙を流用)
        read_json = ReadJson()
        read_json.readJson()

        msg =   f'NGワードゲームを始めます！　DMでそれぞれのNGワードを配りました！(**自分のNGワードのみ分かりません**)\n'\
                f'これから**雑談し、誰かがNGワードを口走ったら、「ドーン！！！」と指摘**してください。すぐさまNGワードが妥当か話し合いください(カッコがある場合は、どちらもNGワードです)。\n'\
                f'妥当な場合、NGワード発言者はお休みです。残った人で続けます。**最後のひとりになったら勝利**です！！\n'\
                f'まず、DMに送られたNGワードを確認し、相手が「NGワードを喋ってしまう」ようにトークしてください！**{answer_minutes}分で終了**です！　今から開始します！！'
        await ctx.send(msg)

        netabare_msg = ''
        # それぞれに役割をDMで送信
        for player in make_team.vc_members:
            #　お題の選定
            choiced_item = random.choice(read_json.list)
            odai = read_json.dict[choiced_item]
            ngword = random.choice(odai)
            netabare_msg += f'{player.display_name}さん:||{ngword}||, '

        for player in make_team.vc_members:
            dm = await player.create_dm()
            rpl_msg_del = f'{player.display_name}さん:(\|\|.+?\|\|, )'
            dm_msg = re.sub(rpl_msg_del, '', netabare_msg)
            dm_msg_open = dm_msg.replace('|', '').replace(', ', '\n')
            await dm.send(f'{player.mention}さん 他の人のNGワードはこちらです！\n{dm_msg_open}')

        netabare_msg = re.sub(', $', '', netabare_msg)

        # NGワードゲームのネタバレメッセージを作成し、チャンネルに貼り付け
        await self.delayedMessage(ctx, 'NGワードゲームのネタバレです！\nそれぞれ、' + netabare_msg + 'でした！', answer_minutes * 60)

    @wordWolf.error
    async def wordWolf_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            logger.error(error)
            await ctx.send(error)

    @ngWordGame.error
    async def ngWordGame_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            logger.error(error)
            await ctx.send(error)

    async def delayedMessage(self, ctx, messsage, delayed_seconds=None):
        await asyncio.sleep(delayed_seconds)
        await ctx.send(messsage)

def setup(bot):
    bot.add_cog(GameCog(bot)) # GameCogにBotを渡してインスタンス化し、Botにコグとして登録する