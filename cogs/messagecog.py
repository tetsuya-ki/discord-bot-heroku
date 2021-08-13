from discord.ext import commands  # Bot Commands Frameworkのインポート
from .modules.grouping import MakeTeam
from .modules.radiko import Radiko
from .modules import settings
from logging import getLogger

import discord
import re
import time

logger = getLogger(__name__)

POLL_CHAR = ['🇦','🇧','🇨','🇩','🇪','🇫','🇬','🇭','🇮','🇯','🇰','🇱','🇲','🇳','🇴','🇵','🇶','🇷','🇸','🇹']

# コグとして用いるクラスを定義。
class MessageCog(commands.Cog, name='通常用'):
    """
    コマンドを元に動作する機能のカテゴリ。
    """
    DEFAULT_NUMBER = 4000
    MAX_NUMBER = 10000
    MAX_RANK = 20

    # MessageCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    def __init__(self, bot):
        self.bot = bot

    # メンバー数が均等になるチーム分け
    @commands.command(aliases=['t','tm'], description='チーム数指定：メンバー数が均等になるように、指定された数に分けます')
    async def team(self, ctx, specified_num=2):
        """
        このコマンドを実行すると、Guildにあるボイスチャンネルの数を計測し、それぞれに接続しているメンバーのリストを作成し、指定された数に振り分けます。
        （一瞬接続は解除されますので、動画配信などもキャンセルされます）
        引数(specified_num)としてチーム数（3などの正数）を与えることができます。デフォルトは2です。
        """
        make_team = MakeTeam(ctx.guild.me)
        remainder_flag = 'true'
        msg = await make_team.make_party_num(ctx, specified_num, remainder_flag)
        await ctx.channel.send(msg)

    # メンバー数を指定してチーム分け
    @commands.command(aliases=['g','gp'], description='メンバー数を指定：指定されたメンバー数になるように、適当な数のチームに分けます')
    async def group(self, ctx, specified_num=1):
        """
        このコマンドを実行すると、Guildにあるボイスチャンネルの数を計測し、それぞれに接続しているメンバーのリストを作成し、指定された数のメンバー数になるようにチームを振り分けます。
        （一瞬接続は解除されますので、動画配信などもキャンセルされます）
        引数(specified_num)としてメンバー数（3などの正数）を与えることができます。デフォルトは1です。
        """
        make_team = MakeTeam(ctx.guild.me)
        msg = await make_team.make_specified_len(ctx, specified_num)
        await ctx.channel.send(msg)

    # ボイスチャンネルに接続しているメンバーリストを取得
    @commands.command(aliases=['v','vcm','vm','vc','vcmember'], description='ボイスチャンネルに接続しているメンバーリストを取得します')
    async def vcmembers(self, ctx):
        """
        このコマンドを実行すると、Guildにあるボイスチャンネルの数を計測し、それぞれに接続しているメンバーのリストを作成し、チャンネルに投稿します。
        """
        make_team = MakeTeam(ctx.guild.me)
        msg = await make_team.get_members(ctx)
        await ctx.channel.send(msg)

    # poll機能
    @commands.command(aliases=['p','pl'], description='簡易的な投票機能です（引数が1つの場合と2以上の場合で動作が変わります）')
    async def poll(self, ctx, arg1=None, *args):
        """
        このコマンドを実行すると、リアクションを利用し簡易的な投票ができます。
        ＊1人1票にはできません。リアクションの制限で20を超える設問は不可能です。
        """
        usage = '/pollの使い方\n複数選択（1〜20まで）: \n `/poll 今日のランチは？ お好み焼き カレーライス`\n Yes/No: \n`/poll 明日は晴れる？`'
        msg = f'🗳 **{arg1}**'

        if arg1 is None:
            await ctx.channel.send(usage)
        elif len(args) == 0:
            message = await ctx.channel.send(msg)
            await message.add_reaction('⭕')
            await message.add_reaction('❌')
        elif len(args) > 20:
            await ctx.channel.send(f'複数選択の場合、引数は1〜20にしてください。（{len(args)}個与えられています。）')
        else:
            embed = discord.Embed()
            for  emoji, arg in zip(POLL_CHAR, args):
                embed.add_field(name=emoji, value=arg) # inline=False
            message = await ctx.channel.send(msg, embed=embed)

            for  emoji, arg in zip(POLL_CHAR, args):
                await message.add_reaction(emoji)

    @commands.group(aliases=['rs','radiko','radikoKensaku','rk'], description='Radikoの番組表を検索する機能(サブコマンド必須)です')
    async def radikoSearch(self, ctx):
        """
        ラジコの番組表を検索するコマンド群です。このコマンドだけでは検索しません。半角スペースの後、続けて以下のサブコマンドを入力ください。
        - 普通に検索したい場合は、`normal`(または`n`)を入力し、キーワード等を指定してください。
        - 日付を指定して検索したい場合は、`withDate`(または`w`)を入力し、キーワード等を指定(開始日付は**s**を付与し、終了日付は**e**を付与(片方のみ指定可))してください。
        """
        if ctx.invoked_subcommand is None:
            await ctx.send('このコマンドにはサブコマンドが必要です(普通に検索したい場合は`n`をつけて、日付指定は`w`をつけてください)')

    @radikoSearch.command(aliases=['norm', 'n'], description='Radikoの番組表を検索する機能です')
    async def normal(self, ctx, *args):
        """
        このコマンドを実行すると、Radikoの番組表を検索することができます。
        1番目の引数(キーワード): 検索する対象。**半角スペースがある場合、"(二重引用符)で囲って**ください。
        2番目の引数(検索対象): 過去(past)、未来(future)を検索対象とします。未指定か不明な場合、allが採用されます
        3番目の引数(地域): XX県かJP01(数字は県番号)と指定すると、その地域の番組表を検索します。未指定か不明の場合はデフォルトの地域が採用されます。
        ＊あんまり検索結果が多いと困るので、一旦5件に制限しています。
        """
        usage = '/radikoSearch normalの使い方\n 例:`/radikoSearch normal 福山雅治 東京都`\nRadikoの番組表を検索した結果（件数や番組の時間など）をチャンネルへ投稿します。詳しい使い方は`/help radikoSearch normal`で調べてください'

        # 引数の数をチェック
        if len(args) == 0:
            await ctx.channel.send(usage)
        elif len(args) > 3:
            await ctx.channel.send(f'引数は３件までです！\n{usage}')
        else:
            radiko = Radiko()
            embed = await radiko.radiko_search(*args)
            if not radiko.r_err:
                await ctx.channel.send(content=radiko.content, embed=embed)
            else:
                await ctx.channel.send(radiko.r_err)

    @radikoSearch.command(aliases=['with','date','w','wd'], description='Radikoの番組表を日付指定で検索する機能です')
    async def withDate(self, ctx, *args):
        """
        このコマンドを実行すると、日付を指定してRadikoの番組表を検索することができます。
        1番目の引数(キーワード)、2番目の引数(検索対象)、3番目の引数(地域)は`radikoSearch normal`と同じ
        4番目の引数(開始日時): sに続けて、today、1桁の数字(日後と解釈)、2桁の数字(日付と解釈)、4桁の数字(月日と解釈)と指定すると、開始日時を設定します。
        5番目の引数(終了日時: eに続けて、today、1桁の数字(日後と解釈)、2桁の数字(日付と解釈)、4桁の数字(月日と解釈)と指定すると、終了日時を設定します。
        ＊あんまり検索結果が多いと困るので、一旦5件に制限しています。
        """
        usage = '/radikoSearch withDateの使い方\n 例:`/radikoSearch withDate 福山雅治 東京都 stoday etoday`\n**日付を指定して**Radikoの番組表を検索した結果（件数や番組の時間など）をチャンネルへ投稿します。詳しい使い方は`/help radikoSearch withDate`で調べてください'

        # 引数の数をチェック
        if len(args) == 0:
            await ctx.channel.send(usage)
        elif len(args) > 5:
            await ctx.channel.send(f'引数は５件までです！\n{usage}')
        else:
            radiko = Radiko()
            start_day = ''
            end_day = ''

            # 引数の準備(開始日時、終了日時)
            arg_list = []
            for tmp in args:
                tmp = tmp.lower()
                if tmp.startswith('s'):
                    start_day = tmp.split('s')[1]
                elif tmp.startswith('e'):
                    end_day = tmp.split('e')[1]
                else:
                    arg_list.append(tmp)

            if len(arg_list) == 0:
                await ctx.channel.send(f'開始日付、終了日付以外の引数がありません\n{usage}')
            elif len(arg_list) > 3:
                await ctx.channel.send(f'開始日付、終了日付以外の引数が３件を超えています\n{usage}')
            else:
                # 引数の設定(開始日時、終了日時を含めたもの)
                while len(arg_list) < 3:
                    arg_list.append('')
                arg_list.append(start_day)
                arg_list.append(end_day)

                embed = await radiko.radiko_search(*arg_list)
                if not radiko.r_err:
                    await ctx.channel.send(content=radiko.content, embed=embed)
                else:
                    await ctx.channel.send(radiko.r_err)

    @commands.command(aliases=['cm','countm'], description='メッセージの件数を取得する機能です(けっこう時間かかります)')
    async def countMessage(self, ctx, channel_name=None, numbers=None):
        """
        ギルドのチャンネルのメッセージを集計する機能です。それぞれのパーセンテージと件数を表示します。
        - channel_name: 集計対象のチャンネル(allの場合全部、未指定はコマンド実行チャンネル)
        - numbers: 集計件数を指定
        """
        start_time = time.time()
        # 集計対象のチャンネルを設定
        count_channels = self.get_target_channels(ctx, channel_name)

        # 集計件数を設定
        if numbers is None or not str(numbers).isdecimal():
            numbers = self.DEFAULT_NUMBER
        elif str(numbers).isdecimal():
            numbers = int(numbers)
            if numbers > self.MAX_NUMBER:
                numbers = self.MAX_NUMBER

        # ランキングの数を設定
        ranking_num = settings.COUNT_RANK_SETTING
        if settings.COUNT_RANK_SETTING > self.MAX_RANK:
            ranking_num = self.MAX_RANK

        # 集計作業
        target = {}
        all_num = 0
        sep_channels = ''
        for count_channel in count_channels:
            try:
                async for message in count_channel.history(limit=numbers):
                    all_num = all_num + 1
                    if message.author in target:
                        target[message.author] = target[message.author] + 1
                    else:
                        target[message.author] = 1
                sep_channels += count_channel.name + ','
            except:
                continue

        target_sorted = sorted(target.items(), key=lambda x:x[1], reverse=True)
        message = f'`{ctx.message.clean_content}`の結果です(総件数:' + '{:,}'.format(all_num) + ')。\n'
        for rank, ranking_target in enumerate(target_sorted):
            percent = '{:.2%}'.format(ranking_target[1] / all_num)
            message += f'{rank+1}位: {ranking_target[0].display_name}さん {percent}(' + '{:,}'.format(ranking_target[1]) + '件)\n'
            if rank + 1 >= ranking_num:
                break

        sep_channels = re.sub(r',$', '', sep_channels)
        message += f'(集計チャンネル: {sep_channels})\n'

        elapsed_time = time.time() - start_time
        elapsed_time_text = '経過時間:{:.2f}'.format(elapsed_time) + '[sec]'
        logger.info(f'{sep_channels}({numbers}件) → {elapsed_time_text}')
        message += elapsed_time_text

        await ctx.send(message)

    @commands.command(aliases=['cr','countr'], description='リアクションの件数を取得する機能です')
    async def countReaction(self, ctx, channel_name=None, numbers=None):
        """
        ギルドのチャンネルのリアクションを集計する機能です。それぞれのパーセンテージと件数を表示します。
        - channel_name: 集計対象のチャンネル(allの場合全部、未指定はコマンド実行チャンネル)
        - numbers: 集計件数を指定
        """
        start_time = time.time()
        # 集計対象のチャンネルを設定
        count_channels = self.get_target_channels(ctx, channel_name)

        # 集計件数を設定
        if numbers is None or not str(numbers).isdecimal():
            numbers = self.DEFAULT_NUMBER
        elif str(numbers).isdecimal():
            numbers = int(numbers)
            if numbers > self.MAX_NUMBER:
                numbers = self.MAX_NUMBER

        # ランキングの数を設定
        ranking_num = settings.COUNT_RANK_SETTING
        if settings.COUNT_RANK_SETTING > self.MAX_RANK:
            ranking_num = self.MAX_RANK

        # 集計作業
        target = {}
        all_num = 0
        sep_channels = ''
        for count_channel in count_channels:
            try:
                async for message in count_channel.history(limit=numbers):
                    for reaction in message.reactions:
                        all_num = all_num + reaction.count
                        if reaction.emoji in target:
                            target[reaction.emoji] = target[reaction.emoji] + reaction.count
                        else:
                            target[reaction.emoji] = reaction.count
                sep_channels += count_channel.name + ','
            except:
                continue

        target_sorted = sorted(target.items(), key=lambda x:x[1], reverse=True)
        message = f'`{ctx.message.clean_content}`の結果です(総件数:' + '{:,}'.format(all_num) + ')。\n'
        for rank, ranking_target in enumerate(target_sorted):
            percent = '{:.2%}'.format(ranking_target[1] / all_num)
            message += f'{rank+1}位: {ranking_target[0]} → {percent}(' + '{:,}'.format(ranking_target[1]) + '件)\n'
            if rank + 1 >= ranking_num:
                break

        sep_channels = re.sub(r',$', '', sep_channels)
        message += f'(集計チャンネル: {sep_channels})\n'

        elapsed_time = time.time() - start_time
        elapsed_time_text = '経過時間:{:.2f}'.format(elapsed_time) + '[sec]'
        logger.info(f'{sep_channels}({numbers}件) → {elapsed_time_text}')
        message += elapsed_time_text

        await ctx.send(message)

    def get_target_channels(self, ctx, channel_name):
        if channel_name is None:
            count_channels = [ctx.channel]
        elif str(channel_name).lower() == 'all':
            count_channels = ctx.guild.text_channels
        else:
            channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)

            # 名前でchannelが取得できなかった場合の処理
            if channel is None:
                # チャンネルID指定 <#\d+>の場合、IDからチャンネルを取得。それでも無理なら今のチャンネルを指定
                channel_id = re.sub(r'[<#>]', '', channel_name)
                if channel_id.isdecimal() and '#' in channel_name:
                    channel_id = int(channel_id)
                    count_channels = [ctx.guild.get_channel(channel_id)]
                else:
                    count_channels = [ctx.channel]
            # 名前で取得できた場合の処理
            else:
                count_channels = [channel]
        return count_channels

    @team.error
    async def team_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            logger.error(error)
            await ctx.send(error)

    @group.error
    async def group_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            logger.error(error)
            await ctx.send(error)

    @radikoSearch.error
    async def radikoSearch_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            logger.error(error)
            await ctx.send(error)

def setup(bot):
    bot.add_cog(MessageCog(bot)) # MessageCogにBotを渡してインスタンス化し、Botにコグとして登録する