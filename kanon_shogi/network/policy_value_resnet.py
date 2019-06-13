from chainer import Chain
import chainer.functions as F
import chainer.links as L

from kanon_shogi.common import *

#チャンネル数
ch = 192
#全結合層のノード数
fcl = 256

class Block(Chain):
    def __init__(self):
        super(Block, self).__init__()
        with self.init_scope():
            self.conv1 = L.Convolution2D(in_channels = ch,
                                            out_channels = ch,
                                            ksize = 3,
                                            pad = 1, nobias = True)
            self.bn1 = L.BatchNormalization(ch)
            self.conv2 = L.Convolution2D(in_channels = ch,
                                            out_channels = ch,
                                            ksize = 3,
                                            pad = 1, nobias = True)
            self.bn2 = L.BatchNormalization(ch)

    def __call__(self, x):
        h1 = F.relu(self.bn1(self.conv1(x)))
        h2 = self.bn2(self.conv2(h1))
        return F.relu(x + h2)

class PolicyValueResnet(Chain):
    def __init__(self, blocks = 5):
        super(PolicyValueResnet, self).__init__()
        self.blocks = blocks
        with self.init_scope():
            self.l1 = L.Convolution2D(in_channels = 104, out_channels = ch, ksize = 3, pad = 1)
            for i in range(1, blocks):
                self.add_link("b{}".format(i), Block())
            #policy network
            self.lpolicy = L.Convolution2D(in_channels = ch,
                                            out_channels = MOVE_DIRECTION_LABEL_NUM,
                                            ksize = 1, nobias = True)
            self.lpolicy_bias = L.Bias(shape=(9 * 9 * MOVE_DIRECTION_LABEL_NUM))
            #value network
            self.lvalue1 = L.Convolution2D(in_channels = ch,
                                            out_channels = MOVE_DIRECTION_LABEL_NUM,
                                            ksize = 1)
            self.lvalue2 = L.Linear(9 * 9 * MOVE_DIRECTION_LABEL_NUM, fcl)
            self.lvalue3 = L.Linear(fcl, 1)

    def __call__(self, x):
        h = F.relu(self.l1(x))
        for i in range(1, self.blocks):
            h = self['b{}'.format(i)](h)
        #policy network
        h_policy = self.lpolicy(h)
        policy = self.lpolicy_bias(F.reshape(h_policy, (-1, 9 * 9 * MOVE_DIRECTION_LABEL_NUM)))
        #value network
        h_value = F.relu(self.lvalue1(h))
        h_value = F.relu(self.lvalue2(h_value))
        value = self.lvalue3(h_value)

        return policy, value