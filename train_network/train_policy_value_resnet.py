import argparse
import random
import pickle
import os
import re
import logging
import numpy as np
import chainer
from chainer.backends import cuda
from chainer import optimizers, serializers, Variable
import chainer.functions as F

from kanon_shogi.common import *
from kanon_shogi.network.policy_value_resnet import PolicyValueResnet
from kanon_shogi.features import *
from kanon_shogi.read_kifu import *

"""
学習ネットワーク構築
※GPU必須
"""

def mini_batch(positions, i, batchsize):
    """
    ミニバッチ作成処理
    """
    mini_batch_data = []
    mini_batch_move = []
    mini_batch_win = []
    for b in range(batchsize):
        features, move, win = make_features(positions[i + b])
        mini_batch_data.append(features)
        mini_batch_move.append(move)
        mini_batch_win.append(win)

    return (Variable(cuda.to_gpu(np.array(mini_batch_data, dtype=np.float32))),
            Variable(cuda.to_gpu(np.array(mini_batch_move, dtype=np.int32))),
            Variable(cuda.to_gpu(np.array(mini_batch_win, dtype=np.int32).reshape((-1, 1)))))

def mini_batch_for_test(positions, batchsize):
    """
    テストデータの評価用ミニバッチ作成処理
    """
    mini_batch_data = []
    mini_batch_move = []
    mini_batch_win = []
    
    for b in range(batchsize):
        features, move, win = make_features(random.choice(positions))
        mini_batch_data.append(features)
        mini_batch_move.append(move)
        mini_batch_win.append(win)

    return (Variable(cuda.to_gpu(np.array(mini_batch_data, dtype=np.float32))),
            Variable(cuda.to_gpu(np.array(mini_batch_move, dtype=np.int32))),
            Variable(cuda.to_gpu(np.array(mini_batch_win, dtype=np.int32).reshape((-1, 1)))))

# 引数             |略 |説明
#________________________________________________________________________________________
# kifulist_train   |  | 訓練データに使用する棋譜一覧が書かれたテキストのパス
# kifulist_test    |  | テストデータに使用する棋譜一覧が書かれたテキストのパス
# --batchsize      |-b| ミニバッチサイズ、デフォルトは32
# --test_batchsize |  | テストバッチサイズ、デフォルトは512
# --epoch          |-e| 学習するエポック数
# --model          |  | モデルを保存する際のパス、デフォルトはmodel/model_policy
# --state          |  | オプティマイザの状態を保存する際のパス、デフォルトはmodel/state_policy
# --initmodel      |-i| 学習を再開する際に読み込むモデルの読み込み
# --resume         |-r| 学習を再開する際に読み込むオプティマイザの状態のパス
# --log            |  | ログを保存する場合のファイル名、指定なしの場合は標準出力される
# --lr             |  | 学習率、デフォルトは0.01
# --eval_interval  |-i| 学習の途中で評価を行う間隔(ミニバッチ単位)

parser = argparse.ArgumentParser()
parser.add_argument("kifulist_train", type = str, help = "train kifu list")
parser.add_argument("kifulist_test", type = str, help = "test kifu list")
parser.add_argument("--batchsize", "-b", type = int, default = 32,
                    help = "Number of positions in each mini-batch")
parser.add_argument("--blocks", type = int, default = 5, help = "Number of resnet blocks")
parser.add_argument("--test_batchsize", type = int, default = 512,
                    help = "Number of positions in each test mini-batch")
parser.add_argument("--epoch", "-e", type = int, default = 1,
                    help = "Number of epoch times")
parser.add_argument("--model", type = str, default = "model/model_policy_value_resnet",
                    help = "model file name")
parser.add_argument("--state", type = str, default = "model/state_policy_value_resnet",
                    help = "state file name")
parser.add_argument("--initmodel", "-m", default = "",
                    help = "Initialize the model given file")
parser.add_argument("--resume", "-r", default = "",
                    help = "Resume the optimization from snapshot")
parser.add_argument("--log", default = r"D:\project\kanon\log\train\log.txt", help = "log file path")
parser.add_argument("--lr", type = float, default = 0.01, help = "learning rate")
parser.add_argument("--eval_interval", "-i", type = int, default = 1000,
                    help = "eval interval")
args = parser.parse_args()

#ログ出力設定
#logger = getLogger(__name__)
logging.basicConfig(format = "%(asctime)s\t%(levelname)s\t%(message)s", datefmt = "%Y/%m/%d %H:%M:%S",
                    filename = args.log, level = logging.DEBUG)

#モデル構築
model = PolicyValueResnet(args.blocks)
#GPUに転送
model.to_gpu()

#勾配降下法に適用する最適化手法としてSGDを使用する
optimizer = optimizers.SGD(lr = args.lr)
optimizer.setup(model)

#モデルとオプティマイザの状態読み込み
if args.initmodel:
    #指定されていた場合モデルを読み込む
    logging.info("Load model from {}".format(args.initmodel))
    serializers.load_npz(args.initmodel, model)
if args.resume:
    #指定されていた場合オプティマイザの状態を読み込む
    logging.info("Load optimizer state from {}".format(args.resume))
    serializers.load_npz(args.resume, optimizer)

#棋譜読み込み(pickleで一度読み込んでメモリに保持した局面データをファイルに保存)
logging.info("read kifu start")

#保存済みのpickleファイルがある場合、pickleファイルを読み込む
#保存済みのpickleが無い場合、pickleファイルを保存する

#訓練データ
train_pickle_filename = re.sub(r"\..*?$", "", args.kifulist_train) + ".pickle"

if os.path.exists(train_pickle_filename):
    with open(train_pickle_filename, "rb") as f:
        positions_train = pickle.load(f)
    logging.info("load train pickle")
else:
    # positions_train = read_csa(args.kifulist_train)
    # positions_train = read_kif(args.kifulist_train)
    positions_train = read_kif24(args.kifulist_train)

#テストデータ
test_pickle_filename = re.sub(r"\..*?$", "", args.kifulist_test) + ".pickle"

if os.path.exists(test_pickle_filename):
    with open(test_pickle_filename, "rb") as f:
        positions_test = pickle.load(f)
    logging.info("load test pickle")
else:
    # positions_test = read_csa(args.kifulist_test)
    positions_test = read_kif(args.kifulist_test)

if not os.path.exists(train_pickle_filename):
    with open(train_pickle_filename, "wb") as f:
        pickle.dump(positions_train, f, pickle.HIGHEST_PROTOCOL)
    logging.info("save train pickle")
if not os.path.exists(test_pickle_filename):
    with open(test_pickle_filename, "wb") as f:
        pickle.dump(positions_test, f, pickle.HIGHEST_PROTOCOL)
    logging.info("save test pickle")

logging.info("read kifu end")

logging.info("train position num = {}".format(len(positions_train)))
logging.info("test position num = {}".format(len(positions_test)))

# 学習ループ
# マルチタスク学習を行う
#_______________________
# A.エポック数分繰り返し
#   訓練データのシャッフル
# B.ミニバッチ数分繰り返し
#   ミニバッチデータ作成
#   順伝播
#   損失計算
#   誤差逆伝播
#   一定間隔おきに評価
#   テストデータ評価

logging.info("start training")
itr = 0
sum_loss = 0
#エポック単位ループ
for e in range(args.epoch):
    #訓練データのシャッフル
    positions_train_shuffled = random.sample(positions_train, len(positions_train))

    itr_epoch = 0
    sum_loss_epoch = 0
    #ミニバッチ単位ループ
    for i in range(0, len(positions_train_shuffled) - args.batchsize, args.batchsize):
        #順伝播
        x, t1, t2 = mini_batch(positions_train_shuffled, i, args.batchsize)
        #方策ネットワーク用と価値ネットワークの出力
        y1, y2 = model(x)
        #勾配の初期化
        model.cleargrads()
        #損失計算(損失 = 方策ネットワーク出力の損失 + 価値ネットワーク出力の損失)
        loss = F.softmax_cross_entropy(y1, t1) + F.sigmoid_cross_entropy(y2, t2)
        #誤差逆伝播
        #勾配を計算
        loss.backward()
        #勾配を使用してニューラルネットワークのパラメータ更新を行う
        optimizer.update()
        #一定間隔で評価
        itr += 1
        sum_loss += loss.data
        itr_epoch += 1
        sum_loss_epoch += loss.data

        #一致率をログ出力する
        if optimizer.t % args.eval_interval == 0:
            x, t1, t2 = mini_batch_for_test(positions_test, args.test_batchsize)
            y1, y2 = model(x)
            logging.info("epoch = {}, iteration = {}, loss = {}, accuracy = {}".format(
                optimizer.epoch + 1, optimizer.t, sum_loss / itr,
                F.accuracy(y1, t1).data, F.binary_accuracy(y2, t2).data))
            itr = 0
            sum_loss = 0

    #テストデータの検証
    logging.info("validate test data")
    itr_test = 0
    sum_test_accuracy1 = 0
    sum_test_accuracy2 = 0
    for i in range(0, len(positions_test) - args.batchsize, args.batchsize):
        x, t1, t2 = mini_batch(positions_test, i, args.batchsize)
        y1, y2 = model(x)
        itr_test += 1
        sum_test_accuracy1 += F.accuracy(y1, t1).data
        sum_test_accuracy2 += F.binary_accuracy(y2, t2).data
    # log
    logging.info("epoch = {}, iteration = {}, train loss avr = {}, test accuracy = {}".format(
        optimizer.epoch + 1, optimizer.t, sum_loss_epoch / itr_epoch,
        sum_test_accuracy1 / itr_test, sum_test_accuracy2 / itr_test)
    )
    #次エポックの処理へ
    optimizer.new_epoch()

#モデルの保存
logging.info("save the model")
serializers.save_npz(args.model, model)
#オプティマイザの保存
logging.info("save the optimizer")
serializers.save_npz(args.state, optimizer)
