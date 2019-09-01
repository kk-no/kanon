import argparse
from datetime import datetime
import os
import random

"""
棋譜ディレクトリから訓練データ、テストデータを振り分ける
それぞれのリストを生成する
"""

#コマンド引数設定
parser = argparse.ArgumentParser()
parser.add_argument("--filetype", type = str, default = "kif")
parser.add_argument("--ratio", type = float, default = 0.9)
args = parser.parse_args()

#棋譜保存ディレクトリ
kifu_dir = "D:\project\kanon\kifu\{}".format(args.filetype)
#出力ファイル名
file_name = "kifulist{0:%Y%m%d}".format(datetime.now())

kifu_list = []
for root, dirs, files in os.walk(kifu_dir):
    for file in files:
        kifu_list.append(os.path.join(root, file))

#シャッフル
random.shuffle(kifu_list)

#訓練データとテストデータに分けて保存
train_len = int(len(kifu_list) * args.ratio)
#訓練データの保存
with open(file_name + "_train.txt", "w") as f:
    for i in range(train_len):
        f.write(kifu_list[i])
        f.write("\n")

#テストデータの保存
with open(file_name + "_test.txt", "w") as f:
    for i in range(train_len, len(kifu_list)):
        f.write(kifu_list[i])
        f.write("\n")

print("total kifu num = {}".format(len(kifu_list)))
print("train kifu num = {}".format(train_len))
print("test kifu num = {}".format(len(kifu_list) - train_len))
