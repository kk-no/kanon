import codecs
import os
import shogi

#=====================================
# 抽出条件(条件に満たない場合は削除する)
rating = 2800
move = 75
kifu_dir = "D:\develop\shogi\script\kif"
#=====================================

def find_all_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            yield os.path.join(root, file)

def read_kifu(path):
    with codecs.open(path, 'r', 'shift_jis') as f:
        kif_str = f.read()

        max_move = 0
        names = [None, None]
        rate = [None, None]
        win = None

        kif_str = kif_str.replace('\r\n', '\n').replace('\r', '\n')
        for line in kif_str.split("\n"):
            if len(line) == 0 or line[0] == "*":
                pass
            elif '\uff1a' in line:
                # 対局情報
                key, value = line.split('\uff1a', 1)
                value = value.rstrip('\u3000').rstrip("\u0029")
                if key == '\u5148\u624b' or key == '\u4e0b\u624b':
                    # 先手
                    bname, brate = value.split("\u0028")
                    names[shogi.BLACK] = bname
                    rate[shogi.BLACK] = brate
                elif key == '\u5f8c\u624b' or key == '\u4e0a\u624b':
                    # 後手
                    wname, wrate = value.split("\u0028")
                    names[shogi.WHITE] = wname
                    rate[shogi.WHITE] = wrate
                else:
                    pass
            else:
                # 棋譜
                if "\u6295\u4e86" in line:
                    # 投了時手数
                    max_move = int(line.split("\u0020")[0])
                    # 投了を手数に含めない
                    max_move = max_move - 1
                    if max_move % 2 == 0:
                        # 後手勝ち
                        win = "w"
                    else:
                        # 先手勝ち
                        win = "b"

    summary = {
        "names": names,
        "rate": rate,
        "move": max_move,
        "win": win
    }

    return summary

kifu_count = 0
for filepath in find_all_files(kifu_dir):
    kifu = read_kifu(filepath)
    if int(kifu["rate"][0]) < rating or int(kifu["rate"][1]) < rating or int(kifu["move"]) < move:
        os.remove(filepath)
    else:
        kifu_count += 1

# 抽出結果出力
print("kifu count: ", kifu_count)