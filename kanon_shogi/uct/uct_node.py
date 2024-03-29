import shogi

"""
ゲーム木における各ノードにハッシュを振り分けて管理
ハッシュ化はゾブリストハッシュを使用する
ノードの情報は配列で保持、アクセスはハッシュの数値とする
"""

#2のn乗であること
UCT_HASH_SIZE = 4096
#SIZEの90%とする
UCT_HASH_LIMIT = UCT_HASH_SIZE * 9 / 10

#未展開のノードのインデックス
NOT_EXPANDED = -1

def hash_to_index(hash):
    return ((hash & 0xffffffff) ^ ((hash >> 32) & 0xffffffff)) & (UCT_HASH_SIZE - 1)

class NodeHashEntry:
    def __init__(self):
        #ゾブリストハッシュの値
        self.hash = 0
        #手番
        self.color = 0
        #ゲーム開始の手番
        self.moves = 0
        #ハッシュ使用中判別フラグ
        self.flag = False

class NodeHash:
    def __init__(self):
        self.used = 0
        self.enough_size = True
        self.node_hash = None

    def __getitem__(self, i):
        return self.node_hash[i]

    def initialize(self):
        """
        UCTノードのハッシュの初期化
        """
        self.used = 0
        self.enough_size = True

        if self.node_hash is None:
            self.node_hash = [NodeHashEntry() for _ in range(UCT_HASH_SIZE)]
        else:
            for i in range(UCT_HASH_SIZE):
                self.node_hash[i].hash = 0
                self.node_hash[i].color = 0
                self.node_hash[i].moves = 0
                self.node_hash[i].flag = False

    def search_empty_index(self, hash, color, moves):
        """
        未使用のインデックスを探して返す
        """
        key = hash_to_index(hash)
        i = key

        while True:
            if not self.node_hash[i].flag:
                self.node_hash[i].hash = hash
                self.node_hash[i].color = color
                self.node_hash[i].moves = moves
                self.node_hash[i].flag = True
                self.used += 1
                if self.used > UCT_HASH_LIMIT:
                    self.enough_size = False
                return i
            i += 1
            if i >= UCT_HASH_SIZE:
                i = 0
            if i == key:
                return UCT_HASH_SIZE

    def find_same_hash_index(self, hash, color, moves):
        """
        ハッシュ値に対応するインデックスを返す
        """
        key = hash_to_index(hash)
        i = key

        while True:
            if not self.node_hash[i].flag:
                return UCT_HASH_SIZE
            elif self.node_hash[i].hash == hash and self.node_hash[i].color == color and self.node_hash[i].moves == moves:
                return i

            i += 1
            if i >= UCT_HASH_SIZE:
                i = 0
            if i == key:
                return UCT_HASH_SIZE

    def save_used_hash(self, board, uct_node, index):
        """
        使用中のノードを残す
        """
        self.node_hash[index].flag = True
        self.used += 1

        current_node = uct_node[index]
        child_index = current_node.child_index
        child_move = current_node.child_move
        chiled_num = current_node.child_num
        for i in range(chiled_num):
            if child_index[i] != NOT_EXPANDED and self.node_hash[child_index[i]].flag == False:
                board.push(child_move[i])
                self.save_used_hash(board, uct_node, child_index[i])
                board.pop()

    def delete_old_hash(self, board, uct_node):
        """
        現在の局面をルートとする局面以外を削除する
        """
        root = self.find_same_hash_index(board.zobrist_hash(), board.turn, board.move_number)

        self.used = 0
        for i in range(UCT_HASH_SIZE):
            self.node_hash[i].flag = False

        if root != UCT_HASH_SIZE:
            self.save_used_hash(board, uct_node, root)

        self.enough_size = True

    def get_usage_rate(self):
        return self.used / UCT_HASH_SIZE

class UctNode:
    def __init__(self):
        #ノードの訪問回数
        self.move_count = 0
        #勝率の合計
        self.win = 0.0
        #子ノードの数
        self.child_num = 0
        #子ノードの指し手
        self.child_move = None
        #子ノードのインデックス
        self.child_index = None
        #子ノードの訪問回数
        self.child_move_count = None
        #子ノードの勝率の合計
        self.child_win = None
        #方策ネットワークの予測勝率
        self.nnrate = None
        #価値ネットワークの予測勝率
        self.value_win = 0.0
        #評価済みフラグ
        self.evaled = False