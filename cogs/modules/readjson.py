import json
import os
from os.path import join, dirname

class ReadJson:
    FILE = 'wordwolf.json'

    def __init__(self):
        self.dict = {} # 辞書
        self.list = [] # リスト

    def readJson(self):

        # 読み込み
        try:
            file_path = join(dirname(__file__), 'files' + os.sep + self.FILE)
            with open(file_path, mode='r') as f:
                self.dict = json.load(f)
            # joinするので文字列に変換し、リストに追加する
            self.list = list(self.dict.keys())

        except FileNotFoundError:
            # 読み込みに失敗したらなにもしない
            print
        except json.JSONDecodeError:
            # JSON変換失敗したらなにもしない
            print
        except EOFError:
            # 読み込みに失敗したらなにもしない
            print
