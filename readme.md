# このBotについて

Discord用のBot。discord.pyのBot Commands Frameworkを使用して実装。大まかな機能ごとにCogを分けて開発しているため、不要な機能はCogを削除するだけで削除可能(一部機能に依存関係あり)。同様に、Cogを追加すれば機能追加も可能。  
word-wolfブランチではゲーム機能に絞って機能開発していく(スラッシュコマンドやボタンに対応)。  
(参考)下記コマンドでブランチをクローンできる。  
`git clone -b word-wolf https://github.com/tetsuya-ki/discord-bot-heroku/tree/word-wolf`

## Table of Contesnts

1. [機能](#機能)

1. [ゲームカテゴリ(gamecog.pyで実装)](#ゲームカテゴリgamecogpyで実装)

1. [環境変数の説明](#環境変数の説明)

1. [ローカルでの動かし方](#ローカルでの動かし方)

1. [Dockerでの動かし方](#dockerでの動かし方)

## 機能

### ゲームカテゴリ(gamecog.pyで実装/あとで修正)

`/wordWolf` ワードウルフを行うコマンド。お題を修正したい場合[jsonファイル](https://github.com/tetsuya-ki/discord-bot-heroku/blob/master/cogs/modules/files/wordwolf.json)を変更すること

- ワードウルフ開始(これは時間が経過し、ネタバレ投稿された画像)  
![image(wordWolf-1)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/wordWolf-1.png?raw=True)

- BotからくるDMの様子  
![image(wordWolf-2)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/wordWolf-2.png?raw=True)

`/ngWordGame` NGワードゲームを行うコマンド。お題を修正したい場合[jsonファイル](https://github.com/tetsuya-ki/discord-bot-heroku/blob/master/cogs/modules/files/wordwolf.json)を変更すること(ワードウルフ機能と共用)

- NGワードゲーム開始(これは時間が経過し、ネタバレ投稿された画像)  
![image(ngWordGame-1)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/ngwordgame-1.png?raw=True)

- BotからくるDMの様子  
![image(ngWordGame-2)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/ngwordgame-2.png?raw=True)

`/coyoteGame` コヨーテを行うコマンド

- コヨーテ開始(説明が長いですがやれば分かります！)  
![image(coyoteGame_start)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/coyoteGame_start.png?raw=True)

- コヨーテ開始やディール時のDMの様子  
![image(coyoteGame_DM)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/coyoteGame_DM.png?raw=True)

- コヨーテのディール(カードを配る)  
![image(coyoteGame_deal)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/coyoteGame_deal.png?raw=True)

- コヨーテ開始(自分でデッキを設定)  
![image(coyoteGame_setDeckAndStart)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/coyoteGame_setDeckAndStart.png?raw=True)

- コヨーテの状況説明  
![image(coyoteGame_description)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/coyoteGame_description.png?raw=True)

- コヨーテの状況説明(ネタバレ有)  
![image(coyoteGame_descriptionAll)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/coyoteGame_descriptionAll.png?raw=True)

`/ohgiriGame` 大喜利を始めるコマンド。お題を修正したい場合[jsonファイル](https://github.com/tetsuya-ki/discord-bot-heroku/blob/master/cogs/modules/files/ohgiri.json)を変更するか、[後述の環境変数](#環境変数の説明)でJSONを返すURLを設定すること

- 大喜利開始(数字を渡すと、勝利点が設定される。すぐ終わらせたいなら、`/o start 1`等で実行)  
![image(ohgiri_start)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/ohgiri_start.png?raw=True)
- 大喜利開始後、BotからくるDMの様子(ここに表示された番号を回答として選択)  
![image(ohgiri_dm)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/ohgiri_dm.png?raw=True)
- 大喜利の回答を選んだところ  
![image(ohgiri_answer)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/ohgiri_answer.png?raw=True)
- 大喜利の状況説明(経過ターン、現在の親、お題、それぞれの得点などが表示される)  
![image(ohgiri_description)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/ohgiri_description.png?raw=True)
- 大喜利の回答カードを捨てるコマンド(いい回答が手札にない場合使うコマンド)  
![image(ohgiri_discard)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/ohgiri_discard.png?raw=True)
- 親が回答を選択  
![image(ohgiri_choice)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/ohgiri_choice.png?raw=True)
- 親が回答を選択しゲーム終了するところ(誰かが勝利点に到達したら終了)  
![image(ohgiri_choice2_game_over)](<https://raw.githubusercontent.com/tetsuya-ki/images/main/discord-bot-heroku/ohgiri_choice2(game_over).png>)

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
- ENABLE_SLASH_COMMAND_GUILD_ID_LIST=__あなたのGuild_IDを入力(数字/複数あるなら;を挟むこと。グローバルコマンドの場合は入力しないこと！(その場合1時間程度登録に時間がかかる可能性あり))__
  - この環境変数を使用する場合、ソースの修正をしてください
  - それぞれのメソッドにある、@cog_ext.cog_slashのguildsについてのコメントアウトを解除する必要があります
  - スラッシュコマンドを有効にするギルドID(複数ある場合は「;」を間に挟むこと)。Botを登録していないギルドを登録するとエラーになってしまうので、登録しており、スラッシュコマンドを有効な状態で招待しておいてください。
  - 例
    - 1件の場合: ENABLE_SLASH_COMMAND_GUILD_ID_LIST=18471289371923
    - 2件の場合: ENABLE_SLASH_COMMAND_GUILD_ID_LIST=18471289371923;1389103890128390

## ローカルでの動かし方

- 詳しくは[wiki](https://github.com/tetsuya-ki/discord-bot-heroku/wiki)を参照ください！

1. Install Poetry

    <https://python-poetry.org/docs/#installation>

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
