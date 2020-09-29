import pickle
import discord
from discord.utils import get
import os
from os.path import join, dirname
import base64
import json

class ReactionChannel:
    FILE = 'reaction-channel.json'

    def __init__(self):
        self.reaction_channels = []
        self.guild_reaction_channels = []
        self.guild_rc_txt_lists = []
        self.rc_len = 0
        self.rc_err = ''

    # 初期設定
    def set_rc(self, guild:discord.Guild):
        # 既に読み込まれている場合は、読み込みしない
        if self.rc_len != 0:
            print('__読み込み不要__')
            return

        # 読み込み
        try:
            print('＊＊読み込み＊＊')
            file_path = join(dirname(__file__), 'files' + os.sep + self.FILE)
            dict = {}
            with open(file_path, mode='r') as f:
                dict = json.load(f)
                serialize = dict["pickle"]
                self.reaction_channels = pickle.loads(base64.b64decode(serialize.encode()))
            self.guild_reaction_channels = [rc[1:] for rc in self.reaction_channels if str(guild.id) in map(str, rc)]
            # joinするので文字列に変換し、リストに追加する
            for rc in self.guild_reaction_channels:
                self.guild_rc_txt_lists.append('+'.join(map(str, rc)))
            self.rc_len = len(self.guild_reaction_channels)
        except FileNotFoundError:
            # 読み込みに失敗したらなにもしない
            print
        except json.JSONDecodeError:
            # JSON変換失敗したらなにもしない
            print
        except EOFError:
            # 読み込みに失敗したらなにもしない
            print

    # リアクションチャンネルを保管する
    def save(self):
        print('＊＊書き込み＊＊')
        file_path = join(dirname(__file__), 'files' + os.sep + self.FILE)
        serialized = base64.b64encode(pickle.dumps(self.reaction_channels)).decode("utf-8")
        dict = {"pickle": serialized}
        # 書き込み
        try:
            with open(file_path, mode='w') as f:
                json.dump(dict, f)
        except pickle.PickleError:
            # 書き込みに失敗したらなにもしない
            self.rc_err = '保管に失敗しました。'

    # 追加するリアクションチャネルが問題ないかチェック
    def check(self, ctx, reaction:str, channel:str):
        reaction_id = None
        if reaction.count(':') == 2:
            reaction_id = reaction.split(':')[1]
        guild = ctx.guild
        additem = f'{reaction}+{channel}'
        print(f'＊＊追加のチェック＊＊, reaction: {reaction}, channel: {channel}')
        # 絵文字が不正な場合(guildに登録された絵文字なら'yes'のような文字が入っているし、そうでない場合は1文字のはず -> 🐈‍⬛,がありえるので緩和)
        emoji = discord.utils.get(guild.emojis, name=reaction_id)
        if emoji is None and len(reaction) > 4:
            self.rc_err = f'絵文字が不正なので登録できません。(reaction: {reaction})'
            return False

        # チャンネルが不正な場合
        get_channel = discord.utils.get(guild.text_channels, name=channel)
        if get_channel is None:
            self.rc_err = 'チャンネルが不正なので登録できません。'
            return False

        # リアクションチャンネルが未登録ならチェックOK
        if self.rc_len == 0:
            return True

        # すでに登録されている場合
        dup_checked_list = list(filter(lambda x: additem in x, self.guild_rc_txt_lists))
        if len(dup_checked_list) > 0:
            self.rc_err = 'すでに登録されています。'
            return False

        return True

    # リアクションチャンネルを追加
    def add(self, ctx, reaction:str, channel:str):
        print(f'＊＊追加＊＊, reaction: {reaction}, channel: {channel}')
        guild = ctx.guild
        self.set_rc(guild)

        # チャンネルがID指定の場合はギルドからチャンネル名を取得
        if channel.count('#') == 1:
            channel_id = channel.split('#')[1].split('>')[0]
            print(f'check channel:{channel_id}')
            channel_info = None
            if channel_id.isdecimal():
                channel_info = guild.get_channel(int(channel_id))
            if channel_info is not None:
                channel = channel_info.name

        if self.check(ctx, reaction, channel) is False:
            return self.rc_err
        get_channel = discord.utils.get(guild.text_channels, name=channel)

        addItem = []
        addItem.append(guild.id)
        addItem.append(reaction)
        addItem.append(get_channel.name)
        addItem.append(get_channel.id)

        # 追加
        self.reaction_channels.append(addItem)
        self.guild_reaction_channels.append(addItem[1:])
        self.guild_rc_txt_lists.append('+'.join(map(str, addItem[1:])))
        self.rc_len = len(self.guild_reaction_channels)

        # 保管
        if self.save() is False:
            return self.rc_err

        serialized = base64.b64encode(pickle.dumps(self.reaction_channels)).decode("utf-8")
        return f'リアクションチャンネルの登録に成功しました！\n{reaction} → <#{get_channel.id}>\n----\n{serialized}'

    def list(self, ctx):
        guild = ctx.guild
        self.set_rc(guild)
        print(f'＊＊リスト＊＊, {self.guild_reaction_channels}')
        text = ''
        for list in self.guild_reaction_channels:
            text = f'{text}  リアクション：{list[0]} → <#{list[2]}>\n'

        if text == '':
            return f'＊現在登録されているリアクションチャンネルはありません！'
        else:
            return f'＊現在登録されているリアクションチャンネルの一覧です！({self.rc_len}種類)\n{text}'

    # 全削除
    def purge(self, ctx):
        print('＊＊リアクションチャネラーを全部削除＊＊')
        guild = ctx.guild
        self.set_rc(guild)
        self.reaction_channels = [rc for rc in self.reaction_channels if guild.id not in rc ]
        self.guild_reaction_channels = []
        self.guild_rc_txt_lists = []
        self.rc_len = 0
        # 保管
        if self.save() is False:
            return self.rc_err

        serialized = base64.b64encode(pickle.dumps(self.reaction_channels)).decode("utf-8")
        return f'全てのリアクションチャンネラーの削除に成功しました！\n----\n{serialized}'

    # 削除
    def delete(self, ctx, reaction:str, channel:str):
        print(f'＊＊削除＊＊, reaction: {reaction}, channel: {channel}')
        guild = ctx.guild
        self.set_rc(guild)

        # チャンネルがID指定の場合はギルドからチャンネル名を取得
        if channel.count('#') == 1:
            channel_id = channel.split('#')[1].split('>')[0]
            print(f'check channel:{channel_id}')
            channel_info = None
            if channel_id.isdecimal():
                channel_info = guild.get_channel(int(channel_id))
            if channel_info is not None:
                channel = channel_info.name

        get_channel = discord.utils.get(guild.text_channels, name=channel)
        deleteItem = []
        deleteItem.append(guild.id)
        deleteItem.append(reaction)
        deleteItem.append(get_channel.name)
        deleteItem.append(get_channel.id)

        # 削除
        self.reaction_channels = [s for s in self.reaction_channels if s != deleteItem]
        self.guild_reaction_channels = [s for s in self.guild_reaction_channels if s != deleteItem[1:]]
        self.guild_rc_txt_lists = [s for s in self.guild_rc_txt_lists if s != '+'.join(map(str, deleteItem[1:]))]
        self.rc_len = len(self.guild_reaction_channels)

        # 保管
        if self.save() is False:
            return self.rc_err

        serialized = base64.b64encode(pickle.dumps(self.reaction_channels)).decode("utf-8")
        return f'リアクションチャンネラーの削除に成功しました！\n{reaction} → <#{get_channel.id}>\n----\n{serialized}'
