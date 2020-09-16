import random
import discord

# 改造元：https://github.com/Rabbit-from-hat/make-team/
class MakeTeam:

    def __init__(self):
        self.v_channels = [] # Guildにあるボイスチャンネル
        self.vc_members = [] # ボイスチャンネルに接続しているメンバー
        self.mem_len = 0
        self.vc_len = 0
        self.vc_state_err = ''
        self.vc_list = ''

    def set_mem(self, ctx):
        guild = ctx.guild
        self.v_channels = guild.voice_channels
        self.vc_len = len(self.v_channels)

        if len(self.v_channels) < 1:
            self.vc_state_err = 'ボイスチャンネルがないため実行できません。ボイスチャンネル作成後、再度実行してください。'
            return False

        # Guildにあるボイスチャンネルごと、メンバリストを追加していく
        for v_channel in self.v_channels:
            # ボイスチャンネルに権限の上書きがある場合、@everyoneがallowされていないなら、存在しないものとみなす
            # 例）@everyoneは閲覧できず、@Managerは接続できる場合は下記のような感じ
            # {<Role id=465376233115353098 name='@everyone'>: <discord.permissions.PermissionOverwrite object at 0x10a41d0d8>, <Role id=584261699742203925 name='Manager'>: <discord.permissions.PermissionOverwrite object at 0x10a41d528>}
            # @everyoneは(<Permissions value=0>, <Permissions value=1048576>)
            # @Managerは(<Permissions value=1048576>, <Permissions value=0>)
            # https://discordpy.readthedocs.io/ja/latest/api.html#discord.PermissionOverwrite.pair
            # > Returns the (allow, deny) pair from this overwrite.
            if(v_channel.overwrites):
                if(v_channel.overwrites[guild.default_role].pair()[0].value == 0):
                    continue
            self.vc_list += '🔈' + v_channel.name + '\n'
            for vc_member in v_channel.members:
                self.vc_members.append(vc_member) # VCメンバリスト取得
                self.vc_list += '> ' + vc_member.name + '\n'

        if len(self.vc_members) < 1:
            self.vc_state_err = 'ボイスチャンネルに接続しているメンバーがいません。ボイスチャンネル接続後、再度実行してください。'
            return False

        self.mem_len = len(self.vc_members) # 人数取得

        return True

    # メンバー取得
    async def get_members(self, ctx):
        self.set_mem(ctx)
        return self.vc_list

    # チーム数を指定した場合のチーム分け
    async def make_party_num(self, ctx, party_num, remainder_flag='false'):
        team = []
        team_string = []
        team_members = []
        remainder = []

        if self.set_mem(ctx) is False:
            return self.vc_state_err

        # 指定数の確認
        if party_num > self.vc_len:
            return f'Guildにあるボイスチャンネルの数を超えているため実行できません。{self.vc_len}以下の数を指定ください。'
        if party_num > self.mem_len:
            return f'指定された`party_num:{party_num}`がボイスチャンネルに接続しているメンバ数({self.mem_len})より大きいため、実行できません。(チーム数を指定しない場合は、デフォルトで2が指定されます）`'
        if party_num <= 0:
            return '実行できません。チーム分けできる数を指定してください。(チーム数を指定しない場合は、デフォルトで2が指定されます)'

        # メンバーリストをシャッフル
        random.shuffle(self.vc_members)

        # チーム分けで余るメンバーを取得
        if remainder_flag:
            remainder_num = self.mem_len % party_num
            if remainder_num != 0:
                for r in range(remainder_num):
                    remainder.append(self.vc_members.pop().name)
                team_string.append('=====余り=====')
                team_string.extend(remainder)

        # チーム分け
        for i in range(party_num):
            # 表示
            team_string.append('=====チーム'+str(i+1)+'=====')
            team_members = self.vc_members[i:self.mem_len:party_num]
            team_string.extend([j.name for j in team_members])
            # 振り分け
            for member in team_members:
                await member.move_to(self.v_channels[i])

        return ('\n'.join(team_string))

    # チームのメンバー数を指定した場合のチーム分け
    async def make_specified_len(self, ctx, specified_len):
        team = []
        team_string = []
        team_members = []
        remainder = []

        if self.set_mem(ctx) is False:
            return self.vc_state_err

        # 指定数の確認
        if specified_len > self.mem_len or specified_len <= 0:
            return '実行できません。チーム分けできる数を指定してください。'

        # チーム数を取得
        party_num = self.mem_len // specified_len

        # メンバーリストをシャッフル
        random.shuffle(self.vc_members)

        # チーム分けで余るメンバーを取得
        remainder_num = self.mem_len % party_num
        if remainder_num != 0:
            for r in range(remainder_num):
                remainder.append(self.vc_members.pop().name)
            team_string.append('=====余り=====')
            team_string.extend(remainder)

        # チーム分け
        for i in range(party_num):
            team_string.append('=====チーム'+str(i+1)+'=====')
            team_members = self.vc_members[i:self.mem_len:party_num]
            team_string.extend([j.name for j in team_members])

            # 振り分け
            for member in team_members:
                await member.move_to(self.v_channels[i])

        return ('\n'.join(team_string))