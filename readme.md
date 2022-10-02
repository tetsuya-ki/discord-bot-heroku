# このBotについて

Discord用のBot。discord.pyのBot Commands Frameworkを使用して実装。大まかな機能ごとにCogを分けて開発しているため、不要な機能はCogを削除するだけで削除可能(一部機能に依存関係あり)。同様に、Cogを追加すれば機能追加も可能。  
gameブランチではゲーム機能に絞って機能開発していく(スラッシュコマンドやボタンに対応)。  
(参考)下記コマンドでブランチをクローンできる。  
`git clone -b game https://github.com/tetsuya-ki/discord-bot-heroku/tree/game`

## Table of Contesnts

1. [機能](#機能)

1. [ゲームカテゴリ(gamecog.pyで実装)](#ゲームカテゴリgamecogpyで実装)

1. [環境変数の説明](#環境変数の説明)

1. [ローカルでの動かし方(Poetry)](#ローカルでの動かし方poetry)

1. [ローカルでの動かし方](#ローカルでの動かし方poetryを使用しない方法)

1. [Dockerでの動かし方](#dockerでの動かし方)

## 機能
### ゲームカテゴリ(gamecog.pyで実装)

`/start-word-wolf` ワードウルフを行うコマンド。お題を修正したい場合[jsonファイル](https://github.com/tetsuya-ki/discord-bot-heroku/blob/master/cogs/modules/files/wordwolf.json)を変更すること

- ワードウルフ開始(これは時間が経過し、ネタバレ投稿された画像)  
![image(wordWolf-1)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/wordWolf-1.png?raw=True)

- BotからくるDMの様子  
![image(wordWolf-2)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/wordWolf-2.png?raw=True)

`/start-ng-word-game` NGワードゲームを行うコマンド。お題を修正したい場合[jsonファイル](https://github.com/tetsuya-ki/discord-bot-heroku/blob/master/cogs/modules/files/wordwolf.json)を変更すること(ワードウルフ機能と共用)

- NGワードゲーム開始
  - ボタンで参加、離脱、開始できるように変更
![image(wordWolf-1)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/start-word-wolf.png?raw=True)  

- 時間が経過し、ネタバレ投稿された画像
![image(ngWordGame-1)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/ngwordgame-1.png?raw=True)

- BotからくるDMの様子  
![image(ngWordGame-2)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/ngwordgame-2.png?raw=True)

`/coyoteGame` コヨーテを行うコマンド

- コヨーテ開始(説明が長いですがやれば分かります！)
  - 説明の長さが選べます
    - 普通: 普通にゲームできる程度省略したもの(デフォルト)
    - 詳しく: 詳しく説明
    - 無し: 説明なし(Botでやったことある人たち用)
![image(coyoteGame_start)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/coyoteGame_start_0.png?raw=True)
![image(coyoteGame_start)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/coyoteGame_start.png?raw=True)
  - 参加するボタンで参加できます
- コヨーテ開始
  - 相手のカードを見るボタン  
![image(coyote_button_display)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/coyote_button_display-card.png?raw=True)
  - コヨーテ！(モーダルでコヨーテする相手のID、相手の値を入力)  
![image(coyote_button_coyote)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/coyote_button_coyote.png?raw=True)
  - カード能力説明
    - 特殊カードなどの意味を忘れたときに使用します  
![image(coyote_button_description-card)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/coyote_button_description-card.png?raw=True)
  - 状況説明
    - 現在相手のHPやターンなど忘れたときに使用します  
![image(coyote_button_description-all)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/coyote_button_description.png?raw=True)
  - 状況説明(ネタバレ)
    - 基本的には使わないでください
    - 場に出してあるカードも含めて表示されます(説明などの時に使用してください)
      - 灰色がかっているところをクリック(タップ)すると表示されます
![image(coyote_button_description-all))](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/coyote_button_description-all.png?raw=True)
  - コヨーテ！されると、その結果が表示されます
![image(coyote_button_coyote-2)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/coyote_button_coyote-2.png?raw=True)
  - その後、「状況説明(全て)」を押すこともできます(山札も見えるのでやめた方がいいかもしれません)
![image(coyote_button2_description-all)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/coyote_button2_description-all.png?raw=True)
- 次ターン以降
  - ディールすることで次ターンが始まります
![image(coyote_button2_deal)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/coyote_button2_deal.png?raw=True)
- コヨーテの終了
  - 生き残りが1名になった時点でゲームが終了します
![image(coyote_finish)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/coyote_finish.png?raw=True)

- コヨーテ開始(自分でデッキを設定)
  - デフォルトのデッキが初期表示されているので好きに編集します
  - 新しい能力の追加などは不可能です(-100〜100までの数値の追加や、特殊カードの枚数変更などのみ)
![image(coyoteGame_setDeckAndStart)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/coyote_button_deck.png?raw=True)

`/start-ohgiri-game` 大喜利を始めるコマンド。お題を修正したい場合[jsonファイル](https://github.com/tetsuya-ki/discord-bot-heroku/blob/master/cogs/modules/files/ohgiri.json)を変更するか、[後述の環境変数](#環境変数の説明)でJSONを返すURLを設定すること

- 大喜利開始(数字を渡すと、勝利点が設定される。すぐ終わらせたいなら、`/start-ohgiri-game win_point:1`等で実行)  
  - 参加方法については[v1.0.0](https://github.com/tetsuya-ki/discord-bot-heroku/releases/tag/v1.0.0)からボタン式に変更  
  - コマンドは以下のように表示される  
![image(ohgiri_start)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/start-ohgiri-game.png?raw=True)
  - コマンドを実行すると以下のように返信される  
![image(ohgiri_start2)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/start-ohgiri-game_2.png?raw=True)
  - 参加ボタンを押すと、ゲームに参加する  
![image(ohgiri_button_join)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/ohgiri-game_button-join.png?raw=True)
  - 離脱ボタンを押すと、ゲームから離脱する(ゲーム中に離脱できてしまうがやらない方が良い)  
![image(ohgiri_button_leave)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/ohgiri-game_button-leave.png?raw=True)
  - 開始ボタンを押すと、ゲームが始まる(人数が集まっている場合)  
![image(ohgiri_button_start)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/ohgiri--game_button-start.png?raw=True)
  - ターンが始まると、お題が与えられる  
    - 回答、状況説明、カードを捨てる(1ポイント減点)ができる  
![image(ohgiri_turn)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/ohgiri-game_turn.png?raw=True)
- 「回答する」ボタンを押して、メニューから大喜利の回答を選ぶ
  - 複数選択するパターンもあり、選ばれた順番に回答を格納する(表示順ではない)  
![image(ohgiri_answer)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/ohgiri-game_button-answer.png?raw=True)
- 「状況を確認する」ボタンを押すと、大喜利の状況説明される(経過ターン、現在の親、お題、それぞれの得点などが表示される)  
![image(ohgiri_description)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/ohgiri-game_button-description.png?raw=True)
- 大喜利の回答カードを捨てることも可能(いい回答が手札にない場合使うコマンド)  
![image(ohgiri_discard)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/ohgiri-game_button-discard.png?raw=True)
- 親が回答を選択
  - ダミーのカードが1枚紛れ込んでおり、ダミーを選択した場合は親のポイントが1点減点され、親が継続する
  - 人間のカードが選択された場合、選ばれた人間に1ポイント加点し、その人物が次の親になる
![image(ohgiri_choice)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/ohgiri-game_button-choice.png?raw=True)

- 親が回答を選択しゲーム終了するところ(誰かが勝利点に到達したら終了)  
![image(ohgiri_choice2_game_over)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/ohgiri-game_finish.png?raw=True)

## 環境変数の説明

- DISCORD_TOKEN = "discord_bot_token"
  - ここにDiscord Botのトークンを貼り付ける(とても重要。これをしないと動かない)
- LOG_LEVEL = INFO
  - ログレベルを設定したい場合、設定する。デフォルトはWARN。DEBUG, INFO, WARN, ERRORが設定可能
- IS_HEROKU = True
  - Herokuで動かす場合、Trueとする（discordのチャンネルを使用し、リアクションチャネラーのデータが消えないように試みる（`reaction_channel_control`を作成し、そこにjsonデータを添付することでデータを保持する））
- OHGIRI_JSON_URL=ohgiri_json_url
  - 大喜利機能で使用するJSONをURLから取得する場合に設定(Cogを読み込む際に取得されます)
- WORDWOLF_JSON_URL=wordwolf_json_url
  - ワードウルフ機能で使用するJSONをURLから取得する場合に設定(Cogを読み込む際に取得されます)。環境変数がない場合は、[jsonファイル](https://github.com/tetsuya-ki/discord-bot-heroku/blob/master/cogs/modules/files/wordwolf.json)を使用
- NGWORD_GAME_JSON_URL=ngword_game_json_url
  - NGワードゲーム機能で使用するJSONをURLから取得する場合に設定(Cogを読み込む際に取得されます)。環境変数がない場合は、[jsonファイル](https://github.com/tetsuya-ki/discord-bot-heroku/blob/master/cogs/modules/files/wordwolf.json)を使用
- USE_IF_AVAILABLE_FILE=True
  - 各JSONファイルがあればそちらを優先的に使用するかどうか。デフォルトはTrue。[v1.0.0](https://github.com/tetsuya-ki/discord-bot-heroku/releases/tag/v1.0.0)で追加
    - テストする時、毎回同じものをダウンロードしていて意味ないなと思ったため追加
- APPLICATION_ID="99999999"
  - あなたのBotの`APPLICATION ID`を指定する(スラッシュコマンドを使う上で設定が必須となります)。[v1.0.0](https://github.com/tetsuya-ki/discord-bot-heroku/releases/tag/v1.0.0)で追加
    - [開発者ポータル](https://discord.com/developers/applications/)の該当Botの`General Information`の上部にある、`APPLICATION ID`
- ENABLE_SLASH_COMMAND_GUILD_ID="99999999"
  - あなたのBotのテストする際はテスト用のギルドですぐに使用したいものと思われます(グローバルコマンドは適用まで時間がかかってしまう)
  - その場合、この環境変数にテスト用ギルドのIDを設定することで、すぐにスラッシュコマンドが試せます(ギルドコマンドとして設定する)。[v1.0.0](https://github.com/tetsuya-ki/discord-bot-heroku/releases/tag/v1.0.0)で追加
    - 設定が**複数存在する場合、「;」を挟む必要**がある
    - 例) ENABLE_SLASH_COMMAND_GUILD_ID="99999999;88888888;77777777"

## ローカルでの動かし方(Poetry)

1. Install Poetry  
<https://python-poetry.org/docs/#installation>

2. Install modules  
`poetry install`

3. create .env  
`.env.sample`を参考に`.env`を作成する  
Botは[こちら](https://discord.com/developers/applications)で作成し、トークンを取得する（トークンは厳重に管理すること！）  
＊環境変数を修正する際は、[環境変数の説明](#環境変数の説明)を参照すること！

4. Start Bot  
`poetry run python assistantbot.py`

## ローカルでの動かし方(Poetryを使用しない方法)

- 詳しくは[wiki](https://github.com/tetsuya-ki/discord-bot-heroku/wiki)を参照ください！

1. Install modules  
Mac: `pip3 install -r requirements.txt`  
Windows: `py -3 pip install -r requirements.txt`

2. Install modules

    Mac/Windows: `poetry update`  

3. create .env  
`.env.sample`を参考に`.env`を作成する  
Botは[こちら](https://discord.com/developers/applications)で作成し、トークンを取得する（トークンは厳重に管理すること！）  
＊環境変数を修正する際は、[環境変数の説明](#環境変数の説明)を参照すること！

4. Start Bot

    Mac/Windows: `poetry run python assitantbot.py`  

## Dockerでの動かし方

- 詳しくは[wiki](https://github.com/tetsuya-ki/discord-bot-heroku/wiki)を参照ください！

1. Docker imageを作成（または、Docker HubからPull）  
1-1. Make Docker Image(Build by yourself)  
`docker build . -t discordbotheroku:latest .`  
1-2. Pull from Docker Hub  
`docker pull tk2812/discord-bot-heroku:latest`

2. Make .env-docker file  
`.env-docker.sample`を参考に`.env-docker`を作成する(=の両端はスペース無しが良さそう。以下のスタイルなら動いた)  
Botは[こちら](https://discord.com/developers/applications)で作成し、トークンを取得する（トークンは厳重に管理すること！）  
＊環境変数を修正する際は、[環境変数の説明](#環境変数の説明)を参照すること！

    ```sh
    DISCORD_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    ...
    ```

3. Run docker container  
    このBOTの場合、環境変数はファイル指定がオススメだが、普通に指定しても動くはず(Build by yourself)。  
    `docker run --env-file ./cogs/modules/files/.env-docker discordbotheroku:latest`
    もしくは  
    `docker run --env-file ./cogs/modules/files/.env-docker docker.io/tk2812/discord-bot-heroku:latest`
