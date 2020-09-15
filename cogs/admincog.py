import discord
from discord.ext import commands # Bot Commands Frameworkのインポート
import datetime
from .modules import settings
import traceback

# コグとして用いるクラスを定義。
class AdminCog(commands.Cog, name='管理用'):
    """
    管理用の機能です。
    """
    # AdminCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    def __init__(self, bot):
        self.bot = bot
        self.command_author = None

    # 監査ログの取得
    @commands.command(aliases=['getal','auditlog','gal'],description='監査ログを取得します')
    async def getAuditLog(self, ctx, limit_num=None):
        """
        監査ログを取得します。ただし、とても読みづらい形式です。。。
        引数が未指定の場合、古いものを先頭に3,000件分取得し、チャンネルに投稿します。
        引数が指定された場合、新しいものを先頭に指定された件数取得し、チャンネルに投稿します。
        """
        first_entry_times = 0
        oldest_first_flag = True
        audit_log = 0

        if limit_num is None:
            limit_num = 3000
            oldest_first_flag = True
            first_entry_times = first_entry_times + 1
        elif limit_num.isdecimal():
            limit_num = int(limit_num)
            oldest_first_flag = False

        to_channel = ctx.guild.get_channel(settings.AUDIT_LOG_SEND_CHANNEL)
        start = f'start getAuditLog ({audit_log}回で開始)'

        if (settings.IS_DEBUG):
            print(f'oldest_first_flag:{oldest_first_flag}')
            print(f'limit_num:{limit_num}')
            await to_channel.send(start)

        print(start)
        first_entry_list = await ctx.guild.audit_logs(limit=1, oldest_first=oldest_first_flag).flatten()
        first_entry = first_entry_list[0]
        if (settings.IS_DEBUG):
            print(f'{audit_log}: (fet:{first_entry_times}) {first_entry}')

        async for entry in ctx.guild.audit_logs(limit=limit_num, oldest_first=oldest_first_flag):
            if first_entry.id == entry.id:
                first_entry_times = first_entry_times + 1

            audit_log = audit_log + 1
            await self.sendAuditLogEntry(ctx, to_channel, entry, audit_log)

            if (settings.IS_DEBUG):
                print(f'{audit_log}: (fet:{first_entry_times}) {entry}')

            if first_entry_times > 1:
                break

        end = f'end getAuditLog ({audit_log}回で終了)'
        if (settings.IS_DEBUG):
            await to_channel.send(end)
        print(end)

    # 監査ログをチャンネルに送信
    async def sendAuditLogEntry(self, ctx, to_channel, entry, audit_log_times):
        created_at = entry.created_at.replace(tzinfo=datetime.timezone.utc)
        created_at_jst = created_at.astimezone(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y/%m/%d(%a) %H:%M:%S')
        msg = '{1}: {0.user} did **{0.action}** to {0.target}'.format(entry, created_at_jst)
        embed = None

        if entry.changes is not None:
            embed = discord.Embed(title = 'entry_changes', description = f'entry.id: {entry.id}, audit_log_times: {audit_log_times}')
            embed.set_author(name='sendAuditLogEntry', url='https://github.com/tetsuya-ki/discord-bot-heroku/')

            if hasattr(entry, 'changes'):
                embed.add_field(name='changes', value=entry.changes)
            if hasattr(entry.changes.after, 'overwrites'):
                embed.add_field(name='after.overwrites', value=entry.changes.after.overwrites)
            if hasattr(entry.changes.before, 'roles'):
                embed.add_field(name='before.roles', value=entry.changes.before.roles)
            if hasattr(entry.changes.after, 'roles'):
                embed.add_field(name='after.roles', value=entry.changes.after.roles)
                print(entry.changes.after.roles)
            if hasattr(entry.changes.before, 'channel'):
                embed.add_field(name='before.channel', value=entry.changes.before.channel)
            if hasattr(entry.changes.after, 'channel'):
                embed.add_field(name='after.channel', value=entry.changes.after.channel)

        if (settings.IS_DEBUG):
            print(msg)
            print(entry.changes)

        await to_channel.send(msg, embed=embed)

    # メッセージの削除
    @commands.command(aliases=['pg','del','delete'],description='メッセージを削除します')
    async def purge(self, ctx, limit_num=None):
        """
        自分かBOTのメッセージを削除します。
        削除するメッセージの数が必要です。
        """
        self.command_author = ctx.author
        # botかコマンドの実行主かチェック
        def is_me(m):
            return self.command_author == m.author or m.author.bot

        # 指定がない、または、不正な場合は、コマンドを削除。そうではない場合、コマンドを削除し、指定の数だけ削除する
        if limit_num is None:
            await ctx.channel.purge(limit=1, check=is_me)
            await ctx.channel.send('オプションとして、1以上の数値を指定してください。\nあなたのコマンド：`{0}`'.format(ctx.message.clean_content))
            return
        if limit_num.isdecimal():
            limit_num = int(limit_num) + 1
        else:
            await ctx.channel.purge(limit=1, check=is_me)
            await ctx.channel.send('有効な数字ではないようです。オプションは1以上の数値を指定してください。\nあなたのコマンド：`{0}`'.format(ctx.message.clean_content))
            return

        if limit_num > 1000:
            limit_num = 1000
        elif limit_num < 2:
            await ctx.channel.purge(limit=1, check=is_me)
            await ctx.channel.send('オプションは1以上の数値を指定してください。\nあなたのコマンド：`{0}`'.format(ctx.message.clean_content))
            return

        # 違和感を持たせないため、コマンドを削除した分を省いた削除数を通知する。
        deleted = await ctx.channel.purge(limit=limit_num, check=is_me)
        await ctx.channel.send('{0}個のメッセージを削除しました。\nあなたのコマンド：`{1}`'.format(len(deleted) - 1, ctx.message.clean_content))

    @getAuditLog.error
    async def getAuditLog_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            print(error)
            await ctx.send(error)

    # チャンネル作成時に実行されるイベントハンドラを定義
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        event_text = '作成'
        await self.on_guild_channel_xxx(channel, event_text)

    # チャンネル削除時に実行されるイベントハンドラを定義
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        event_text = '削除'
        await self.on_guild_channel_xxx(channel, event_text)

    # チャンネル作成/削除時のメッセージを作成
    async def on_guild_channel_xxx(self, channel: discord.abc.GuildChannel, event_text):
        guild = channel.guild
        str = 'id: {0}, name: {1}, type:{2}が{3}されました'.format(channel.id, channel.name, channel.type, event_text)

        if isinstance(channel, discord.TextChannel):
            str = 'id: {0}, name: #{1}, type:{2}が{3}されました'.format(channel.id, channel.name, channel.type, event_text)
            category = guild.get_channel(channel.category_id)
            if category is not None:
                str += '\nCategory: {0}, channel: <#{1}>'.format(category.name, channel.id)
            else:
                str += '\nchannel: <#{0}>'.format(channel.id)
        elif isinstance(channel, discord.VoiceChannel):
            category = guild.get_channel(channel.category_id)
            if category is not None:
                str += '\nCategory: {0}'.format(category.name)
        if (settings.IS_DEBUG):
            print(f'***{str}***')
        await self.sendGuildChannel(guild, str, channel.created_at)

    # メンバーGuild参加時に実行されるイベントハンドラを定義
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        event_text = '参加'
        await self.on_member_xxx(member, event_text)

    # メンバーGuild脱退時に実行されるイベントハンドラを定義
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        event_text = '脱退'
        await self.on_member_xxx(member, event_text)

    # メンバーの参加/脱退時のメッセージを作成
    async def on_member_xxx(self, member: discord.Member, event_text):
        guild = member.guild
        str = 'member: {0}が{1}しました'.format(member, event_text)

        if (settings.IS_DEBUG):
            print(f'***{str}***')

        await self.sendGuildChannel(guild, str, member.joined_at)

    # 監査ログをチャンネルに送信
    async def sendGuildChannel(self, guild, string, created_time):
        to_channel = guild.get_channel(settings.AUDIT_LOG_SEND_CHANNEL)
        created_at = created_time.replace(tzinfo=datetime.timezone.utc)
        created_at_jst = created_at.astimezone(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y/%m/%d(%a) %H:%M:%S')
        msg = '{1}: {0}'.format(string, created_at_jst)
        await to_channel.send(msg)

def setup(bot):
    bot.add_cog(AdminCog(bot)) # AdminCogにBotを渡してインスタンス化し、Botにコグとして登録する