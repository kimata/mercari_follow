# mercari_follow

メルカリの出品アイテムに自動的にコメントを投稿するスクリプトです．
受け取り評価がされない場合に，フォローコメントを投稿するのに便利です．

## 準備

必要なモジュールをインストールします．
後述する Docker を使った方法で実行する場合は，インストール不要です．

```
# Poetry をインストール済みの場合は次の2行は不要
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
poetry install
```

## 設定

ログイン情報やフォロー内容を `config.yaml` で指定します．

`config.example.yaml` を名前変更して設定してください．
設定方法方はファイルを見ていただけばわかると思います．

## 実行方法

```
poetry run ./app/mercari_follow.py
```

# ライセンス

Apache License Version 2.0 を適用します．
