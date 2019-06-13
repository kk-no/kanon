import argparse
import os
import re
import statistics

"""
指定条件でCSA形式の棋譜ファイルを抽出する
python filter_csa.py ディレクトリ指定で実行
"""

#=====================================
# 抽出条件(条件に満たない場合は削除する)
rating = 3500
move = 75
kifu_dir = "D:\project\kanon\kifu"
#=====================================

#parser = argparse.ArgumentParser()
#parser.add_argument("dir", type = str)
#args = parser.parse_args()

def find_all_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            #yield:処理の一時中断と分割
            yield os.path.join(root, file)

ptn_rate = re.compile(r"^'(black|white)_rate:.*:(.*)$")

kifu_count = 0
rates = []
for filepath in find_all_files(kifu_dir):
    rate = {}
    move_len = 0
    toryo = False
    for line in open(filepath, "r", encoding = "utf-8"):
        line = line.strip()
        m = ptn_rate.match(line)
        if m:
            rate[m.group(1)] = float(m.group(2))
        if line[:1] == "+" or line[:1] == "-":
            move_len += 1
        if line == "%TORYO":
            toryo = True
    if not toryo or move_len <= move or len(rate) < 2 or min(rate.values()) < rating:
        os.remove(filepath)
    else:
        kifu_count += 1
        rates.extend([_ for _ in rate.values()])

print("kifu count : ", kifu_count)
print("rate mean : {}".format(statistics.mean(rates)))
print("rate median : {}".format(statistics.median(rates)))
print("rate max : {}".format(max(rates)))
print("rate min : {}".format(min(rates)))