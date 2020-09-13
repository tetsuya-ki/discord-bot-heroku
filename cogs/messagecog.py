import discord
from discord.ext import commands # Bot Commands Frameworkのインポート
from .modules.grouping import MakeTeam

POLL_CHAR = ['🇦','🇧','🇨','🇩','🇪','🇫','🇬','🇭','🇮','🇯','🇰','🇱','🇲','🇳','🇴','🇵','🇶','🇷','🇸','🇹']

# コグとして用いるクラスを定義。
class MessageCog(commands.Cog, name="通常用"):
    """
    コマンドを元に動作する機能のカテゴリ。
    """

    # MessageCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    def __init__(self, bot):
        self.bot = bot

    # メンバー数が均等になるチーム分け
    @commands.command(aliases=["tm"], description="メンバー数が均等になるように、指定された数に分けます")
    async def team(self, ctx, specified_num=2):
        """
        このコマンドを実行すると、Guildにあるボイスチャンネルの数を計測し、それぞれに接続しているメンバーのリストを作成し、指定された数に振り分けます。
        （一瞬接続は解除されますので、動画配信などもキャンセルされます）
        引数(specified_num)としてチーム数（3などの正数）を与えることができます。デフォルトは2です。
        """
        make_team = MakeTeam()
        remainder_flag = 'true'
        msg = await make_team.make_party_num(ctx, specified_num, remainder_flag)
        await ctx.channel.send(msg)

    # メンバー数を指定してチーム分け
    @commands.command(aliases=["gp"], description="指定されたメンバー数になるように、適当な数のチームに分けます")
    async def group(self, ctx, specified_num=1):
        """
        このコマンドを実行すると、Guildにあるボイスチャンネルの数を計測し、それぞれに接続しているメンバーのリストを作成し、指定された数のメンバー数になるようにチームを振り分けます。
        （一瞬接続は解除されますので、動画配信などもキャンセルされます）
        引数(specified_num)としてメンバー数（3などの正数）を与えることができます。デフォルトは1です。
        """
        make_team = MakeTeam()
        msg = await make_team.make_specified_len(ctx, specified_num)
        await ctx.channel.send(msg)

    # ボイスチャンネルに接続しているメンバーリストを取得
    @commands.command(aliases=["vcm","vm","vc","vcmember"], description="ボイスチャンネルに接続しているメンバーリストを取得します")
    async def vcmembers(self, ctx):
        """
        このコマンドを実行すると、Guildにあるボイスチャンネルの数を計測し、それぞれに接続しているメンバーのリストを作成し、チャンネルに投稿します。
        """
        make_team = MakeTeam()
        msg = await make_team.get_members(ctx)
        await ctx.channel.send(msg)

    # poll機能
    @commands.command(aliases=["p","pl"], description="簡易的な投票機能です（引数が1つの場合と2以上の場合で動作が変わります）")
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

    @team.error
    async def team_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            print(error)
            await ctx.send(error)

    @group.error
    async def group_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            print(error)
            await ctx.send(error)

def setup(bot):
    bot.add_cog(MessageCog(bot)) # MessageCogにBotを渡してインスタンス化し、Botにコグとして登録する