import random
import discord
from logging import getLogger

logger = getLogger(__name__)

class CoyoteMember:
    DEFAULT_HP = 3
    def __init__(self):
        self.HP = self.DEFAULT_HP
        self.card = ''
        self.isDead = False

    def setCard(self, card: str):
        self.card = card

    def damage(self, number: int):
        self.HP = self.HP -number
        if self.HP == 0:
            self.isDead = True

class Coyote:
    # DEFAULT_DECK = [20, 15, 15, 10, 10, 10, 5, 5, 5, 5, 4, 4, 4, 4, 3, 3, 3, 3, 2, 2, 2, 2, 1, 1, 1, 1, 0, 0, 0, '0(Night)', -5, -5, -10, '*2(Chief)', 'Max->0(Fox)', '?(Cave)']
    DEFAULT_DECK = [20,'Max->0(Fox)','?(Cave)','?(Cave)']

    def __init__(self):
        self.members = {}
        self.body = []
        self.deck = self.DEFAULT_DECK
        self.hands = []
        self.discards = []
        self.turn = 0
        self.description = ''

    def set(self, members):
        for member in members:
            coyoteMember = CoyoteMember()
            self.members[member] = coyoteMember

    def shuffle(self):
        self.deck.extend(self.discards)
        self.discards = []
        random.shuffle(self.deck)
        self.description += 'シャッフルしました。\n'

    def deal(self):
        self.turn = self.turn + 1
        self.description = ''
        self.hands = []

        for member in self.members:
            card = self.deck.pop()
            self.members[member].setCard(card)
            self.hands.append(card)
            if len(self.deck) == 0:
                self.shuffle()

    def coyote(self, me: discord.Member, you: discord.Member, number):
        # 計算
        coyotes = self.calc()

        #　コヨーテの結果の判定
        if number > coyotes:
            self.members[you].damage(1)
            self.description += f'{number} > {coyotes} → 「コヨーテ！」の勝ち({me.display_name}が正しい！)\n'
            self.description += f'{you.display_name}に1点ダメージ。'
            if self.members[you].isDead:
                self.description += f'{you.display_name}は死にました。\n'
                self.body.append(self.members.pop(you))
        else:
            self.members[me].damage(1)
            self.description += f'{number} <= {coyotes} → 「コヨーテ！」の負け({you.display_name}が正しい！)\n'
            self.description += f'{me.display_name}に1点ダメージ。'
            if self.members[me].isDead:
                self.description += f'{me.display_name}は死にました。\n'
                self.body.append(self.members.pop(me))

        # 一人になったら、勝利
        if len(self.members) == 1:
            for member in self.members:
                self.description += f'{member.display_name}の勝ちです！　おめでとうございます！！'
        else:
            self.description += '現在の状況:'
            for member in self.members:
                self.description += f'{member.display_name}さん(HP:{self.members[member].HP}) '

    def calc(self):
        # [変数名 for 変数名 in 元のリスト if 条件式]
        normal_hands = [i for i in self.hands if self.is_num(i)]
        special_hands = [i for i in self.hands if not self.is_num(i)]
        additional_hands = []
        shuffle_flg = False

        # Caveカードの効果
        cave_hands = [i for i in special_hands if ('Cave' in str(i))]
        for card in cave_hands:
            while(True):
                self.discards.append(card)
                additional_card = self.deck.pop()
                self.hands.append(additional_card)
                self.description += f'{card}の効果で、1枚山札から引いた(値は{additional_card})。\n'

                # 引いたもので再計算
                normal_hands = [i for i in self.hands if self.is_num(i)]
                special_hands = [i for i in self.hands if (not self.is_num(i) and not 'Cave' in str(i))]
                if len(self.deck) == 0:
                    self.shuffle()
                if not 'Cave' in str(additional_card):
                    break

        # Chiefカードを集計
        chief_hands = [i for i in special_hands if ('Chief' in str(i))]
        special_hands = [i for i in special_hands if not 'Chief' in str(i)]

        for card in special_hands:
            card = str(card)

            # Nightカードの効果
            if 'Night'in card:
                self.discards.append(card)
                normal_hands.append(0)
                shuffle_flg = True
                self.description += f'{card}の効果で、計算終了後に山札/捨て札を混ぜてシャッフルする。\n'

            # Foxカードの効果
            if 'Fox' in card:
                self.discards.append(card)
                num_hands = [i for i in normal_hands if self.is_num(i)]
                if len(num_hands) == 0:
                    max_num = 0
                else:
                    max_num = max(num_hands)
                normal_hands.append(-max_num)
                self.description += f'{card}の効果で、この場で最大の値である{max_num}を0にした。\n'

        # 計算
        coyotes = 0
        self.description += '通常カードの計算：'
        for card in normal_hands:
            self.discards.append(card)
            coyotes += card
            if card >= 0:
                self.description += f'+ {str(card)}'
            else:
                self.description += f'{str(card)}'
        self.description += '\n'

        # Chiefカードの効果
        for card in chief_hands:
            self.discards.append(card)
            coyotes = coyotes * 2
            self.description += f'{card}の効果で、2倍にした。\n'

        if shuffle_flg:
            self.shuffle()

        return coyotes

    def is_num(self, num):
        try:
            int(num)
        except:
            return False
        return True