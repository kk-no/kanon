import logging
from datetime import datetime

#GUIから受け取ったコマンドを判別し、USIクラスに受け渡す
def usi(player):
    #ログ出力設定
    logging.basicConfig(
        format = "%(asctime)s\t%(levelname)s\t%(message)s",
        datefmt = "%Y/%m/%d %H:%M:%S",
        filename = "log\game\log.txt",
        level = logging.DEBUG
    )
    while True:
        #標準入力から1行読み取る
        cmd_line = input()
        cmd = cmd_line.split(" ", 1)
        #ログ出力
        logging.info("[{}]".format(cmd_line))

        if cmd[0] == "usi":
            player.usi()

        elif cmd[0] == "setoption":
            option = cmd[1].split(" ")
            player.setoption(option)

        elif cmd[0] == "isready":
            player.isready()

        elif cmd[0] == "usinewgame":
            player.usinewgame()

        elif cmd[0] == "position":
            moves = cmd[1].split(" ")
            player.position(moves)

        elif cmd[0] == "go":
            player.go()

        elif cmd[0] == "quit":
            player.quit()
            break
        else:
            continue