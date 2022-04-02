# このBotについて

Discord用のBot。discord.pyのBot Commands Frameworkを使用して実装。大まかな機能ごとにCogを分けて開発しているため、不要な機能はCogを削除するだけで削除可能(一部機能に依存関係あり)。同様に、Cogを追加すれば機能追加も可能。

## Table of Contesnts

1. [機能](#機能)

1. [通常用カテゴリ(messagecog.pyで実装)](#通常用カテゴリmessagecogpyで実装)

1. [管理用カテゴリ(admincog.pyで実装)](#管理用カテゴリadmincogpyで実装)

1. [リアクションチャンネラーカテゴリ(reactionchannelercog.pyで実装)](#リアクションチャンネラーカテゴリreactionchannelercogpyで実装)

1. [ゲームカテゴリ(gamecog.pyで実装)](#ゲームカテゴリgamecogpyで実装)

1. [メッセージイベント用(onmessagecog.pyで実装)](#メッセージイベント用onmessagecogpyで実装)

1. [カテゴリ未設定](#カテゴリ未設定)

1. [環境変数の説明](#環境変数の説明)

1. [ローカルでの動かし方](#ローカルでの動かし方)

1. [Dockerでの動かし方](#dockerでの動かし方)

## 機能

### 通常用カテゴリ(messagecog.pyで実装)

`/group` メンバー数を指定：指定されたメンバー数になるように、適当な数のチームに分ける(コマンド実行者がボイスチャンネルに接続している必要アリ。サーバーに複数のボイスチャンネルがある必要アリ。Zoomのブレイクアウトルーム機能からインスパイアされ、作成したもの)  
![image(group)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/group.png?raw=true)

`/poll` 簡易的な投票機能（引数が1つの場合と2以上の場合で動作が変わる）。  

- 引数が1件の場合、YES, NOの投票となる  
![image(poll)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/poll_1.png?raw=true)  

- 引数が2件以上の場合、1つ目の引数がタイトルになり、2件目以降が投票される項目になる  
![image(poll-2)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/poll_2.png?raw=true)

`/team` チーム数指定：メンバー数が均等になるよう、指定された数に分ける(コマンド実行者がボイスチャンネルに接続している必要アリ。サーバーに複数のボイスチャンネルがある必要アリ。Zoomのブレイクアウトルーム機能からインスパイアされ、作成したもの)  
![image(team)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/team.png?raw=true)

`/vcmembers` ボイスチャンネルに接続しているメンバーリストを取得  
![image(vcmembers)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/vcmembers.png?raw=true)

`/radikoSearch` ラジコの番組表を検索する機能(**サブコマンド必須**)  

- サブコマンドなし(`/radikoSearch`)  
![image(radikoSearch)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/radikoSearch-1.png?raw=true)

- 通常の検索(`/radikoSearch normal`)  
  - もっとも単純なキーワードのみ指定  
![image(radikoSearch)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/radikoSearch_normal-1.png?raw=true)
  - キーワード、検索対象(過去、未来)、地域を指定  
![image(radikoSearch)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/radikoSearch_normal-2.png?raw=true)

- 日付を指定して検索(`/radikoSearch withDate`)  
  - sを付与し開始日付、eを付与し終了日付を設定できる
  - todayを設定すると当日として扱われる
![image(radikoSearch)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/radikoSearch_withDate-1.png?raw=true)
  - 日付の桁数で扱いが変わる(1桁はx日後として扱われ、2桁は当月の日付と扱われ、4桁は今年の月日として扱われる)  
![image(radikoSearch)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/radikoSearch_withDate-3.png?raw=true)

- `/countMessage`
  - メッセージを数え、ランキングにするコマンド
  - チャンネル名、（チャンネルごとに）数える数を指定できる。チャンネル名で`all`を指定するとすべてのチャンネルを数える

- `/countReaction`
  - リアクションを数え、ランキングにするコマンド
  - チャンネル名、（チャンネルごとに）数える数を指定できる。チャンネル名で`all`を指定するとすべてのチャンネルを数える

### 管理用カテゴリ(admincog.pyで実装)

`/channel` チャンネルを操作するコマンド（サブコマンド必須）。チャンネルの操作権限を渡すと、削除も可能だから嫌だなと思って作ったコマンド。  

- サブコマンド`make`でPublicなチャンネルを作成  
![image(channel_make)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/channel_make.png?raw=true)  

- サブコマンド`privateMake`でPrivateなチャンネルを作成  
![image(channel_privateMake)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/channel_privateMake.png?raw=true)  

- サブコマンド`roleDelete`でチャンネルからロールを削除  
![image(channel_roleDelete)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/channel_roleDelete.png?raw=true)  

- サブコマンド`roleDelete`でチャンネルからロールを削除失敗  
![image(channel_roleDelete-2)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/channel_roleDelete(error).png?raw=true)

`/getAuditLog` 監査ログを取得。とっても重たい上に見づらい。。。いつかなんとかしたい（[AuditLogChanges](https://discordpy.readthedocs.io/ja/latest/api.html#discord.AuditLogChanges)をわかりやすく表示する方法あるのかな。。。）

`/purge` メッセージを削除（自分とBot※のメッセージのみ削除される）※Botを削除対象とするかは[環境変数](#環境変数の説明)で指定可能。デフォルトは削除しない  
![image(purge)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/purge.png?raw=true)

`/deleteMessage` 指定したキーワードを含むメッセージを削除（自分とBot※のメッセージのみ削除される）※Botを削除対象とするかは[環境変数](#環境変数の説明)で指定可能。デフォルトは削除しない  
![image(deleteMessage)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/deleteMessage.png?raw=true)

### リアクションチャンネラーカテゴリ(reactionchannelercog.pyで実装)

`/reactionChanneler` リアクションチャンネラーを操作するコマンド（サブコマンド必須）。Slackのリアク字チャンネラーからインスパイアされ、作成したもの。

- リアクションチャンネラー追加  
![image(reactionChanneler_add)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/reactionChanneler_add.png?raw=true)

- リアクションチャンネラー削除  
![image(reactionChanneler_delete)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/reactionChanneler_delete.png?raw=true)

- リアクションチャンネラー表示  
![image(reactionChanneler_list)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/reactionChanneler_list.png?raw=true)

- リアクションチャンネラー全削除  
![image(reactionChanneler_purge)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/reactionChanneler_purge.png?raw=true)

その他、リアクションによって発動する機能をまとめている。:pushpin:をつけると、ピン留めする機能（メッセージ編集権限を与えるのは微妙だが、ピン留めさせたかったため）や、リアクションによってチャンネルに投稿する機能（リアクションチャンネラー機能とする）、:ok_hand:をつけると画像を保存する機能。

-:pushpin: のイベント  
![image(pushpin)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/event_pushpin.png?raw=True)

- リアクションチャンネラーの対象のリアクションを追加すると、  
![image(reactionChanneler)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/event_reaction.png?raw=True)

- あらかじめ指定されたチャンネルへリンクが投稿される  
![image(reactionChanneler-2)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/event_reaction_added.png?raw=True)

- [環境変数](#環境変数の説明)で設定しておけば、別のギルドのチャンネルへリンクを投稿することもできる(v0.7.1で実装)  
![image(reactionChanneler-3)](<https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/event_reaction_added(webhook).png?raw=True>)

### ゲームカテゴリ(gamecog.pyで実装)

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

### メッセージイベント用(onmessagecog.pyで実装)

- コマンドを使って実行する訳ではない機能
  - メッセージ投稿時に発動する、ScrapboxのURL展開機能([環境変数の説明](#環境変数の説明)SCRAPBOX_SID_AND_PROJECTNAMEで指定した対象のみ)
  ![image(help)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/on_message-scrapbox_url_expander.png?raw=true)  

  - メッセージ編集時(discordによるURLの展開時）に発動する、画像保存機能([環境変数の説明](#環境変数の説明)のSAVE_FILE_MESSAGEで指定した対象のみ)
![image(help)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/on_message_edit-save_image.png?raw=true)  

### カテゴリ未設定

`/help` ヘルプを表示(`/help channel`のように指定すると説明が返答される)  。コマンドが分からない、使い方が分からない、エイリアスが分からない時に使用

- `help`コマンドでこのBOTの使えるコマンドが表示される  
![image(help)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/help.png?raw=true)  

- `help`コマンドの結果、下線で表示された物(Cogに付けた機能名)について指定すると説明が表示される  
![image(help_category)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/help_category.png?raw=true)  

- コマンドを指定すれば、コマンドの説明が表示される  
![image(help_subcommand)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/help_subcommand.png?raw=true)  

- コマンドのサブコマンドも（あれば）指定でき、説明が表示される
![image(help_subcommand-2)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/help_subcommand_subcommand.png?raw=true)

## 環境変数の説明

- DISCORD_TOKEN = "discord_bot_token"
  - ここにDiscord Botのトークンを貼り付ける(とても重要。これをしないと動かない)
- LOG_LEVEL = INFO
  - ログレベルを設定したい場合、設定する。デフォルトはWARN。DEBUG, INFO, WARN, ERRORが設定可能
- AUDIT_LOG_SEND_CHANNEL = "guild1.audit_log_send_channel_id1;guild1.audit_log_send_channel_id1"
  - 管理用のチャンネルを記載する。`ギルドID.管理用のチャンネルID`の形式で記載する。**複数ある場合は、「;」を挟む**必要がある
- IS_HEROKU = True
  - Herokuで動かす場合、Trueとする（discordのチャンネルを使用し、リアクションチャネラーのデータが消えないように試みる（`reaction_channel_control`を作成し、そこにjsonデータを添付することでデータを保持する））
- SAVE_FILE_MESSAGE = "twitter"
  - 保存したい画像ファイルをもつURLの一部を指定。正規表現対応。複数ある場合はパイプ(|)などを駆使すること
- FIRST_REACTION_CHECK = True
  - すでにリアクションが付けられた物について、**リアクションチャンネラーを発動しないかどうか**の設定。基本的にはTrueがオススメ。寂しいときはFalseでもOK（何回だってチャンネルに転記されちゃいますが！）
- REACTION_CHANNELER_PERMIT_WEBHOOK_ID = "webhook_id"
  - リアクションチャンネラー機能の拡張設定。ここにWebhook IDか「all」という文字列を記載すると、リアクションチャンネラー機能でWebhookが使用できる(v0.7.1で実装)
    - リアクションを設定するだけで、別のギルドにメッセージを転送することができるようになる
  - この環境変数にWebhook IDがない、または、allが記載されていない場合、登録は可能だが、実際に実行はされない
    - 勝手にリアクションチャンネラーを登録され情報が流出することを防ぐため、環境変数で指定がない限り実行されないようにする(少し面倒かもしれない)
- SCRAPBOX_SID_AND_PROJECTNAME = "all:scrapbox_sid@projectname1,projectname2;guild1:scrapbox_sid@projectname3"
  - Scrapboxの展開をする際に使用する、sidとプロジェクト名についての設定
    - sidについては、[ScrapboxのprivateプロジェクトのAPIを叩く](https://scrapbox.io/nishio/Scrapbox%E3%81%AEprivate%E3%83%97%E3%83%AD%E3%82%B8%E3%82%A7%E3%82%AF%E3%83%88%E3%81%AEAPI%E3%82%92%E5%8F%A9%E3%81%8F)を参照し、注意点を把握した上対応すること
  - 設定が**複数存在する場合、「;」を挟む必要**がある
  - 左端のallの部分（対象ギルド）をギルドIDにすると、指定のギルドでしか展開しない。allの場合、すべてのギルドで発動
  - sidを適用したいプロジェクトが複数ある場合、「,」(コンマ)を挟む必要がある
- PURGE_TARGET_IS_ME_AND_BOT=False
  - `/purge`コマンド、`/deleteMessage`コマンドで削除する対象にBotを含むかの設定(設定がない場合は、**自分の投稿のみ**が削除対象)
- OHGIRI_JSON_URL=ohgiri_json_url
  - 大喜利機能で使用するJSONをURLから取得する場合に設定(Cogを読み込む際に取得されます)
- WORDWOLF_JSON_URL=wordwolf_json_url
  - ワードウルフ機能で使用するJSONをURLから取得する場合に設定(Cogを読み込む際に取得されます)。環境変数がない場合は、[jsonファイル](https://github.com/tetsuya-ki/discord-bot-heroku/blob/master/cogs/modules/files/wordwolf.json)を使用
- NGWORD_GAME_JSON_URL=ngword_game_json_url
  - NGワードゲーム機能で使用するJSONをURLから取得する場合に設定(Cogを読み込む際に取得されます)。環境変数がない場合は、[jsonファイル](https://github.com/tetsuya-ki/discord-bot-heroku/blob/master/cogs/modules/files/wordwolf.json)を使用
- COUNT_RANK_SETTING=5
  - `/countMessage`と`/countReaction`で使用するランキングの数を設定。未指定の場合、5として扱う。
- APPLICATION_ID="99999999"
  - あなたのBotの`APPLICATION ID`を指定する(スラッシュコマンドを使う上で設定が必須となります)
    - [開発者ポータル](https://discord.com/developers/applications/)の該当Botの`General Information`の上部にある、`APPLICATION ID`
- ENABLE_SLASH_COMMAND_GUILD_ID="99999999"
  - あなたのBotのテストする際はテスト用のギルドですぐに使用したいものと思われます(グローバルコマンドは適用まで時間がかかってしまう)
  - その場合、この環境変数にテスト用ギルドのIDを設定することで、すぐにスラッシュコマンドが試せます(ギルドコマンドとして設定する)

## ローカルでの動かし方

- 詳しくは[wiki](https://github.com/tetsuya-ki/discord-bot-heroku/wiki)を参照ください！

1. Install modules

    Mac: `pip3 install -r requirements.txt`  
    Windows: `py -3 pip install -r requirements.txt`

2. create .env  
`.env.sample`を参考に`.env`を作成する  
Botは[こちら](https://discord.com/developers/applications)で作成し、トークンを取得する（トークンは厳重に管理すること！）  
＊環境変数を修正する際は、[環境変数の説明](#環境変数の説明)を参照すること！

3. Start Bot

    Mac: `python3 assitantbot.py`  
    Windows: `py -3 assitantbot.py`

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
