from discord.ext import commands # Bot Commands Frameworkのインポート
from .modules.grouping import MakeTeam

# コグとして用いるクラスを定義。
class MessageCog(commands.Cog):

    # MessageCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hello(self, ctx):
        await ctx.channel.send('Hello!')

    # メンバー数が均等になるチーム分け
    @commands.command()
    async def team(self, ctx, specified_num=2):
        make_team = MakeTeam()
        remainder_flag = 'true'
        msg = await make_team.make_party_num(ctx, specified_num, remainder_flag)
        await ctx.channel.send(msg)

    # メンバー数を指定してチーム分け
    @commands.command()
    async def group(self, ctx, specified_num=1):
        make_team = MakeTeam()
        msg = await make_team.make_specified_len(ctx, specified_num)
        await ctx.channel.send(msg)

def setup(bot):
    bot.add_cog(MessageCog(bot)) # MessageCogにBotを渡してインスタンス化し、Botにコグとして登録する