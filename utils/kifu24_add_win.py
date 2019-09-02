import subprocess

"""
将棋倶楽部24形式の棋譜をKIF形式に揃える
"""

with open("kifu_list\\kifu_list.txt", "r") as f:
    for line in f.readlines():
        filepath = line.rstrip("\r\n")
        print(filepath)

        move_list = []
        move_len = 0

        # 指し手の数をカウント
        with open(filepath, "r") as r:
            # 棋譜の読み込み
            move_list = r.readlines()
            # 対局情報6行と投了分1行を除く
            move_len = len(move_list) - 7
            del r

        # 勝敗追記処理
        with open(filepath, "a") as k:
            k.write("まで{0}手で{1}の勝ち".format(str(move_len), "先手" if move_len % 2 != 0 else "後手" ))
            del k