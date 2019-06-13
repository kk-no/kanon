import numpy as np
import shogi
import copy

from kanon_shogi.common import *

"""
局面から入力特徴を作成する
"""

#piece_bb[15]     :駒ごとの配置の配列(0:空白、1:歩、2:香...)
#occupied[2]      :手番ごとの占有している座標の配列(0:先手、1:後手)
#piece_in_hand[2] :手番ごとの持ち駒の配列(0:先手、1:後手)

def make_input_features(piece_bb, occupied, pieces_in_hand):
    features = []
    for color in shogi.COLORS:
        #盤上
        for piece_type in shogi.PIECE_TYPES_WITH_NONE[1:]:
            bb = piece_bb[piece_type] & occupied[color]
            #np.zeros:要素が0の配列を指定した要素数で生成する
            feature = np.zeros(9 * 9)
            for pos in shogi.SQUARES:
                if bb & shogi.BB_SQUARES[pos] > 0:
                    feature[pos] = 1
            features.append(feature.reshape(9, 9))

        #持ち駒
        for piece_type in range(1, 8):
            for n in range(shogi.MAX_PIECES_IN_HAND[piece_type]):
                if piece_type in pieces_in_hand[color] and n < pieces_in_hand[color][piece_type]:
                    #np.ones:要素が1の配列を指定した要素数で生成する
                    feature = np.ones(9 * 9)
                else:
                    feature = np.zeros(9 * 9)
                #reshape:1次元配列を2次元配列に変換
                features.append(feature.reshape((9, 9)))

    return features

def make_output_label(move, color):
    #移動先
    move_to = move.to_square
    #移動元
    move_from = move.from_square

    #白(後手)の場合版を回転
    if color == shogi.WHITE:
        move_to = SQUARES_R180[move_to]
        if move_from is not None:
            move_from = SQUARES_R180[move_from]

    if move_from is not None:
        #盤上の駒を動かした場合

        #divmod:割り算の商と余りを同時に取得する
        to_y, to_x = divmod(move_to, 9)
        from_y, from_x = divmod(move_from, 9)
        dir_x = to_x - from_x
        dir_y = to_y - from_y

        #移動種類判定
        if dir_y < 0 and dir_x == 0:
            move_direction = UP
        elif dir_y == -2 and dir_x == -1:
            move_direction = UP2_LEFT
        elif dir_y == -2 and dir_x == 1:
            move_direction = UP2_RIGHT
        elif dir_y < 0 and dir_x < 0:
            move_direction = UP_LEFT
        elif dir_y < 0 and dir_x > 0:
            move_direction = UP_RIGHT
        elif dir_y == 0 and dir_x < 0:
            move_direction = LEFT
        elif dir_y == 0 and dir_x > 0:
            move_direction = RIGHT
        elif dir_y > 0 and dir_x == 0:
            move_direction = DOWN
        elif dir_y > 0 and dir_x < 0:
            move_direction = DOWN_LEFT
        elif dir_y > 0 and dir_x > 0:
            move_direction = DOWN_RIGHT

        #成判定
        if move.promotion:
            move_direction = MOVE_DIRECTION_PROMOTED[move_direction]
    else:
        #持ち駒
        move_direction = len(MOVE_DIRECTION) + move.drop_piece_type - 1

    move_label = 9 * 9 * move_direction + move_to
    return move_label

#局面と出力ラベルのデータから、入力特徴と出力ラベルの形式に変換
def make_features(position):
    piece_bb, occupied, pieces_in_hand, move, win = position
    features = make_input_features(piece_bb, occupied, pieces_in_hand)

    return (features, move, win)

#入力特徴作成処理
def make_input_features_from_board(board):
    if board.turn == shogi.BLACK:
        piece_bb = board.piece_bb
        occupied = (board.occupied[shogi.BLACK],
                    board.occupied[shogi.WHITE])
        pieces_in_hand = (board.pieces_in_hand[shogi.BLACK],
                        board.pieces_in_hand[shogi.WHITE])

    else:
        piece_bb = [bb_rotate_180(bb) for bb in board.piece_bb]
        occupied = (bb_rotate_180(board.occupied[shogi.WHITE]),
                    bb_rotate_180(board.occupied[shogi.BLACK]))
        pieces_in_hand = (board.pieces_in_hand[shogi.WHITE],
                        board.pieces_in_hand[shogi.BLACK])

    return make_input_features(piece_bb, occupied, pieces_in_hand)