import shogi

"""
USIエンジン基底クラス
"""

class BasePlayer:
    def __init__(self):
        self.board = shogi.Board()

    #usiコマンドに対する処理
    def usi(self):
        pass

    #usinewgameコマンドに対する処理
    def usinewgame(self):
        pass

    #setoptionコマンドに対する処理
    def setoption(self, option):
        pass

    #isreadyコマンドに対する処理
    def isready(self):
        pass

    #positionコマンドに対する処理
    #エンジン毎に分ける必要がないため基底クラスに記述
    def position(self, moves):
        if moves[0] == "startpos":
            self.board.reset()
            for move in moves[2:]:
                self.board.push_usi(move)

        elif moves[0] == "sfen":
            self.board.set_sfen(" ".join(moves[1:]))

        #デバッグ出力
        print(self.board.sfen())

    #goコマンドに対する処理
    def go(self):
        pass

    #quitコマンドに対する処理
    def quit(self):
        pass
    