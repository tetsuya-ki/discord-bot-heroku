from datetime import date
import discord
from discord import channel
from discord.ext import commands # Bot Commands Frameworkのインポート
import datetime
from .modules import settings
from .modules.auditlogchannel import AuditLogChannel
import asyncio

# コグとして用いるクラスを定義。
class AdminCog(commands.Cog, name='管理用'):
    """
    管理用の機能です。
    """
    # AdminCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    def __init__(self, bot):
        self.bot = bot
        self.command_author = None
        self.audit_log_channel = AuditLogChannel()

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

        if await self.audit_log_channel.get_ch(ctx.guild) is False:
            print(self.audit_log_channel.alc_err)
            return
        else:
            to_channel = self.audit_log_channel.channel

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
        なお、BOTにメッセージの管理権限、メッセージの履歴閲覧権限、メッセージの閲覧権限がない場合は失敗します。
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

    # チャンネル管理コマンド群
    @commands.group(aliases=['ch'], description='チャンネルを操作するコマンド（サブコマンド必須）')
    async def channel(self, ctx):
        """
        チャンネルを管理するコマンド群です。このコマンドだけでは管理できません。半角スペースの後、続けて以下のサブコマンドを入力ください。
        - チャンネルを作成したい場合は、`make`を入力し、チャンネル名を指定してください。
        - プライベートなチャンネルを作成したい場合は`privateMake`を入力し、チャンネル名を指定してください。
        - チャンネルを閲覧できるロールを削除したい場合、`roleDelete`を入力し、ロール名を指定してください。
        - トピックを変更したい場合は、`topic`を入力し、トピックに設定したい文字列を指定してください。
        """
        # サブコマンドが指定されていない場合、メッセージを送信する。
        if ctx.invoked_subcommand is None:
            await ctx.send('このコマンドにはサブコマンドが必要です。')

    # channelコマンドのサブコマンドmake
    # チャンネルを作成する
    @channel.command(aliases=['c','m','mk','craft'], description='チャンネルを作成します')
    async def make(self, ctx, channelName=None):
        """
        引数に渡したチャンネル名でテキストチャンネルを作成します（コマンドを打ったチャンネルの所属するカテゴリに作成されます）。
        10秒以内に👌(ok_hand)のリアクションをつけないと実行されませんので、素早く対応ください。
        """
        self.command_author = ctx.author
        # チャンネル名がない場合は実施不可
        if channelName is None:
            await ctx.channel.purge(limit=1)
            await ctx.channel.send('チャンネル名を指定してください。\nあなたのコマンド：`{0}`'.format(ctx.message.clean_content))
            return

        # メッセージの所属するカテゴリを取得
        guild = ctx.channel.guild
        category_id = ctx.message.channel.category_id
        category = guild.get_channel(category_id)

        # カテゴリーが存在するなら、カテゴリーについて確認メッセージに記載する
        category_text = ''
        if category is not None:
            category_text = f'カテゴリー「**{category.name}**」に、\n';

        # 念の為、確認する
        confirm_text = f'{category_text}パブリックなチャンネル **{channelName}** を作成してよろしいですか？ 問題ない場合、10秒以内に👌(ok_hand)のリアクションをつけてください。\nあなたのコマンド：`{ctx.message.clean_content}`'
        await ctx.channel.purge(limit=1)
        await ctx.channel.send(confirm_text)

        def check(reaction, user):
            return user == self.command_author and str(reaction.emoji) == '👌'

        # リアクション待ち
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
        except asyncio.TimeoutError:
            await ctx.channel.send('→リアクションがなかったのでキャンセルしました！')
        else:
            try:
                # カテゴリが存在しない場合と存在する場合で処理を分ける
                if category is None:
                    new_channel = await guild.create_text_channel(name=channelName)
                else:
                    # メッセージの所属するカテゴリにテキストチャンネルを作成する
                    new_channel = await category.create_text_channel(name=channelName)
            except discord.errors.Forbidden:
                await ctx.channel.send('→権限がないため、実行できませんでした！')
            else:
                await ctx.channel.send(f'<#{new_channel.id}>を作成しました！')

    # channelコマンドのサブコマンドprivateMake
    # チャンネルを作成する
    @channel.command(aliases=['p','pm','pmk', 'pcraft', 'primk'], description='プライベートチャンネルを作成します')
    async def privateMake(self, ctx, channelName=None):
        """
        引数に渡したチャンネル名でプライベートなテキストチャンネルを作成します（コマンドを打ったチャンネルの所属するカテゴリに作成されます）。
        10秒以内に👌(ok_hand)のリアクションをつけないと実行されませんので、素早く対応ください。
        """
        self.command_author = ctx.author

        # チャンネル名がない場合は実施不可
        if channelName is None:
            await ctx.channel.purge(limit=1)
            await ctx.channel.send('チャンネル名を指定してください。\nあなたのコマンド：`{0}`'.format(ctx.message.clean_content))
            return

        # トップロールが@everyoneの場合は実施不可
        if ctx.author.top_role.position == 0:
            await ctx.channel.purge(limit=1)
            await ctx.channel.send('everyone権限しか保持していない場合、このコマンドは使用できません。\nあなたのコマンド：`{0}`'.format(ctx.message.clean_content))
            return

        # メッセージの所属するカテゴリを取得
        guild = ctx.channel.guild
        category_id = ctx.message.channel.category_id
        category = guild.get_channel(category_id)

        # カテゴリーが存在するなら、カテゴリーについて確認メッセージに記載する
        category_text = ''
        if category is not None:
            category_text = f'カテゴリー「**{category.name}**」に、\n';

        # Guildのロールを取得し、@everyone以外のロールで最も下位なロール以上は書き込めるような辞書型overwritesを作成
        permissions = []
        for guild_role in ctx.guild.roles:
            # authorのeveryoneの1つ上のロールよりも下位のポジションの場合
            if guild_role.position < ctx.author.roles[1].position:
                permissions.append(discord.PermissionOverwrite(read_messages=False))
            else:
                permissions.append(discord.PermissionOverwrite(read_messages=True))
        overwrites = dict(zip(ctx.guild.roles, permissions))

        if settings.IS_DEBUG:
            print('-----author\'s role-----------------------------------------------------------')
            for author_role in ctx.author.roles:
                print(f'id:{author_role.id}, name:{author_role.name}, position:{author_role.position}')
            print('-----------------------------------------------------------------')
            print('-----Guild\'s role-----------------------------------------------------------')
            for guild_role in ctx.guild.roles:
                print(f'id:{guild_role.id}, name:{guild_role.name}, position:{guild_role.position}')
            print('-----------------------------------------------------------------')

        # 念の為、確認する
        confirm_text = f'{category_text}プライベートなチャンネル **{channelName}** を作成してよろしいですか()？ 問題ない場合、10秒以内に👌(ok_hand)のリアクションをつけてください。\nあなたのコマンド：`{ctx.message.clean_content}`'
        await ctx.channel.purge(limit=1)
        await ctx.channel.send(confirm_text)

        def check(reaction, user):
            return user == self.command_author and str(reaction.emoji) == '👌'

        # リアクション待ち
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
        except asyncio.TimeoutError:
            await ctx.channel.purge(limit=1)
            await ctx.channel.send('＊リアクションがなかったのでキャンセルしました！(プライベートなチャンネルを立てようとしていました。)')
        else:
            try:
                # カテゴリが存在しない場合と存在する場合で処理を分ける
                if category is None:
                    new_channel = await guild.create_text_channel(name=channelName, overwrites=overwrites)
                else:
                    # メッセージの所属するカテゴリにテキストチャンネルを作成する
                    new_channel = await category.create_text_channel(name=channelName, overwrites=overwrites)
            except discord.errors.Forbidden:
                await ctx.channel.purge(limit=1)
                await ctx.channel.send('＊権限がないため、実行できませんでした！(プライベートなチャンネルを立てようとしていました。)')
            else:
                await ctx.channel.purge(limit=1)
                await ctx.channel.send(f'`/channel privateMake`コマンドでプライベートなチャンネルを作成しました！')

    # channelコマンドのサブコマンドtopic
    # チャンネルのトピックを設定する
    @channel.command(aliases=['t', 'tp'], description='チャンネルにトピックを設定します')
    async def topic(self, ctx, *, topicWord=None):
        """
        引数に渡した文字列でテキストチャンネルのトピックを設定します。
        10秒以内に👌(ok_hand)のリアクションをつけないと実行されませんので、素早く対応ください。
        """
        self.command_author = ctx.author
        # トピックがない場合は実施不可
        if topicWord is None:
            await ctx.channel.purge(limit=1)
            await ctx.channel.send('トピックを指定してください。\nあなたのコマンド：`{0}`'.format(ctx.message.clean_content))
            return

        # 念の為、確認する
        original_topic = ''
        if ctx.channel.topic is not None:
            original_topic = f'このチャンネルには、トピックとして既に**「{ctx.channel.topic}」**が設定されています。\nそれでも、'
        confirm_text = f'{original_topic}このチャンネルのトピックに**「{topicWord}」** を設定しますか？ 問題ない場合、10秒以内に👌(ok_hand)のリアクションをつけてください。\nあなたのコマンド：`{ctx.message.clean_content}`'
        await ctx.channel.purge(limit=1)
        await ctx.channel.send(confirm_text)

        def check(reaction, user):
            return user == self.command_author and str(reaction.emoji) == '👌'

        # リアクション待ち
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
        except asyncio.TimeoutError:
            await ctx.channel.send('→リアクションがなかったのでキャンセルしました！')
        else:
            # チャンネルにトピックを設定する
            try:
                await ctx.channel.edit(topic=topicWord)
            except discord.errors.Forbidden:
                await ctx.channel.send('→権限がないため、実行できませんでした！')
            else:
                await ctx.channel.send(f'チャンネル「{ctx.channel.name}」のトピックに**「{topicWord}」**を設定しました！')

    # channelコマンドのサブコマンドroleDel
    # チャンネルのロールを削除する（テキストチャンネルが見えないようにする）
    @channel.command(aliases=['rd', 'roledel', 'deleterole' 'delrole', 'dr'], description='チャンネルのロールを削除します')
    async def roleDelete(self, ctx, targetRole=None):
        """
        指定したロールがテキストチャンネルを見れないように設定します（自分とおなじ権限まで指定可能（ただしチャンネルに閲覧できるロールがない場合、表示されなくなります！））。
        10秒以内に👌(ok_hand)のリアクションをつけないと実行されませんので、素早く対応ください。
        """
        self.command_author = ctx.author
        # 対象のロールがない場合は実施不可
        if targetRole is None:
            await ctx.channel.purge(limit=1)
            await ctx.channel.send('チャンネルから削除するロールを指定してください。\nあなたのコマンド：`{0}`'.format(ctx.message.clean_content))
            return
        # トップロールが@everyoneの場合は実施不可
        if ctx.author.top_role.position == 0:
            await ctx.channel.purge(limit=1)
            await ctx.channel.send('everyone権限しか保持していない場合、このコマンドは使用できません。\nあなたのコマンド：`{0}`'.format(ctx.message.clean_content))
            return

        underRoles = [guild_role.name for guild_role in ctx.guild.roles if guild_role.position <= ctx.author.top_role.position]
        underRolesWithComma = ",".join(underRoles).replace('@', '')

        role = discord.utils.get(ctx.guild.roles, name=targetRole)
        # 指定したロール名がeveryoneの場合、@everyoneとして処理する
        if targetRole == 'everyone':
            role = ctx.guild.default_role

        # 削除対象としたロールが、実行者のトップロールより大きい場合は実施不可(ロールが存在しない場合も実施不可)
        if role is None:
            await ctx.channel.purge(limit=1)
            await ctx.channel.send('存在しないロールのため、実行できませんでした(大文字小文字を正確に入力ください)。\n＊削除するロールとして{0}が指定できます。\nあなたのコマンド：`{1}`'.format(underRolesWithComma,ctx.message.clean_content))
            return
        elif role > ctx.author.top_role:
            await ctx.channel.purge(limit=1)
            await ctx.channel.send('削除対象のロールの方が権限が高いため、実行できませんでした。\n＊削除するロールとして{0}が指定できます。\nあなたのコマンド：`{1}`'.format(underRolesWithComma,ctx.message.clean_content))
            return

        # 読み書き権限を削除したoverwritesを作る
        overwrite =    discord.PermissionOverwrite(read_messages=False)

        # botのロール確認
        botRoleUpdateFlag = False
        botUser = self.bot.user
        botMember = discord.utils.find(lambda m: m.name == botUser.name, ctx.channel.guild.members)

        bot_role,bot_overwrite = None, None
        attention_text = ''
        if botMember.top_role.position == 0:
            if targetRole == 'everyone':
                attention_text = f'＊＊これを実行するとBOTが書き込めなくなるため、**権限削除に成功した場合でもチャンネルに結果が表示されません**。\n'
        else:
            bot_role = botMember.top_role
            bot_overwrites_pair = ctx.channel.overwrites_for(bot_role).pair()
            print(bot_overwrites_pair)
            # 権限が初期設定なら
            if (bot_overwrites_pair[0].value == 0) and (bot_overwrites_pair[1].value == 0):
                bot_overwrite = discord.PermissionOverwrite(read_messages=True,read_message_history=True)
                botRoleUpdateFlag = True
            if targetRole == bot_role.name:
                attention_text = f'＊＊これを実行するとBOTが書き込めなくなるため、**権限削除に成功した場合でもチャンネルに結果が表示されません**。\n'

        # 念の為、確認する
        confirm_text = f'{attention_text}このチャンネルから、ロール**「{targetRole}」** を削除しますか？\n（{targetRole}はチャンネルを見ることができなくなります。）\n 問題ない場合、10秒以内に👌(ok_hand)のリアクションをつけてください。\nあなたのコマンド：`{ctx.message.clean_content}`'
        await ctx.channel.purge(limit=1)
        await ctx.channel.send(confirm_text)

        def check(reaction, user):
            return user == self.command_author and str(reaction.emoji) == '👌'

        # リアクション待ち
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
        except asyncio.TimeoutError:
            await ctx.channel.send('→リアクションがなかったのでキャンセルしました！')
        else:
            # チャンネルに権限を上書きする
            try:
                if botRoleUpdateFlag:
                    await ctx.channel.set_permissions(bot_role, overwrite=bot_overwrite)
                await ctx.channel.set_permissions(role, overwrite=overwrite)
            except discord.errors.Forbidden:
                await ctx.channel.send('→権限がないため、実行できませんでした！')
            else:
                await ctx.channel.send(f'チャンネル「{ctx.channel.name}」からロール**「{targetRole}」**の閲覧権限を削除しました！')

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
        await self.on_member_xxx(member, event_text, member.joined_at)

    # メンバーGuild脱退時に実行されるイベントハンドラを定義
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        event_text = '脱退'
        now = datetime.datetime.now()
        now_tz = now.astimezone(datetime.timezone(datetime.timedelta(hours=0)))
        await self.on_member_xxx(member, event_text, now_tz)

    # メンバーの参加/脱退時のメッセージを作成
    async def on_member_xxx(self, member: discord.Member, event_text: str, dt: datetime):
        guild = member.guild
        str = 'member: {0}が{1}しました'.format(member, event_text)

        if (settings.IS_DEBUG):
            print(f'***{str}***')

        await self.sendGuildChannel(guild, str, dt)

    # 監査ログをチャンネルに送信
    async def sendGuildChannel(self, guild: discord.Guild, str: str, dt: datetime):
        if await self.audit_log_channel.get_ch(guild) is False:
            print(self.audit_log_channel.alc_err)
            return
        else:
            to_channel = self.audit_log_channel.channel
        dt_tz = dt.replace(tzinfo=datetime.timezone.utc)
        dt_jst = dt_tz.astimezone(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y/%m/%d(%a) %H:%M:%S')
        msg = '{1}: {0}'.format(str, dt_jst)
        await to_channel.send(msg)

def setup(bot):
    bot.add_cog(AdminCog(bot)) # AdminCogにBotを渡してインスタンス化し、Botにコグとして登録する