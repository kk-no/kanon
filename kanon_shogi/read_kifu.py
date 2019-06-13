import shogi
import shogi.CSA
import shogi.KIF
import copy

from kanon_shogi.features import *

"""
棋譜の読み込みを行う
"""
# KIF形式
def read_kif(kifu_list_files):
    positions = []
    with open(kifu_list_files, "r") as f:
        for line in f.readlines():
            #rstrip:指定文字列の削除
            filepath = line.rstrip("\r\n")
            kifu = shogi.KIF.Parser.parse_file(filepath)[0]
            #条件式が真の場合の値 if 条件式 else 条件式が偽の場合の値
            win_color = shogi.BLACK if kifu["win"] == "b" else shogi.WHITE
            board = shogi.Board()
            for move in kifu["moves"]:
                #盤面の回転(後手番の場合180度回転)
                if board.turn == shogi.BLACK:
                    #先手番
                    piece_bb = copy.deepcopy(board.piece_bb)
                    occupied = copy.deepcopy(
                        (board.occupied[shogi.BLACK]
                        ,board.occupied[shogi.WHITE]))
                    piece_in_hand = copy.deepcopy(
                        (board.pieces_in_hand[shogi.BLACK]
                        ,board.pieces_in_hand[shogi.WHITE]))
                else:
                    #後手番
                    piece_bb = [bb_rotate_180(bb) for bb in board.piece_bb]
                    occupied = (bb_rotate_180(board.occupied[shogi.WHITE]),
                                bb_rotate_180(board.occupied[shogi.BLACK]))
                    piece_in_hand = copy.deepcopy(
                        (board.pieces_in_hand[shogi.WHITE]
                        ,board.pieces_in_hand[shogi.BLACK]))

                #指し手ラベル
                move_label = make_output_label(shogi.Move.from_usi(move), board.turn)

                #結果
                win = 1 if win_color == board.turn else 0

                positions.append((piece_bb, occupied, piece_in_hand, move_label, win))
                board.push_usi(move)
    return positions

# CSA形式
def read_csa(kifu_list_files):
    positions = []
    with open(kifu_list_files, "r") as f:
        for line in f.readlines():
            #rstrip:指定文字列の削除
            filepath = line.rstrip("\r\n")
            kifu = shogi.CSA.Parser.parse_file(filepath)[0]
            #条件式が真の場合の値 if 条件式 else 条件式が偽の場合の値
            win_color = shogi.BLACK if kifu["win"] == "b" else shogi.WHITE
            board = shogi.Board()
            for move in kifu["moves"]:
                #盤面の回転(後手番の場合180度回転)
                if board.turn == shogi.BLACK:
                    #先手番
                    piece_bb = copy.deepcopy(board.piece_bb)
                    occupied = copy.deepcopy(
                        (board.occupied[shogi.BLACK]
                        ,board.occupied[shogi.WHITE]))
                    piece_in_hand = copy.deepcopy(
                        (board.pieces_in_hand[shogi.BLACK]
                        ,board.pieces_in_hand[shogi.WHITE]))
                else:
                    #後手番
                    piece_bb = [bb_rotate_180(bb) for bb in board.piece_bb]
                    occupied = (bb_rotate_180(board.occupied[shogi.WHITE]),
                                bb_rotate_180(board.occupied[shogi.BLACK]))
                    piece_in_hand = copy.deepcopy(
                        (board.pieces_in_hand[shogi.WHITE]
                        ,board.pieces_in_hand[shogi.BLACK]))

                #指し手ラベル
                move_label = make_output_label(shogi.Move.from_usi(move), board.turn)

                #結果
                win = 1 if win_color == board.turn else 0

                positions.append((piece_bb, occupied, piece_in_hand, move_label, win))
                board.push_usi(move)
    return positions