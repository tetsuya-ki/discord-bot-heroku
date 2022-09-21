import random
import json
import os
import discord
from os.path import join, dirname
from logging import getLogger
from . import settings
from .savefile import SaveFile
from .members import Members

LOG = getLogger('assistantbot')

class OhrgiriStart(discord.ui.View):
    def __init__(self, oh_members, ohgiriGames, msg):
        super().__init__()
        self.oh_members = oh_members
        self.ohgiriGames = ohgiriGames
        self.msg = msg

    @discord.ui.button(label='参加する', style=discord.ButtonStyle.green)
    async def join(self, interaction, button: discord.ui.Button):
        if interaction.guild_id in self.oh_members:
            self.oh_members[interaction.guild_id].add_member(interaction.user)
        else:
            self.oh_members[interaction.guild_id] = Members()
            self.ohgiriGames[interaction.guild_id] = Ohgiri()
            self.ohgiriGames[interaction.guild_id].file_path = self.ohgiriGames['default'].file_path
            self.oh_members[interaction.guild_id].add_member(interaction.user)
        LOG.debug(f'追加:{interaction.user.display_name}')
        await interaction.response.edit_message(content=f'{interaction.user.display_name}が参加しました!(参加人数:{self.oh_members[interaction.guild_id].len})', view=self)

    @discord.ui.button(label='離脱する', style=discord.ButtonStyle.red)
    async def leave(self, interaction, button: discord.ui.Button):
        if interaction.guild_id in self.oh_members:
            self.oh_members[interaction.guild_id].remove_member(interaction.user)
        else:
            self.oh_members[interaction.guild_id] = Members()
            self.ohgiriGames[interaction.guild_id] = Ohgiri()
            self.ohgiriGames[interaction.guild_id].file_path = self.ohgiriGames['default'].file_path
        LOG.debug(f'削除:{interaction.user.display_name}')
        await interaction.response.edit_message(content=f'{interaction.user.display_name}が離脱しました!(参加人数:{self.oh_members[interaction.guild_id].len})', view=self)

    @discord.ui.button(label='開始する', style=discord.ButtonStyle.blurple)
    async def start(self, interaction, button: discord.ui.Button):
        if interaction.guild_id not in self.oh_members:
            msg = f'ゲームが始まっていません。`/start-ohgiri-game`でゲームを開始してください。'
            self.oh_members[interaction.guild_id] = Members()
            self.ohgiriGames[interaction.guild_id] = Ohgiri()
            self.ohgiriGames[interaction.guild_id].file_path = self.ohgiriGames['default'].file_path
            await interaction.response.edit_message(content=msg, view=self)
            return
        if self.oh_members[interaction.guild_id].len < 2:
            msg = f'大喜利を楽しむには2人以上のメンバーが必要です(現在、{self.oh_members[interaction.guild_id].len}人しかいません)'
            await interaction.response.edit_message(content=msg, view=self)
            return
        await self.startOhgiri(interaction)

    @discord.ui.button(label='参加者をクリアする', style=discord.ButtonStyle.grey)
    async def clear(self, interaction, button: discord.ui.Button):
        self.oh_members[interaction.guild_id] = Members()
        self.ohgiriGames[interaction.guild_id] = Ohgiri()
        LOG.debug(f'参加者クリア:{interaction.user.display_name}')
        await interaction.response.edit_message(content=f'参加者がクリアされました(参加人数:{self.oh_members[interaction.guild_id].len})', view=self)

    @discord.ui.button(label='終了する', style=discord.ButtonStyle.grey)
    async def close(self, interaction, button: discord.ui.Button):
        self.oh_members[interaction.guild_id] = Members()
        self.ohgiriGames[interaction.guild_id] = Ohgiri()
        LOG.debug(f'終了:{interaction.user.display_name}')
        self.stop()
        await interaction.response.edit_message(content=f'終了しました', view=self)

    async def startOhgiri(self, interaction: discord.Interaction):
        # 参加者と手札の数を設定
        await self.ohgiriGames[interaction.guild_id].setting(self.oh_members[interaction.guild_id].get_members(), 12, self.ohgiriGames[interaction.guild_id].win_point)
        self.ohgiriGames[interaction.guild_id].shuffle()
        msg = 'お題が提供されるので**「親」はお題を声に出して読み上げ**てください（"○○"は「まるまる」、"✕✕"は「ばつばつ」と読む）。ほかのプレイヤーは読み上げられた**お題に相応しいと思う回答**をボタンを押して、プルダウンから回答します。\n'\
            + '全員が回答したら、**「親」はもっとも秀逸な回答**をボタンを押して、選択します。「親」から選ばれたプレイヤーは1点もらえます。ただし、山札から1枚カードが混ざっており、それを選択すると親はポイントが減算されます。\n'\
            + f'今回のゲームの勝利点は{self.ohgiriGames[interaction.guild_id].win_point}点です。'
        await interaction.response.send_message(msg)
        await self.ohgiriGames[interaction.guild_id].dealAndNextGame(interaction)

class OhrgiriAnswerDropdown(discord.ui.Select):
    def __init__(self, ohgiri, guild_id: int, user: discord.User):
        self.ohgiri = ohgiri
        self.guild_id = guild_id
        self.user = user
        options = []
        emoji_list = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

        for i, card in enumerate(self.ohgiri.members[self.user].cards):
            emoji = ''
            if len(emoji_list) > i:
                emoji=emoji_list[i]
            else:
                emoji='🔢'
            data = discord.SelectOption(label=self.ohgiri.ans_dict[card], value=card, emoji=emoji)
            options.append(data)

        msg = f'あなたの回答を{self.ohgiri.required_ans_num}枚選択...'
        if self.ohgiri.required_ans_num == 2:
            msg += '(2枚の場合、選択順で格納/表示順ではありません)'
        super().__init__(placeholder=msg, min_values=1, max_values=self.ohgiri.required_ans_num, options=options)

    async def callback(self, interaction: discord.Interaction):
        view: OhrgiriAnswer = self.view

        # カードID, 2枚目のカードIDを設定
        card_id = self.values[0]
        second_card_id = None
        if len(self.values) == 2:
            second_card_id = self.values[1]

        # 始まっているかのチェック
        if len(self.ohgiri.members) == 0 or self.ohgiri.game_over:
            await interaction.response.send_message('ゲームが起動していません！', ephemeral=True)
        # コマンド実行者のチェック(親は拒否)
        elif interaction.user == self.ohgiri.house:
            await interaction.response.send_message('親は回答を提出できません！', ephemeral=True)
        # 引数が設定されているかチェック
        elif card_id is None:
            await interaction.response.send_message('引数`card_id`を指定してください！', ephemeral=True)
        # 参加者かチェック
        elif self.ohgiri.members.get(interaction.user) is None:
            await interaction.response.send_message(f'{interaction.user.display_name}は、参加者ではありません！', ephemeral=True)
        # コマンド実行者が所持しているかチェック
        elif card_id not in self.ohgiri.members[interaction.user].cards:
            await interaction.response.send_message(f'{card_id}は{interaction.user.display_name}の所持しているカードではありません！', ephemeral=True)
        elif self.ohgiri.required_ans_num == 1 and second_card_id is not None:
            await interaction.response.send_message('お題で2つ設定するように指定がないので、回答は1つにしてください！', ephemeral=True)
        elif self.ohgiri.required_ans_num == 2 and second_card_id is None:
            await interaction.response.send_message('2つめの引数`second_card_id`が設定されていません！(もう一つ数字を設定してください)', ephemeral=True)
        elif self.ohgiri.required_ans_num == 2 and second_card_id not in self.ohgiri.members[interaction.user].cards:
            await interaction.response.send_message(f'{second_card_id}は{interaction.user.display_name}の所持しているカードではありません！', ephemeral=True)
        else:
            LOG.debug('回答を受け取ったよ！')
            current_max_num = len(self.ohgiri.members) - 1
            current_field_num = len(self.ohgiri.field)
            turn_end_flg = (current_max_num)  <= current_field_num
            if not turn_end_flg:
                # 既に回答したメンバーから再度回答を受けた場合、入れ替えた旨お知らせする
                if self.ohgiri.members[interaction.user].answered:
                    await interaction.response.send_message(f'{interaction.user.mention} 既に回答を受け取っていたため、そちらのカードと入れ替えますね！', ephemeral=True)
                # カードの受領処理
                self.ohgiri.receive_card(card_id, interaction.user, second_card_id)
                # カードを受領したので場の数を更新
                current_field_num = len(self.ohgiri.field)
            # 回答者が出そろった場合、場に出す(親は提出できないので引く)
            if (current_max_num)  == current_field_num:
                self.ohgiri.show_answer()
                LOG.info('回答者が出揃ったので、場に展開！')
                house_player = self.ohgiri.house
                msg = self.ohgiri.description + f'\n{house_player.mention} 回答を読み上げたのち、お気に入りを選択ください！'
                # 全員回答完了したので、ドロップダウンを無効化
                view.stop()
                # 親選択用のDropdownを表示するボタンのView作成
                await interaction.response.send_message(content=msg, view=OhrgiriChoice(self.ohgiri), ephemeral=False)
            # 回答済、かつ、親選択中
            elif (current_max_num + 1)  == current_field_num:
                await interaction.response.send_message('親が選択中です。お待ちください。', ephemeral=True)
            else:
                await interaction.response.send_message('回答ありがとうございます', ephemeral=True)

class OhrgiriAnswerView(discord.ui.View):
    def __init__(self, ohgiri, guild_id: int, user: discord.User):
        super().__init__()
        self.ohgiri = ohgiri
        self.guild_id = guild_id
        self.user = user
        self.add_item(OhrgiriAnswerDropdown(self.ohgiri, self.guild_id, self.user))

class OhrgiriAnswer(discord.ui.View):
    def __init__(self, ohgiri):
        super().__init__()
        self.ohgiri = ohgiri

    @discord.ui.button(label='回答する', style=discord.ButtonStyle.green)
    async def answer(self, interaction, button: discord.ui.Button):
        current_max_num = len(self.ohgiri.members) - 1
        current_field_num = len(self.ohgiri.field)
        # 始まっているかのチェック
        if len(self.ohgiri.members) == 0 or self.ohgiri.game_over:
            await interaction.response.send_message('ゲームが起動していません！', ephemeral=True)
        # コマンド実行者のチェック(親は拒否)
        elif interaction.user == self.ohgiri.house:
            await interaction.response.send_message('親は回答を提出できません！', ephemeral=True)
        # 参加者かチェック
        elif self.ohgiri.members.get(interaction.user) is None:
            await interaction.response.send_message(f'{interaction.user.display_name}は、参加者ではありません！', ephemeral=True)
        # 全員回答完了しているため、ボタンを無効化
        elif (current_max_num + 1)  == current_field_num:
            view.stop()
        else:
            # 回答用のDropdownを表示するボタンのView作成
            view = OhrgiriAnswerView(self.ohgiri, interaction.guild_id , interaction.user)
            await interaction.response.send_message(content='回答ください', view=view, ephemeral=True)

    @discord.ui.button(label='状況を確認する', style=discord.ButtonStyle.gray)
    async def button_check_description(self, interaction, button: discord.ui.Button):
        """
        現在の状況を説明します
        """
        # 始まっているかのチェック
        if len(self.ohgiri.members) == 0 or self.ohgiri.game_over:
            await interaction.response.send_message('ゲームが起動していません！', ephemeral=True)
            return
        self.ohgiri.show_info()
        await interaction.response.send_message(self.ohgiri.description, ephemeral=True)

    @discord.ui.button(label='ポイント1点減点の上手札を全て捨てる', style=discord.ButtonStyle.red)
    async def button_discard_hand(self, interaction, button: discord.ui.Button):
        """
        ポイントを1点減点し、手札をすべて捨て、山札からカードを引く（いい回答カードがない時に使用ください）
        """
        # 始まっているかのチェック
        if len(self.ohgiri.members) == 0 or self.ohgiri.game_over:
            await interaction.response.send_message('ゲームが起動していません！', ephemeral=True)
            return
        self.ohgiri.discard_hand(interaction.user)
        await interaction.response.send_message(self.ohgiri.description, ephemeral=True)

class OhrgiriChoiceDropdown(discord.ui.Select):
    def __init__(self, ohgiri: dict, guild_id: int, user: discord.User):
        self.ohgiri = ohgiri
        self.guild_id = guild_id
        self.user = user
        options = []
        emoji_list = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

        for i, choice in enumerate(self.ohgiri.answer_list):
            emoji = ''
            if len(emoji_list) > i:
                emoji=emoji_list[i]
            else:
                emoji='🔢'
            data = discord.SelectOption(label=choice, value=str(i), emoji=emoji)
            options.append(data)

        super().__init__(placeholder=f'あなたが気に入った回答を選択してください...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        view: OhrgiriChoice = self.view

        # 回答番号を設定
        ans_index= self.values[0]
        # その他変数
        current_max_num = len(self.ohgiri.members) - 1
        current_field_num = len(self.ohgiri.field)
        # 始まっているかのチェック
        if len(self.ohgiri.members) == 0 or self.ohgiri.game_over:
            await interaction.response.send_message('ゲームが起動していません！', ephemeral=True)
        # コマンド実行者のチェック(親以外は拒否)
        elif interaction.user != self.ohgiri.house:
            await interaction.response.send_message('親以外が秀逸な回答を選択することはできません！', ephemeral=True)
        elif ans_index is None or not ans_index.isdecimal():
            await interaction.response.send_message('`ans_index`が選択されていません！', ephemeral=True)
        # 回答が出揃っているかチェック
        elif current_max_num  > current_field_num:
            view.stop()
            await interaction.response.send_message(f'次のターンが始まっています', ephemeral=True)
        else:
            # 場にある数かどうかのチェック
            if int(ans_index) > current_max_num:
                await interaction.response.send_message(f'{ans_index}は場に出ている最大の選択数({current_max_num})を超えています！', ephemeral=True)
                return

            # 結果を表示
            self.ohgiri.choose_answer(ans_index)
            await interaction.response.send_message(self.ohgiri.description)

            # ゲームが終了していない場合、次のターンを開始
            if not self.ohgiri.game_over:
                view.stop()
                await self.ohgiri.dealAndNextGame(interaction)

class OhrgiriChoiceView(discord.ui.View):
    def __init__(self, ohgiri, guild_id: int, user: discord.User):
        super().__init__()
        self.guild_id = guild_id
        self.ohgiri = ohgiri
        self.user = user
        self.add_item(OhrgiriChoiceDropdown(self.ohgiri, self.guild_id, self.user))

class OhrgiriChoice(discord.ui.View):
    def __init__(self, ohgiri):
        super().__init__()
        self.ohgiri = ohgiri

    @discord.ui.button(label='気に入った回答を選択する', style=discord.ButtonStyle.green)
    async def choice(self, interaction, button: discord.ui.Button):
        # 始まっているかのチェック
        if len(self.ohgiri.members) == 0 or self.ohgiri.game_over:
            await interaction.response.send_message('ゲームが起動していません！', ephemeral=True)
        # コマンド実行者のチェック(親以外は拒否)
        elif interaction.user != self.ohgiri.house:
            await interaction.response.send_message('親以外が秀逸な回答を選択することはできません！', ephemeral=True)
        # 参加者かチェック
        elif self.ohgiri.members.get(interaction.user) is None:
            await interaction.response.send_message(f'{interaction.user.display_name}は、参加者ではありません！', ephemeral=True)
        else:
            # 回答用のDropdownを表示するボタンのView作成
            view = OhrgiriChoiceView(self.ohgiri, interaction.guild_id , interaction.user)
            await interaction.response.send_message(content='選択ください', view=view, ephemeral=True)

class OhgiriMember:
    """
    大喜利参加者クラス
    """
    def __init__(self):
        self.point = 0
        self.cards = [] # カードのID
        self.answered = False

class Answer:
    def __init__(self, card_id, member, second_card_id=None):
        self.card_id = card_id # 回答カード配列の配列番号
        self.member = member # 回答者
        self.answer_index = None # 画面にある番号(画面に表示する前にまとめて採番して設定するのでinitではNone)
        self.second_card_id = second_card_id # 2つ目の回答カード配列の配列番号

class Ohgiri():
    """
    大喜利ゲームのクラス
    """
    FILE = 'ohgiri.json'
    DEFAULT_WIN_POINT = 5
    MAX_WIN_POINT = 20

    def __init__(self):
        self.members = {} # ゲームの参加者
        self.house = None # 今の親
        self.deck_odai = [] # デッキ（お題）
        self.deck_ans = [] # デッキ（回答）
        self.odai = None # 場におかれているお題
        self.required_ans_num = 1 # 必要な回答数
        self.field = [] # 場におかれている回答
        self.discards_odai = [] # 捨て札(お題)
        self.discards_ans = [] # 捨て札(回答)
        self.winCardsList = []
        self.turn = 0
        self.description = ''
        self.answer_list = [] # Choiceで使用するもの
        self.max_hands = None
        self.ans_dict = {}
        self.savefile = SaveFile()
        self.game_over = False
        self.win_point = 5 # 勝利扱いとするポイント
        self.file_path = self.file_path = join(dirname(__file__), 'files' + os.sep + self.FILE)

    async def on_ready(self):
        json_path = join(dirname(__file__), 'files' + os.sep + 'temp' + os.sep + self.FILE)
        # 環境変数に大喜利用JSONのURLが登録されており、可能ならファイルを使用がFalseの場合はそちらを使用
        if settings.OHGIRI_JSON_URL and not settings.USE_IF_AVAILABLE_FILE:
            self.file_path = await self.savefile.download_file(settings.OHGIRI_JSON_URL,  json_path)
            LOG.info(f'大喜利JSONのURLが登録されているため、JSONを保存しました。\n{self.file_path}')

    async def init_card(self):
        json_data = {}

        try:
            with open(self.file_path, mode='r') as f:
                json_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, EOFError) as e:
            # JSON変換失敗、読み込みに失敗したらなにもしない
            LOG.error(e)

        # お題配列を取り出してお題カードデッキを作る
        self.deck_odai = json_data['subject']

        # 回答配列を取り出して回答カード辞書を作る
        answer_index = 0
        for answer in json_data['answer']:
            self.ans_dict[str(answer_index)] = answer
            self.deck_ans.append(str(answer_index))
            answer_index += 1

    async def setting(self, members, max_hands, win_point):
        """
        メンバーに大喜利メンバーをセットし、ゲームできるようにセッティングする
        - members: 参加者
        - max_hands: 手札の数
        - win_point: 勝利ポイント
        """
        self.__init__()
        await self.init_card()
        self.max_hands = max_hands
        self.win_point = win_point

        for member in members:
            ohgiriMember = OhgiriMember()
            self.members[member] = ohgiriMember
        self.house = random.choice(members)

    def shuffle(self):
        """
        デッキをシャッフルする（お題、回答両方）
        """
        random.shuffle(self.deck_odai)
        random.shuffle(self.deck_ans)
        message = 'シャッフルしました。\n'
        self.description += message
        LOG.info(message)

    def deal(self):
        """
        カードを配る
        """
        self.turn = self.turn + 1
        self.description = ''
        self.field = []

        # 場に置かれるお題をひく
        self.odai =  self.deck_odai.pop()

        # お題にXXがあるかチェック
        if '✕✕' in self.odai:
            self.required_ans_num = 2
        else:
            self.required_ans_num = 1

        # お題の山札がなくなった場合の処理
        if len(self.deck_odai) == 0:
            self.retern_discards_to_deck('お題カード', self.discards_odai, self.deck_odai)

        for member in self.members:
            # 回答未済に設定する
            self.members[member].answered = False
            # 手札が「手札の最大数 - メンバーのpoint」になるまでカードを配る
            while len(self.members[member].cards) < (self.max_hands - self.members[member].point):
                self.members[member].cards.append(self.deck_ans.pop())
                # 回答が無くなった時の処理
                if len(self.deck_ans) == 0:
                    self.retern_discards_to_deck('回答カード', self.discards_ans, self.deck_ans)

            self.members[member].cards = sorted(self.members[member].cards, key=int)

    def retern_discards_to_deck(self, name, target_discards, target_deck):
        message = f'{name}がなくなったので山札と捨て札を混ぜて、'
        self.description += message
        LOG.info(message)
        target_deck.extend(target_discards)
        target_discards = []
        self.shuffle()

    def receive_card(self, card_id, member, second_card_id=None):
        """
        メンバーからカードを受け取ったときの処理
        受け取ったカードを場に出す
        メンバーの手持ちから受領したカードを除去
        cardNum {Int}
        member self.membersから取り出すキー
        second_card_id {Int}
        """
        # 回答済のメンバーからカードを受け取った場合は、場に出されたカードとそのカードを入れ替える
        if self.members[member].answered:
            for answer in self.field:
                if answer.member == member:
                    self.members[member].cards.append(answer.card_id)
                    if answer.second_card_id is not None:
                        self.members[member].cards.append(answer.second_card_id)
                    break
            self.field = [answer for answer in self.field if answer.member != member]

        # 回答済に設定する
        self.members[member].answered = True
        if second_card_id is None:
            self.field.append(Answer(card_id, member))
        else:
            self.field.append(Answer(card_id, member, second_card_id))

        # 受信したカード以外のカードをユーザに返す
        self.members[member].cards = [users_card_id for users_card_id in self.members[member].cards if (users_card_id != card_id and users_card_id != second_card_id)]

    def show_answer(self):
        """
        山札からカードを1枚加え、ランダムに混ぜた上で、回答を表示
        """
        # 山札からカードを引いてダミーの回答を作る
        if self.required_ans_num == 1:
            self.field.append(Answer(self.deck_ans.pop(), 'dummy'))
        else:
            self.field.append(Answer(self.deck_ans.pop(), 'dummy', self.deck_ans.pop()))

        # 場に出た回答に画面表示用のランダムな番号を設定する。
        random_field = random.sample(self.field, len(self.field))
        for i in range(len(random_field)):
            random_field[i].answer_index = str(i)

        self.description = ''
        self.answer_list = []
        for sorted_answer in sorted(random_field, key=lambda answer: answer.answer_index):
            # dropdownで番号がずれるため、表示だけ同様にずらす
            description_text = f'{(int(sorted_answer.answer_index) + 1)}: {str(self.odai).replace("〇〇", "||" + self.ans_dict[sorted_answer.card_id] + "||")}\n'
            answer_text = f'{str(self.odai).replace("〇〇", self.ans_dict[sorted_answer.card_id])}\n'
            if self.required_ans_num == 2:
                description_text = description_text.replace("✕✕", "||" + self.ans_dict[sorted_answer.second_card_id] + "||")
                answer_text = answer_text.replace("✕✕", self.ans_dict[sorted_answer.second_card_id])
            self.description += description_text
            self.answer_list.append(answer_text)

    def choose_answer(self, answer_index):
        """
        回答を選択
        """
        self.description = ''
        choosen_answer = [answer for answer in self.field if answer.answer_index == answer_index][0]

        if choosen_answer.member == 'dummy':
            choosen_member_display_name = 'dummy'
            # ダミーを選択したら親が減点
            house_member_obj = self.members[self.house]
            if house_member_obj.point > 0:
                house_member_obj.point += -1
                self.description += f'ダミーを選択したので、{discord.utils.escape_markdown(self.house.display_name)}のポイントが1点減りました。\n'
            else:
                self.description += f'ダミーを選択しました！（ポイント追加もなく、親もそのままです）\n'
        else :
            choosen_member_display_name = discord.utils.escape_markdown(choosen_answer.member.display_name)
            # 選ばれた人が得点を得て、親になる
            self.members[choosen_answer.member].point += 1
            self.description += f'親から選ばれた、{choosen_member_display_name}のポイントが1点増えました。\n'
            self.house = choosen_answer.member

        # 回答と回答者を入れたメッセージをwinCardsListに入れ、説明文に追加
        win_word = f'{str(self.odai).replace("〇〇", "**" + self.ans_dict[choosen_answer.card_id] + "**")} ({choosen_member_display_name}さん)\n'
        if self.required_ans_num == 2:
            win_word = win_word.replace("✕✕", "**" + self.ans_dict[choosen_answer.second_card_id] + "**")
        self.winCardsList.append(win_word)
        self.description += '> ' + win_word

        # 使用済みのカードを捨てる(お題と回答どちらも)
        self.discards_odai.append(self.odai)
        self.odai = ''
        for answer in self.field:
            self.discards_ans.append(str(answer.card_id))
            if answer.second_card_id is not None:
                self.discards_ans.append(str(answer.second_card_id))

        # 勝利判定
        if choosen_answer.member != 'dummy' and self.members[choosen_answer.member].point >= self.win_point:
            self.game_over = True
            self.description += f'\n{choosen_member_display_name}さん、あなたが優勝です！　\n■今回選出されたカードの一覧はコチラ！\n'
            for i, win_word in enumerate(self.winCardsList):
                self.description += f'{i+1}: {win_word}'

    def show_info(self):
        house = '' if self.game_over else f'、現在の親: {discord.utils.escape_markdown(self.house.display_name)}さん'
        self.description = f'ターン: {self.turn}{house}({self.win_point}点取得した人が勝利です)\n現在のお題: {self.odai}\n'

        # 参加者の点数と回答済みかどうかを表示する
        for member in self.members:
            self.description += f'{discord.utils.escape_markdown(member.display_name)}さん'
            self.description += f'({self.members[member].point}点): '

            if self.members[member].answered:
                self.description += '回答済\n'
            elif member == self.house or self.game_over:
                self.description += '親(回答不要)\n'
            else:
                self.description += '未回答\n'

    def discard_hand(self, member):
        self.description = ''
        # ポイントを減らす(1点以上なら)
        if self.members[member].point > 0:
            self.members[member].point += -1
            self.description += 'ポイントを1点減点し、'

        self.description += '手札をすべて捨てて、山札から引きました！'
        # 手札を全て捨てる
        self.discards_ans.extend(self.members[member].cards)
        self.members[member].cards = []
        # 山札から回答カードを引く(手札が「手札の最大数 - メンバーのpoint」になるまでカードを配る)
        while len(self.members[member].cards) < (self.max_hands - self.members[member].point):
            self.members[member].cards.append(self.deck_ans.pop())
            # 回答が無くなった時の処理
            if len(self.deck_ans) == 0:
                self.retern_discards_to_deck('回答カード', self.discards_ans, self.deck_ans)

        self.members[member].cards = sorted(self.members[member].cards, key=int)

    async def dealAndNextGame(self, interaction: discord.Interaction):
        self.deal()

        # お題を表示
        await interaction.followup.send(f'お題：{self.odai}\n＊親は{self.house.display_name}(親以外が回答してください)', view=OhrgiriAnswer(self))