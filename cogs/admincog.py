import discord
from discord.ext import commands # Bot Commands Frameworkのインポート
import datetime
from .modules import settings
import traceback

# コグとして用いるクラスを定義。
class AdminCog(commands.Cog):

    # AdminCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    def __init__(self, bot):
        self.bot = bot
        self.command_author = None

    # 監査ログの取得
    @commands.command()
    async def getAuditLog(self, ctx, limit_num=None):

        if limit_num is None:
            oldest_first_flag = True
        elif limit_num.isdecimal():
            limit_num = int(limit_num)
            oldest_first_flag = False

        to_channel = ctx.guild.get_channel(settings.AUDIT_LOG_SEND_CHANNEL)

        async for entry in ctx.guild.audit_logs(limit=limit_num, oldest_first=oldest_first_flag):
                await self.sendAuditLogEntry(ctx, to_channel, entry)

    # 監査ログをチャンネルに送信
    async def sendAuditLogEntry(self, ctx, to_channel, entry):
        created_at = entry.created_at.replace(tzinfo=datetime.timezone.utc)
        created_at_jst = created_at.astimezone(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y/%m/%d(%a) %H:%M:%S')
        msg = '{1}: {0.user} did **{0.action}** to {0.target}'.format(entry, created_at_jst)

        if entry.changes is not None:
            embed = discord.Embed(title = 'entry_changes')
            embed.set_author(name="sendAuditLogEntry", url="https://github.com/tetsuya-ki/discord-bot-heroku/")

            if hasattr(entry, 'changes'):
                embed.add_field(name="changes", value=entry.changes)
            if hasattr(entry.changes.after, 'overwrites'):
                embed.add_field(name="after.overwrites", value=entry.changes.after.overwrites)
            if hasattr(entry.changes.before, 'roles'):
                embed.add_field(name="before.roles", value=entry.changes.before.roles)
            if hasattr(entry.changes.after, 'roles'):
                embed.add_field(name="after.roles", value=entry.changes.after.roles)
                print(entry.changes.after.roles)
            if hasattr(entry.changes.before, 'channel'):
                embed.add_field(name="before.channel", value=entry.changes.before.channel)
            if hasattr(entry.changes.after, 'channel'):
                embed.add_field(name="after.channel", value=entry.changes.after.channel)
        print(msg)
        print(entry.changes)
        await to_channel.send(msg, embed=embed)

    # メッセージの削除
    @commands.command()
    async def purge(self, ctx, limit_num=None):
        self.command_author = ctx.author
        if limit_num is None:
            await ctx.channel.send('オプションとして、1以上の数値を指定してください。')
            return
        if limit_num.isdecimal():
            limit_num = int(limit_num)
        else:
            limit_num = 10

        if limit_num > 100:
            limit_num = 100
        elif limit_num < 1:
            await ctx.channel.send('オプションは1以上の数値を指定してください。')
            return

        # botかコマンドの実行主かチェック
        def is_me(m):
            return self.command_author == m.author or m.author.bot

        deleted = await ctx.channel.purge(limit=limit_num, check=is_me)
        await ctx.channel.send('{0}個のメッセージを削除しました。\nあなたのコマンド：`{1}`'.format(len(deleted), ctx.message.clean_content))

    @getAuditLog.error
    async def getAuditLog_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            print(error)
            await ctx.send(error)

def setup(bot):
    bot.add_cog(AdminCog(bot)) # AdminCogにBotを渡してインスタンス化し、Botにコグとして登録する