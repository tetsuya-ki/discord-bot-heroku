import discord
import re
import time
from discord.ext import commands  # Bot Commands Frameworkのインポート
from discord import app_commands
from typing import Literal
from .modules.grouping import MakeTeam
from .modules.radiko import Radiko, Pref
from logging import getLogger

LOG = getLogger('assistantbot')

# コグとして用いるクラスを定義。
class MessageCog(commands.Cog, name='通常用'):
    """
    コマンドを元に動作する機能のカテゴリ。
    """
    SHOW_ME = '自分のみ'
    SHOW_ALL = '全員に見せる'

    # MessageCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    def __init__(self, bot):
        self.bot = bot

    # ボイスチャンネルコマンド群
    voice_channel = app_commands.Group(name="voice-channel", description='ボイスチャンネルを操作するコマンド（サブコマンド必須）')

    # メンバー数が均等になるチーム分け
    @voice_channel.command(
        name='team',
        description='チーム数指定：メンバー数が均等になるように、指定された数に分けます')
    @app_commands.describe(
        specified_num='チーム数（3などの正数）を与えることができます。デフォルトは2です')
    async def team(self, interaction: discord.Interaction, specified_num: app_commands.Range[int, 1, 100] = 2):
        """
        このコマンドを実行すると、Guildにあるボイスチャンネルの数を計測し、それぞれに接続しているメンバーのリストを作成し、指定された数に振り分けます。
        （一瞬接続は解除されますので、動画配信などもキャンセルされます）
        引数(specified_num)としてチーム数（3などの正数）を与えることができます。デフォルトは2です。
        """
        make_team = MakeTeam(interaction.guild.me)
        remainder_flag = 'true'
        msg = await make_team.make_party_num(interaction, specified_num, remainder_flag)
        await interaction.response.send_message(msg)

    # メンバー数を指定してチーム分け
    @voice_channel.command(
        name='group',
        description='メンバー数を指定：指定されたメンバー数になるように、適当な数のチームに分けます')
    @app_commands.describe(
        specified_num='メンバー数（3などの正数）を与えることができます。デフォルトは1です。')
    async def group(self, interaction: discord.Interaction, specified_num: app_commands.Range[int, 1, 100] = 1):
        """
        このコマンドを実行すると、Guildにあるボイスチャンネルの数を計測し、それぞれに接続しているメンバーのリストを作成し、指定された数のメンバー数になるようにチームを振り分けます。
        （一瞬接続は解除されますので、動画配信などもキャンセルされます）
        引数(specified_num)としてメンバー数（3などの正数）を与えることができます。デフォルトは1です。
        """
        make_team = MakeTeam(interaction.guild.me)
        msg = await make_team.make_specified_len(interaction, specified_num)
        await interaction.response.send_message(msg)

    # ボイスチャンネルに接続しているメンバーリストを取得
    @voice_channel.command(
        name='members',
        description='ボイスチャンネルに接続しているメンバーリストを取得します')
    async def vcmembers(self, interaction: discord.Interaction):
        """
        このコマンドを実行すると、Guildにあるボイスチャンネルの数を計測し、それぞれに接続しているメンバーのリストを作成し、チャンネルに投稿します。
        """
        make_team = MakeTeam(interaction.guild.me)
        msg = await make_team.get_members(interaction)
        await interaction.response.send_message(msg)

    @app_commands.command(
        name='radiko-search',
        description='Radikoの番組表を検索する機能です')
    @app_commands.describe(
        keyword='検索する対象')
    @app_commands.describe(
        filter='検索対象。過去(past)、未来(future)を検索対象とします。未指定か不明な場合、allが採用')
    @app_commands.describe(
        area='地域。XX県かJP01(数字は県番号)と指定すると、その地域の番組表を検索します。未指定か不明の場合はデフォルトの地域が採用')
    @app_commands.describe(
        start_day='開始日時。1桁の数字(日後と解釈)、2桁の数字(日付と解釈)、4桁の数字(月日と解釈)と指定すると、開始日時を設定')
    @app_commands.describe(
        end_day='開始日時。1桁の数字(日後と解釈)、2桁の数字(日付と解釈)、4桁の数字(月日と解釈)と指定すると、開始日時を設定')
    @app_commands.describe(
        reply_is_hidden='Botの実行結果を全員に見せるどうか(デフォルトは全員に見せる)')
    async def radiko_search(self,
                    interaction: discord.Interaction,
                    keyword: str,
                    filter: Literal['過去', '未来', 'すべて'] = 'すべて',
                    area: Pref = Pref.東京都,
                    start_day: app_commands.Range[int, 0, 1231] = None,
                    end_day: app_commands.Range[int, 0, 1231] = None,
                    reply_is_hidden: Literal['自分のみ', '全員に見せる'] = SHOW_ME):
        """
        このコマンドを実行すると、日付を指定してRadikoの番組表を検索することができます。
        1番目の引数(キーワード): 検索する対象。
        2番目の引数(検索対象): 過去(past)、未来(future)を検索対象とします。未指定か不明な場合、allが採用されます。
        3番目の引数(地域): XX県かJP01(数字は県番号)と指定すると、その地域の番組表を検索します。未指定か不明の場合はデフォルトの地域が採用されます。
        4番目の引数(開始日時): 1桁の数字(日後と解釈)、2桁の数字(日付と解釈)、4桁の数字(月日と解釈)と指定すると、開始日時を設定します。
        5番目の引数(終了日時: 1桁の数字(日後と解釈)、2桁の数字(日付と解釈)、4桁の数字(月日と解釈)と指定すると、終了日時を設定します。
        ＊あんまり検索結果が多いと困るので、一旦5件に制限しています。
        """
        usage = '/radikoSearch withDateの使い方\n 例:`/radikoSearch withDate 福山雅治 東京都 stoday etoday`\n**日付を指定して**Radikoの番組表を検索した結果（件数や番組の時間など）をチャンネルへ投稿します。詳しい使い方は`/help radikoSearch withDate`で調べてください'
        hidden = True if reply_is_hidden == self.SHOW_ME else False
        radiko = Radiko()
        embed = await radiko.radiko_search(keyword, filter, area.value, start_day, end_day)
        if not radiko.r_err:
            await interaction.response.send_message(content=radiko.content, embed=embed, ephemeral=hidden)
        else:
            await interaction.response.send_message(radiko.r_err, ephemeral=True)

    @app_commands.command(
        name='count-message',
        description='メッセージの件数を取得する機能です(けっこう時間かかります)')
    @app_commands.describe(
        all_flg='全て取得するかどうか')
    @app_commands.describe(
        channel='取得対象のチャンネル(特定の場合のみ指定)')
    @app_commands.describe(
        count_numbers='集計件数を指定(チャンネルごとに読み込む件数。大きいほど遅くなる)')
    @app_commands.describe(
        ranking_num='集計順位を指定(指定された順位まで表示)')
    @app_commands.describe(
        reply_is_hidden='Botの実行結果を全員に見せるどうか(デフォルトは全員に見せる)')
    async def countMessage(self,
                        interaction: discord.Interaction,
                        all_flg: Literal['すべて', 'ひとつ'] = 'ひとつ',
                        channel: discord.TextChannel = None,
                        count_numbers: app_commands.Range[int, 1, 99999] = 99999,
                        ranking_num: app_commands.Range[int, 1, 100] = 5,
                        reply_is_hidden: Literal['自分のみ', '全員に見せる'] = SHOW_ME):
        """
        ギルドのチャンネルのメッセージを集計する機能です。それぞれのパーセンテージと件数を表示します。
        """
        hidden = True if reply_is_hidden == self.SHOW_ME else False
        start_time = time.time()
        # 集計対象のチャンネルを設定(すべてが選択された場合は全て。チャンネル未指定はコマンド実行チャンネル。指定時はそのチャンネル)
        if all_flg == 'すべて':
            count_channels = self.get_target_channels(interaction, 'all')
        elif channel is None:
            count_channels = self.get_target_channels(interaction, None)
        else:
            count_channels = [channel]

        await interaction.response.defer()
        # 集計作業
        target = {}
        all_num = 0
        sep_channels = ''
        for count_channel in count_channels:
            try:
                async for message in count_channel.history(limit=count_numbers):
                    all_num = all_num + 1
                    if message.author in target:
                        target[message.author] = target[message.author] + 1
                    else:
                        target[message.author] = 1
                sep_channels += count_channel.name + ','
            except:
                continue

        target_sorted = sorted(target.items(), key=lambda x:x[1], reverse=True)
        message = f'メッセージ集計結果です(総件数:' + '{:,}'.format(all_num) + ')。\n'
        for rank, ranking_target in enumerate(target_sorted):
            percent = '{:.2%}'.format(ranking_target[1] / all_num)
            message += f'{rank+1}位: {ranking_target[0].display_name}さん {percent}(' + '{:,}'.format(ranking_target[1]) + '件)\n'
            if rank + 1 >= ranking_num:
                break

        sep_channels = re.sub(r',$', '', sep_channels)
        message += f'(集計チャンネル({len(count_channels)}件): {sep_channels})\n'

        elapsed_time = time.time() - start_time
        elapsed_time_text = '経過時間:{:.2f}'.format(elapsed_time) + '[sec]'
        LOG.info(f'{sep_channels}({count_numbers}件) → {elapsed_time_text}')
        message += elapsed_time_text

        await interaction.followup.send(message, ephemeral=hidden)

    @app_commands.command(
        name='count-reaction',
        description='リアクションの件数を取得する機能です(けっこう時間かかります)')
    @app_commands.describe(
        all_flg='全て取得するかどうか')
    @app_commands.describe(
        channel='取得対象のチャンネル(特定の場合のみ指定)')
    @app_commands.describe(
        count_numbers='集計件数を指定(チャンネルごとに読み込む件数。大きいほど遅くなる)')
    @app_commands.describe(
        ranking_num='集計順位を指定(指定された順位まで表示(')
    @app_commands.describe(
        reply_is_hidden='Botの実行結果を全員に見せるどうか(デフォルトは全員に見せる)')
    async def countReaction(self,
                        interaction: discord.Interaction,
                        all_flg: Literal['すべて', 'ひとつ'] = 'ひとつ',
                        channel: discord.TextChannel = None,
                        count_numbers: app_commands.Range[int, 1, 99999] = 99999,
                        ranking_num: app_commands.Range[int, 1, 100] = 5,
                        reply_is_hidden: Literal['自分のみ', '全員に見せる'] = SHOW_ME):
        """
        ギルドのチャンネルのリアクションを集計する機能です。それぞれのパーセンテージと件数を表示します。
        """
        hidden = True if reply_is_hidden == self.SHOW_ME else False
        start_time = time.time()
        # 集計対象のチャンネルを設定(すべてが選択された場合は全て。チャンネル未指定はコマンド実行チャンネル。指定時はそのチャンネル)
        if all_flg == 'すべて':
            count_channels = self.get_target_channels(interaction, 'all')
        elif channel is None:
            count_channels = self.get_target_channels(interaction, None)
        else:
            count_channels = [channel]

        await interaction.response.defer()
        # 集計作業
        target = {}
        all_num = 0
        sep_channels = ''
        for count_channel in count_channels:
            try:
                async for message in count_channel.history(limit=count_numbers):
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
        message = f'リアクション集計結果です(総件数:' + '{:,}'.format(all_num) + ')。\n'
        for rank, ranking_target in enumerate(target_sorted):
            percent = '{:.2%}'.format(ranking_target[1] / all_num)
            message += f'{rank+1}位: {ranking_target[0]} → {percent}(' + '{:,}'.format(ranking_target[1]) + '件)\n'
            if rank + 1 >= ranking_num:
                break

        sep_channels = re.sub(r',$', '', sep_channels)
        message += f'(集計チャンネル({len(count_channels)}件): {sep_channels})\n'

        elapsed_time = time.time() - start_time
        elapsed_time_text = '経過時間:{:.2f}'.format(elapsed_time) + '[sec]'
        LOG.info(f'{sep_channels}({count_numbers}件) → {elapsed_time_text}')
        message += elapsed_time_text

        await interaction.followup.send(message, ephemeral=hidden)

    def get_target_channels(self, interaction, channel_name):
        if channel_name is None:
            count_channels = [interaction.channel]
        elif str(channel_name).lower() == 'all':
            count_channels = interaction.guild.text_channels
        return count_channels

async def setup(bot):
    await bot.add_cog(MessageCog(bot)) # MessageCogにBotを渡してインスタンス化し、Botにコグとして登録する