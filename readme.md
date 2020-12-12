# このBotについて

Discord用のBot。discord.pyのBot Commands Frameworkを使用して実装。大まかな機能ごとにCogを分けて開発しているため、不要な機能はCogを削除するだけで削除可能。同様に、Cogを追加すれば機能追加も可能。

## Table of Contesnts

1. [機能](#機能)

1. [通常用カテゴリ(messagecog.pyで実装)](#通常用カテゴリmessagecogpyで実装)

1. [管理用カテゴリ(admincog.pyで実装)](#管理用カテゴリadmincogpyで実装)

1. [リアクションチャンネラーカテゴリ(reactionchannelercog.pyで実装)](#リアクションチャンネラーカテゴリreactionchannelercogpyで実装)

1. [ゲームカテゴリ(gamecog.pyで実装)](#ゲームカテゴリgamecog.pyで実装)

1. [カテゴリ未設定](#カテゴリ未設定)

1. [環境変数の説明](#環境変数の説明)

1. [ローカルでの動かし方](#ローカルでの動かし方)

1. [Dockerでの動かし方](#Dockerでの動かし方)

## 機能

### 通常用カテゴリ(messagecog.pyで実装)

`/group` メンバー数を指定：指定されたメンバー数になるように、適当な数のチームに分ける(コマンド実行者がボイスチャンネルに接続している必要アリ。サーバーに複数のボイスチャンネルがある必要アリ。Zoomのブレイクアウトルーム機能からインスパイアされ、作成したもの)  
![image(group](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/group.png?raw=true)

`/poll` 簡易的な投票機能（引数が1つの場合と2以上の場合で動作が変わる）。  

- 引数が1件の場合、YES, NOの投票となる  
![image(group](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/poll_1.png?raw=true)  

- 引数が2件以上の場合、1つ目の引数がタイトルになり、2件目以降が投票される項目になる  
![image(group](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/poll_2.png?raw=true)

`/team` チーム数指定：メンバー数が均等になるよう、指定された数に分ける(コマンド実行者がボイスチャンネルに接続している必要アリ。サーバーに複数のボイスチャンネルがある必要アリ。Zoomのブレイクアウトルーム機能からインスパイアされ、作成したもの)  
![image(group](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/team.png?raw=true)

`/vcmembers` ボイスチャンネルに接続しているメンバーリストを取得  
![image(group](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/vcmembers.png?raw=true)

### 管理用カテゴリ(admincog.pyで実装)

`/channel` チャンネルを操作するコマンド（サブコマンド必須）。チャンネルの操作権限を渡すと、削除も可能だから嫌だなと思って作ったコマンド。  

- サブコマンド`make`でPublicなチャンネルを作成  
![image(group](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/channel_make.png?raw=true)  

- サブコマンド`privateMake`でPrivateなチャンネルを作成  
![image(group](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/channel_privateMake.png?raw=true)  

- サブコマンド`roleDelete`でチャンネルからロールを削除  
![image(group](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/channel_roleDelete.png?raw=true)  

- サブコマンド`roleDelete`でチャンネルからロールを削除失敗  
![image(group](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/channel_roleDelete(error).png?raw=true)

`/getAuditLog` 監査ログを取得。とっても重たい上に見づらい。。。いつかなんとかしたい（[AuditLogChanges](https://discordpy.readthedocs.io/ja/latest/api.html#discord.AuditLogChanges)をわかりやすく表示する方法あるのかな。。。）

`/purge` メッセージを削除（Botと自分のメッセージのみ削除される）  
![image(group](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/purge.png?raw=true)

### リアクションチャンネラーカテゴリ(reactionchannelercog.pyで実装)

`/reactionChanneler` リアクションチャンネラーを操作するコマンド（サブコマンド必須）。Slackのリアク字チャンネラーからインスパイアされ、作成したもの。

- リアクションチャンネラー追加  
![image(group](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/reactionChanneler_add.png?raw=true)

- リアクションチャンネラー削除  
![image(group](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/reactionChanneler_delete.png?raw=true)

- リアクションチャンネラー表示  
![image(group](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/reactionChanneler_list.png?raw=true)

- リアクションチャンネラー全削除  
![image(group](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/reactionChanneler_purge.png?raw=true)

その他、リアクションによって発動する機能をまとめている。:pushpin:をつけると、ピン留めする機能（メッセージ編集権限を与えるのは微妙だが、ピン留めさせたかったため）や、リアクションによってチャンネルに投稿する機能（リアクションチャンネラー機能とする）

-:pushpin:　のイベント  
![image(pushpin)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/event_pushpin.png?raw=True)

- リアクションチャンネラーの対象のリアクションを追加すると、  
![image(pushpin)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/event_reaction.png?raw=True)

- あらかじめ指定されたチャンネルへリンクが投稿される  
![image(pushpin)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/event_reaction_added.png?raw=True)

### ゲームカテゴリ(gamecog.pyで実装)

`/wordwolf` ワードウルフを行うコマンド

### カテゴリ未設定

`/help` ヘルプを表示(`/help channel`のように指定すると説明が返答される)  

- `help`コマンドでこのBOTの使えるコマンドが表示される  
![image(group](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/help.png?raw=true)  

- サブコマンドも（あれば）で指定できる  
![image(group](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/help_subcommand.png?raw=true)  

- サブコマンドのサブコマンドも（あれば）指定できる  
![image(group](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/help_subcommand_subcommand.png?raw=true)

## 環境変数の説明

- DISCORD_TOKEN = 'discord_bot_token'
  - ここにDiscordのトークンを貼り付ける
- IS_DEBUG = True
  - デバッグ用のログを出力したい場合のみTrueとする。これがFalseや存在しない場合はデバッグ用のログが出力されない
- AUDIT_LOG_SEND_CHANNEL = "guild1.audit_log_send_channel_id1;guild1.audit_log_send_channel_id1"
  - 管理用のチャンネルを記載する。ギルドID.管理用のチャンネルIDの形式で記載する。複数ある場合は、「;」を挟む必要がある。
- IS_HEROKU = True
  - Herokuで動かす場合、Trueとする（discordのチャンネルを使用し、リアクションチャネラーのデータが消えないように試みる（`reaction_channel_control`を作成し、そこにjsonデータを添付することでデータを保持する））

## ローカルでの動かし方

1. Install modules

    Mac: `pip3 install -r requirements.txt`  
    Windows: `py -3 pip install -r requirements.txt`

2. create .env  
`.env.sample`を参考に`.env`を作成する  
Botは[こちら](https://discord.com/developers/applications)で作成し、トークンを取得する（トークンは厳重に管理すること！）

3. Start Bot

    Mac: `python3 assitantbot.py`  
    Windows: `py -3 assitantbot.py`

## Dockerでの動かし方

1. Docker imageを作成（または、Docker HubからPull）

1-1. Make Docker Image(Build by yourself)  
    `docker build --pull --rm -f Dockerfile -t discordbotheroku:latest .`

1-2. Pull from Docker Hub
    `docker pull tk2812/discord-bot-heroku:latest`

2. Make .env-docker file  
`.env-docker.sample`を参考に`.env-docker`を作成する(=の両端はスペース無しが良さそう。以下のスタイルなら動いた)  
Botは[こちら](https://discord.com/developers/applications)で作成し、トークンを取得する（トークンは厳重に管理すること！）  

    ```sh
    DISCORD_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    ...
    ```

3. Run docker container  
    このBOTの場合、環境変数はファイル指定がオススメだが、普通に指定しても動くはず(Build by yourself)。  
    `docker run --env-file ./cogs/modules/files/.env-docker discordbotheroku:latest`
    もしくは  
    `docker run --env-file ./cogs/modules/files/.env-docker docker.io/tk2812/discord-bot-heroku:latest`
