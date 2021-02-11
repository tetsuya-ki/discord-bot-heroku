import random
import json
import os
import discord
from os.path import join, dirname, exists
from logging import getLogger
from . import settings
from .savefile import SaveFile

logger = getLogger(__name__)

class OhgiriMember:
    """
    大喜利参加者クラス
    """
    def __init__(self):
        self.point = 0 
        self.cards = [] # カードのID
        self.answered = False

class Answer:
    def __init__(self, card_id, member):
        self.card_id = card_id # 回答カード配列の配列番号
        self.member = member # 回答者
        self.answer_index = None # 画面にある番号(画面に表示する前にまとめて採番して設定するのでinitではNone)

class Ohgiri:
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
        self.field = [] # 場におかれている回答
        self.discards_odai = [] # 捨て札(お題)
        self.discards_ans = [] # 捨て札(回答)
        self.winCardsList = []
        self.turn = 0
        self.description = ''
        self.max_hands = None
        self.ans_dict = {}
        self.savefile = SaveFile()
        self.game_over = False
        self.win_point = 5 # 勝利扱いとするポイント

    async def on_ready(self):
        json_path = join(dirname(__file__), 'files' + os.sep + 'temp' + os.sep + self.FILE)
        # 環境変数に大喜利用JSONのURLが登録されている場合はそちらを使用
        if settings.OHGIRI_JSON_URL:
            self.file_path = await self.savefile.download_file(settings.OHGIRI_JSON_URL,  json_path)
            logger.info(f'大喜利JSONのURLが登録されているため、JSONを保存しました。\n{self.file_path}')
        else:
            self.file_path = join(dirname(__file__), 'files' + os.sep + self.FILE)

    async def init_card(self):
        json_data = {}

        try:
            with open(self.file_path, mode='r') as f:
                json_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, EOFError) as e:
            # JSON変換失敗、読み込みに失敗したらなにもしない
            logger.error(e)

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
        logger.info(message)

    def deal(self):
        """
        カードを配る
        """
        self.turn = self.turn + 1
        self.description = ''
        self.hands = []
        self.field = []

        # 場に置かれるお題をひく
        self.odai =  self.deck_odai.pop()

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
        logger.info(message)
        target_deck.extend(target_discards)
        target_discards = []
        self.shuffle()

    def receive_card(self, card_id, member):
        """
        メンバーからカードを受け取ったときの処理
        受け取ったカードを場に出す
        メンバーの手持ちから受領したカードを除去
        cardNum {Int}
        member self.membersから取り出すキー
        """
        # 回答済のメンバーからカードを受け取った場合は、場に出されたカードとそのカードを入れ替える
        if self.members[member].answered:
            for answer in self.field:
                if answer.member == member:
                    self.members[member].cards.append(answer.card_id)
                    break
            self.field = [answer for answer in self.field if answer.member != member] 

        # 回答済に設定する
        self.members[member].answered = True
        self.field.append(Answer(card_id, member))

        # 受信したカード以外のカードをユーザに返す
        self.members[member].cards = [users_card_id for users_card_id in self.members[member].cards if users_card_id != card_id]

    def show_answer(self):
        """
        山札からカードを1枚加え、ランダムに混ぜた上で、回答を表示
        """
        # 山札からカードを引いてダミーの回答を作る
        self.field.append(Answer(self.deck_ans.pop(), 'dummy'))

        # 場に出た回答に画面表示用のランダムな番号を設定する。
        random_field = random.sample(self.field, len(self.field))
        for i in range(len(random_field)):
            random_field[i].answer_index = str(i)

        self.description = ''
        for sorted_answer in sorted(random_field, key=lambda answer: answer.answer_index):
            self.description += f'{str(sorted_answer.answer_index)}: {str(self.odai).replace("〇〇", "||" + self.ans_dict[sorted_answer.card_id] + "||")}\n'

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
        self.winCardsList.append(win_word)
        self.description += '> ' + win_word

        # 使用済みのカードを捨てる(お題と回答どちらも)
        self.discards_odai.append(self.odai)
        self.odai = ''
        for answer in self.field:
            self.discards_ans.append(str(answer.card_id))

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