# このBotについて

Discord用のBot。discord.pyのBot Commands Frameworkを使用して実装。大まかな機能ごとにCogを分けて開発しているため、不要な機能はCogを削除するだけで削除可能(一部機能に依存関係あり)。同様に、Cogを追加すれば機能追加も可能。

## Table of Contesnts

1. [機能](#機能)

1. [通常用カテゴリ(messagecog.pyで実装)](#通常用カテゴリmessagecogpyで実装)

1. [管理用カテゴリ(admincog.pyで実装)](#管理用カテゴリadmincogpyで実装)

1. [リアクションチャンネラーカテゴリ(reactionchannelercog.pyで実装)](#リアクションチャンネラーカテゴリreactionchannelercogpyで実装)

1. [ゲームカテゴリ(gamecog.pyで実装)＊一部WIP](#ゲームカテゴリgamecogpyで実装)

1. [メッセージイベント用(onmessagecog.pyで実装)](#メッセージイベント用onmessagecogpyで実装)

1. [環境変数の説明](#環境変数の説明)

1. [ローカルでの動かし方(Poetry)](#ローカルでの動かし方poetry)

1. [ローカルでの動かし方](#ローカルでの動かし方poetryを使用しない方法)

1. [Dockerでの動かし方](#dockerでの動かし方)

## 機能

### 通常用カテゴリ(messagecog.pyで実装)

`/voice group` メンバー数を指定：指定されたメンバー数になるように、適当な数のチームに分ける(コマンド実行者がボイスチャンネルに接続している必要アリ。サーバーに複数のボイスチャンネルがある必要アリ。Zoomのブレイクアウトルーム機能からインスパイアされ、作成したもの)  
![image(voice group)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/voice_group.png?raw=true)

`/voice team` チーム数指定：メンバー数が均等になるよう、指定された数に分ける(コマンド実行者がボイスチャンネルに接続している必要アリ。サーバーに複数のボイスチャンネルがある必要アリ。Zoomのブレイクアウトルーム機能からインスパイアされ、作成したもの)  
![image(voice team)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/voice_team.png?raw=true)

`/voice members` ボイスチャンネルに接続しているメンバーリストを取得  
![image(voice members)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/voice_members.png?raw=true)

`/simple-poll` 簡易的な投票機能（「/」なしの場合と、ありの場合で動作が変わる）。  

- 「/」なしの場合、YES, NOの投票となる  
- 「/」あり場合、「/」より前の部分がタイトルになり、それ以降が投票される項目になる  
![image(poll-2)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/simple-poll_0.png?raw=true)
![image(poll-2)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/simple-poll_1.png?raw=true)

`/radikoSearch` ラジコの番組表を検索する機能

- もっとも単純なキーワードのみ指定  
![image(radikoSearch)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/radiko-search_0.png?raw=true)
![image(radikoSearch)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/radiko-search_1.png?raw=true)

- 検索対象(過去、未来、すべて)はプルダウン、地域はオートコンプリートで指定  
  - 地域についてはdiscord側の制限で25個までしか設定できなかったため、全地域で使用できない点に注意(申し訳ないですが、近場の他県で検索ください)
![image(radikoSearch)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/radiko-search_area.png?raw=true)
- 以下、画像は差し代わっていないが、過去と同様の仕組みとなっている
  - 0を設定すると当日として扱われる
![image(radikoSearch)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/radikoSearch_withDate-1.png?raw=true)
  - 日付の桁数で扱いが変わる(1桁はx日後として扱われ、2桁は当月の日付と扱われ、4桁は今年の月日として扱われる)  
![image(radikoSearch)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/radikoSearch_withDate-3.png?raw=true)

- `/count-message`
  - メッセージを数え、ランキングにするコマンド
  - チャンネル名、（チャンネルごとに）数える数などを指定できる
    - all_flagで、「すべて」を指定するとすべてのチャンネルを数える
      - channelで特定のチャンネルのみ数えることも可能
    - count_numbersでチャンネルごとに読み込む数を指定できる
    - ranking_numで集計する順位を指定できる(「5」と入力した場合、5位まで表示)
    - reply_is_hiddenで結果を全員に見せるか指定できる(デフォルトは公開)
![image(count-message)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/count-message.png?raw=true)

- `/count-reaction`
  - リアクションを数え、ランキングにするコマンド
  - チャンネル名、（チャンネルごとに）数える数などを指定できる
    - all_flagで、「すべて」を指定するとすべてのチャンネルを数える
      - channelで特定のチャンネルのみ数えることも可能
    - count_numbersでチャンネルごとに読み込む数を指定できる
    - ranking_numで集計する順位を指定できる(「5」と入力した場合、5位まで表示)
    - reply_is_hiddenで結果を全員に見せるか指定できる(デフォルトは公開)
![image(count-reaction)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/count-reaction.png?raw=true)

### 管理用カテゴリ(admincog.pyで実装)

`/channel` チャンネルを操作するコマンド（サブコマンド必須）。チャンネルの操作権限を渡すと、削除も可能だから嫌だなと思って作ったコマンド。  

- `channel make`でPublicなチャンネルを作成  
  - ただし、カテゴリの権限に同期されるため注意(想定通りの結果にならない可能性アリ)
![image(channel_make)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/channel_make.png?raw=true)  

- `channel private-make`でPrivateなチャンネルを作成  
![image(channel_privateMake)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/channel_private-make.png?raw=true)  

- `channel role-delete`でチャンネルからロールを削除  
![image(channel_roleDelete)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/channel_role-delete.png?raw=true)  

- `channel role-delete`でチャンネルからロールを削除失敗  
![image(channel_roleDelete-2)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/channel_role-delete(failed).png?raw=true)

- `channel topic`でチャンネルにトピックを設定  
![image(channel_topic)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/channel_topic.png?raw=true)  

`/channel delete-message` 指定したキーワードを含むメッセージを削除（自分とBot※のメッセージのみ削除される）※Botを削除対象とするかは[環境変数](#環境変数の説明)で指定可能。デフォルトは削除しない  
![image(deleteMessage)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/channel_delete-message_0.png?raw=true)
![image(deleteMessage)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/channel_delete-message_1.png?raw=true)

`/get-audit-log` 監査ログを取得。とっても重たい上に見づらい。。。いつかなんとかしたい（[AuditLogChanges](https://discordpy.readthedocs.io/ja/latest/api.html#discord.AuditLogChanges)をわかりやすく表示する方法あるのかな。。。）

`/purge` メッセージを削除（自分とBot※のメッセージのみ削除される）※Botを削除対象とするかは[環境変数](#環境変数の説明)で指定可能。デフォルトは削除しない  
![image(purge)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/purge.png?raw=true)

### リアクションチャンネラーカテゴリ(reactionchannelercog.pyで実装)

`/reaction-channeler` リアクションチャンネラーを操作するコマンド（サブコマンド必須）。Slackのリアク字チャンネラーからインスパイアされ、作成したもの。

- リアクションチャンネラー追加  
![image(reaction-channeler_add)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/reaction-channeler-add_0.png?raw=true)
![image(reaction-channeler_add)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/reaction-channeler-add_1.png?raw=true)

- リアクションチャンネラー削除  
![image(reaction-channeler_delete)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/reaction-channeler-remove_0.png?raw=true)
![image(reaction-channeler_delete)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/reaction-channeler-remove_1.png?raw=true)

- リアクションチャンネラー表示  
![image(reactionChanneler_list)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/reaction-channerler_list.png?raw=true)

- リアクションチャンネラー全削除  
![image(reaction-channeler_purge)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/reaction-channeler-purge.png?raw=true)

その他、リアクションによって発動する機能をまとめている。:pushpin:をつけると、ピン留めする機能（メッセージ編集権限を与えるのは微妙だが、ピン留めさせたかったため）や、リアクションによってチャンネルに投稿する機能（リアクションチャンネラー機能とする）、:ok_hand:をつけると画像を保存する機能。

-:pushpin: のイベント  
![image(pushpin)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/event_pushpin.png?raw=True)

- リアクションチャンネラーの対象のリアクションを追加すると、  
![image(reaction-channeler)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/event_reaction.png?raw=True)

- あらかじめ指定されたチャンネルへリンクが投稿される  
![image(reaction-channeler-2)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/event_reaction_added.png?raw=True)

- [v1.0.0](https://github.com/tetsuya-ki/discord-bot-heroku/releases/tag/v1.0.0)で画像も表示するように改善  
![image(reaction-channeler-2)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku_v2/on_reaction-channneler.png?raw=True)

- [環境変数](#環境変数の説明)で設定しておけば、別のギルドのチャンネルへリンクを投稿することもできる([v0.7.1](https://github.com/tetsuya-ki/discord-bot-heroku/releases/tag/v0.7.1)で実装)  
![image(reaction-channeler-3)](<https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/event_reaction_added(webhook).png?raw=True>)

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

`/coyoteGame` コヨーテを行うコマンド([v1.0.0](https://github.com/tetsuya-ki/discord-bot-heroku/releases/tag/v1.0.0)では使用できず/dicord.py v2.0対応中)

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

### メッセージイベント用(onmessagecog.pyで実装)

- コマンドを使って実行する訳ではない機能
  - メッセージ投稿時に発動する、ScrapboxのURL展開機能([環境変数の説明](#環境変数の説明)SCRAPBOX_SID_AND_PROJECTNAMEで指定した対象のみ)
  ![image(help)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/on_message-scrapbox_url_expander.png?raw=true)  

  - メッセージ編集時(discordによるURLの展開時）に発動する、画像保存機能([環境変数の説明](#環境変数の説明)のSAVE_FILE_MESSAGEで指定した対象のみ)
![image(help)](https://github.com/tetsuya-ki/images/blob/main/discord-bot-heroku/on_message_edit-save_image.png?raw=true)  

### カテゴリ未設定(削除されました)

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
  - リアクションチャンネラー機能の拡張設定。ここにWebhook IDか「all」という文字列を記載すると、リアクションチャンネラー機能でWebhookが使用できる([v0.7.1](https://github.com/tetsuya-ki/discord-bot-heroku/releases/tag/v0.7.1)で追加で実装)
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
  - `/purge`コマンド、`/channel delete-message`コマンドで削除する対象にBotを含むかの設定(設定がない場合は、**自分の投稿のみ**が削除対象)
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

### 廃止された環境変数

- COUNT_RANK_SETTING
  - `/countMessage`と`/countReaction`で使用するランキングの数を保持する環境変数
  - スラッシュコマンドで指摘できるようにしたため、[v1.0.0](https://github.com/tetsuya-ki/discord-bot-heroku/releases/tag/v1.0.0)で廃止

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

2. create .env  
`.env.sample`を参考に`.env`を作成する  
Botは[こちら](https://discord.com/developers/applications)で作成し、トークンを取得する（トークンは厳重に管理すること！）  
＊環境変数を修正する際は、[環境変数の説明](#環境変数の説明)を参照すること！

3. Start Bot  
Mac: `python3 assistantbot.py`  
Windows: `py -3 assistantbot.py`

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
