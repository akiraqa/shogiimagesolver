#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import glob
import os

if __name__ == "__main__" or __package__ == "":
    from boardimage import BoardImage
    from csaconverter import CsaConverter
    from usiengine import UsiEngine
    from sfen2kif import Sfen2kif
    from csa2sfen import Csa2Sfen
else:
    from .boardimage import BoardImage
    from .csaconverter import CsaConverter
    from .usiengine import UsiEngine
    from .sfen2kif import Sfen2kif
    from .csa2sfen import Csa2Sfen


class ImageSolver:
    """将棋アプリ画像を解析して次の一手/詰め手順を求める"""

    DEFAULT_ENGINE = "./YaneuraOu-mate"
    MATE_WAIT = 5

    def __init__(self, engine=None, options=[]):
        self.converter = CsaConverter()
        env_engine = os.environ.get("SHOGI_ENGINE")
        # 引数→環境変数→デフォルトの順
        if engine:
            self.engine = engine
        elif env_engine:
            self.engine = env_engine
        else:
            self.engine = self.DEFAULT_ENGINE
        self.usi = UsiEngine(
            os.path.abspath(os.path.expanduser(self.engine)), debug=True
        )
        for (option_name, option_value) in options:
            self.usi.setoption(option_name, option_value)

    def __del__(self):
        self.quit()

    def quit(self):
        """USIプロトコル対応将棋エンジンを終了させる"""
        if self.usi:
            self.usi.quit()
            self.usi = None

    def image_to_sfen(self, board_image):
        """将棋アプリ画像をsfen形式に変換"""
        csa = self.converter.from_board_image(board_image)
        print(csa)
        csa2Sfen = Csa2Sfen.from_csa(csa)
        sfen = csa2Sfen.sfen()
        # parser = shogi.CSA.Parser.parse_str(csa)
        # sfen = parser[0]["sfen"]
        if sfen is None:
            print("解析NG")
            return (None, None)
        print(sfen)
        return (sfen, csa)

    def mate_by_usi(self, sfen):
        """USIプロトコル対応詰将棋エンジンで詰め手順を計算"""
        usi = self.usi
        usi.isready()
        usi.position(sfen="sfen " + sfen)
        mate_lines = usi.go_mate(self.MATE_WAIT * 1000)
        return mate_lines

    def solve_from_board_image(self, board_image):
        """将棋盤イメージを元に解析"""
        (sfen, csa) = self.image_to_sfen(board_image)
        if sfen is None:
            return ("parse_NG", None, None)
        mate_lines = self.mate_by_usi(sfen)
        if not mate_lines[-1].startswith("checkmate"):
            return ("solve_NG", sfen, csa)
        mate_line = mate_lines[-1][10:]
        if "nomate" in mate_line:
            print("不詰")
            return ("nomate", sfen, csa)
        kif = Sfen2kif.parse_moves(sfen, mate_line)
        print(kif)
        return (kif, sfen, csa)

    def solve_from_file(self, file_name):
        """将棋盤イメージファイルを元に解析"""
        board_image = BoardImage.from_file(file_name)
        if board_image is None or not board_image.is_board:
            return ("image_NG", None, None, None)
        (result, sfen, csa) = self.solve_from_board_image(board_image)
        img = board_image.trimmed_image()
        return (result, sfen, csa, img)


if __name__ == "__main__":
    imageSolver = ImageSolver(options=[("USI_HASH", 128)])
    files = glob.glob("./**/testin/*.jpg")
    total = 0
    nomate_num = 0
    for file_name in files:
        (result, sfen, csa, img) = imageSolver.solve_from_file(file_name)
        if result is None or sfen is None or img is None:
            continue
        basename_without_ext = os.path.splitext(os.path.basename(file_name))[0]
        result_file_name = "./testout/result_" + basename_without_ext
        img.save(result_file_name + ".png")
        total = total + 1
        if result == "nomate":
            nomate_num = nomate_num + 1
        summary = (
            "image="
            + file_name
            + ", result="
            + result
            + "\nsfen="
            + sfen
            + "\ncsa:\n"
            + csa
        )
        print(summary)
        with open(result_file_name + ".txt", "w", encoding="utf-8") as f:
            f.write(summary)
    imageSolver.quit()
    print("nomate/total = " + str(nomate_num) + "/" + str(total))
    exit(0)
