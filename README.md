# shogi image solver

将棋アプリのスクリーンショット画像を元に次の一手/詰み手順を出力します。

現状、将棋クエストの詰めチャレ・一字駒（裏赤）に対応しています。

OpenCVのテンプレートマッチング+ORB特徴量検出を用いて、サンプル画像との類似度を元に駒を決定しています。

## 実行準備

画像処理にPillow,画像解析にOpenCVを、sfen形式のmoveを棋譜に変換するためにpython-shogi[python-shogi](https://github.com/gunyarakun/python-shogi)を利用します。

```
pip install pillow cv2 numpy python-shogi
```
（以前CSA局面→sfen棋譜変換機能についても[python-shogi](https://github.com/gunyarakun/python-shogi)を利用していましたが、持ち駒が正しくないケースがあったのでそこは自前で行うようにしました。）

詰将棋エンジンを同梱していませんので別途用意してください。

テスト時には以下のように、[やねうら王](https://github.com/yaneurao/YaneuraOu)詰将棋エンジンをカレントディレクトリに準備しています。

```
git clone https://github.com/yaneurao/YaneuraOu.git
cd YaneuraOu/source
make clean normal TARGET_CPU=AVX2 YANEURAOU_EDITION=YANEURAOU_MATE_ENGINE
mv YaneuraOu-by-gcc ../../YaneuraOu-mate
```

### サンプル画像

サンプル画像を元に判定するため、画像ファイルが必要です。

- bankomaディレクトリ
  - 00.png 盤の1マス（駒なし）
  - 01.png 歩
  - 01r.png 歩(後手)
  - 08.png 玉
  - 08r.png 玉(後手)
  - 11.png と
  - 11r.png と(後手)
  - 17.png 龍
  - 17r.png 龍(後手)
02〜07,12〜14,16も同様に必要です。

- mochigoma_senteディレクトリ
  - num2.png〜numXX.png 持ち駒右下の数字部分
  - FU0.png, FU1.png, FU2.png 歩(0/1/2枚)
  - KY0.png, KY1.png, KY2.png 香(0/1/2枚)
  - KE0.png, KE1.png, KE2.png 桂(0/1/2枚)
  - GI0.png, GI1.png, GI2.png 銀(0/1/2枚)
  - KI0.png, KI1.png, KI2.png 金(0/1/2枚)
  - KA0.png, KA1.png, KA2.png 角(0/1/2枚)
  - HI0.png, HI1.png, HI2.png 飛(0/1/2枚)

## 実行方法

testinディレクトリに将棋クエスト詰めチャレのスクリーンショット画像を.jpgファイルとして置いてから以下を実行してください。
```
python imageSolver.py
```
成功すればtestoutディレクトリに`result_*.png`形式で盤だけ切り抜いた画像と`result_*.txt`形式で詰め手順のファイルが出来ます。

ライブラリとして使う場合
```pip install git+https://github.com/akiraqa/shogiimagesolver```
でインストールして以下のように使用します。
```
from shogiimagesolver import ImageSolver
imageSolver = ImageSolver(options=[("USI_HASH", 128)])
(result, sfen, csa, img) = imageSolver.solve_from_file(filename)
```

webアプリ化したものが[shogi image solver web版](https://github.com/akiraqa/shogiimgsolverweb)にあります。

## usiEngine.py

USIプロトコルで将棋エンジンに接続してコマンド発行して応答を受け取るモジュールです。

一定時間応答がなければタイムアウトして制御を戻す機能を備えています。

