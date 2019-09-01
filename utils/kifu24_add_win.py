import subprocess

"""
将棋倶楽部24形式の棋譜をKIF形式に揃える
"""

with open("kifu_list\\kifu_list.txt", "r") as f:
    for line in f.readlines():
        filepath = line.rstrip("\r\n")
        with open(filepath, "a") as k:
            # 指し手の数をカウント(wcを使用するため改行注意)
            move_count = int(subprocess.check_output(["wc", "-l", filepath]).decode().split(' ')[0]) - 6
            k.write("\nまで{0}手で{1}の勝ち".format(str(move_count), "先手" if move_count % 2 != 0 else "後手" ))
            del k