# mercari_bot

メルカリの受け取り評価がされない場合に，フォローコメントを投稿するスクリプトです．

## 準備

必要なモジュールをインストールします．
後述する Docker を使った方法で実行する場合は，インストール不要です．

```
sudo apt install -y python3-yaml
sudo apt install -y python3-coloredlogs
sudo apt install -y python3-pip
sudo apt install -y smem
sudo apt install -y libnss3
sudo apt install -y chromium-browser
sudo snap install chromium

pip3 install selenium
pip3 install webdriver-manager
pip3 install SpeechRecognition
```

## 設定

ログイン情報やフォロー内容を `config.yml` で指定します．

`config.example.yml` を名前変更して設定してください．
設定方法方はファイルを見ていただけばわかると思います．

## 実行方法

```
./mercari_follow.py
```

# ライセンス

Apache License Version 2.0 を適用します．
