# 前処理の設計

- 以下の記事を参考にして前処理を丁寧に実装する
  - [自然言語処理における前処理の種類とその威力 | Qiita](https://qiita.com/Hironsan/items/2466fe0f344115aff177)
  - [NLP Pipeline 101 With Basic Code Example — Feature Extraction](https://medium.com/voice-tech-podcast/nlp-pipeline-101-with-basic-code-example-feature-extraction-ea9894ed8daf)

## 構成モジュール

1. <font color=blue>SlackMsgExtraction</font> : **Slack App**
   1. Slackのメッセージ群の抽出処理を担当するモジュール
   2. Slackからメッセージ、チャンネル情報、ユーザー情報などを抽出する
2. <font color=blue>Cleaning</font> : **Text Processing**
   1. クリーニング処理を担当するモジュール
   2. テキスト中のノイズ(htmlタグとか)を除去する
3. <font color=blue>MorphologicalAnalysis(Tokenization + Part-of-speech tagging)</font> : **Text Processing**
   1. 文字列の形態素解析処理を担当するモジュール
   2. 形態素解析、指定したタグの文字列のみ抽出、分かち書きなどのメソッドを提供する
4. <font color=blue>Normalization</font> : **Text Processing**
   1. 単語の正規化処理を担当するモジュール
   2. 文字種の統一や大文字小文字変換などを行う
5. <font color=blue>StopWordRemoval</font> : **Text Processing**
   1. ストップワード除去処理を担当するモジュール
6. <font color=blue>ImportantWordExtraction</font> : **Feature Extraction**
   1. 重要単語の抽出処理を担当するモジュール
   2. tf-idf算出を用いる
7. <font color=blue>WordVectorization</font> : **Feature Extraction**
   1. 文字列のベクトル化処理を担当するモジュール
   2. word2vecを用いる
   3. 文字列情報をベクトル表現に置き換えて、有用な情報の抽出及びそのサポートを行う

## 処理の流れ

1. 前処理：Slackメッセージ群取得、ユーザーごとにグルーピング
2. クリーニング処理 <font color=blue>（該当モジュール：Cleaning）</font>
   1. url文字列
   2. HTMLタグ、Javascriptタグ
   3. [HTML特殊文字](http://www.shurey.com/js/labo/character.html) ※特に引用を表す">"など（&gtとして出現）
   4. [BeautifulSoupを利用した参考になりそうなコード](https://github.com/Hironsan/natural-language-preprocessings/blob/master/preprocessings/ja/cleaning.py)
   5. 正規表現による文字列抽出結果を[簡単にチェックできるツール](https://regex101.com/)
3. 文章の単語分割処理 <font color=blue>（該当モジュール：MorphologicalAnalysis）</font>
   1. Janomeを使う
   2. 辞書はNEologdを利用する
   3. [MecabとJanomeを使った単語分割の参考になりそうなコード](https://github.com/Hironsan/natural-language-preprocessings/blob/master/preprocessings/ja/tokenizer.py)
4. 単語の正規化処理 <font color=blue>（該当モジュール：Normalization）</font>
   1. 文字種の統一
      1. 半角文字を全角文字に統一
      2. アルファベットを小文字に統一
   2. 数字の置き換え
      1. 数字を全て0にする
   3. ~~辞書を用いた単語の統一~~ <font color=red>**これは単語の分散表現により実現する**</font>
      1. ソニーをSonyなど。
      2. [参考になりそうなコード](https://github.com/Hironsan/natural-language-preprocessings/blob/master/preprocessings/ja/normalization.py)
5. ストップワードの除去処理 <font color=blue>（該当モジュール：StopWordRemoval）</font>
   1. [Slothlib](http://svn.sourceforge.jp/svnroot/slothlib/CSharp/Version1/SlothLib/NLP/Filter/StopWord/word/Japanese.txt)を利用して、一般的に利用可能なレベルのストップワードを除去する
6. 特徴抽出
   1. 重要単語の判定 <font color=blue>（該当モジュール：ImportantWordExtraction）</font>
   2. 単語の分散表現 <font color=blue>（該当モジュール：WordVectorization）</font>
7. やりたい処理
   1. 都度調整
