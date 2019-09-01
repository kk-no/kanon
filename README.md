# kanon
Python Deep Learning Shogi

## 実装環境
- Windows10 Home 64bit
- Visual Studio 2017 (C++ BuildTool)
- Python 3.6.9 (Miniconda3 64bit)
- Chainer 5.3.0
- Cuda 9.1
- Cupy 6.2.0 (cupy-cuda91 6.0.0)

## 環境構築
- Python3 インストール (64bit版)
- CUDAをインストール(9.0または9.1以外の場合は別途cuDNNが必要)
- pipを利用してChainer、Cupyをインストール
```
# Chainerをインストール
$ pip install chainer

# Cupyをインストール(wheel形式/CUDA9.0または9.1の場合のみ)
$ pip install cupy-cuda91(90)

# GPU接続確認(正常に接続できていればCUDA/Cupyの詳細が出力)
$ python -c "import chainer; chainer.print_runtime_info()"
```
- 実行モジュール化
```
$ pip install --no-cache-dir -e .
```
- 実行コマンド
```
# CPU版実行
python -m kanon_shogi.usi.mcts_cpu_player

# GPU版実行
python -m kanon_shogi.usi.mcts_gpu_player

# 初期化コマンド
$ isready

# 盤面初期化
$ position startpos

# 思考開始
$ go
```

## やる事
- 倶楽部24の棋譜を読み込めるようにする(対局情報・棋譜)
- 倶楽部24の棋譜をディレクトリ上でレーティング絞り込み(Done)
- 自己対局機能追加
- ライブラリのアップデート(cython)
- KIF形式での対局棋譜出力
- 強化学習