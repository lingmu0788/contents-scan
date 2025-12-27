#!/bin/bash

# ディレクトリ移動
cd "$(dirname "$0")/src" || exit 1

# 仮想環境のアクティブ化
source venv/bin/activate

# main.py を実行
python main.py





