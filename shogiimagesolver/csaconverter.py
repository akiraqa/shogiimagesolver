#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import glob

if __name__ == "__main__" or __package__ == "":
    from boardimage import BoardImage
    from komadetector import KomaDetector
    from mochigomadetector import MochigomaDetector
else:
    from .boardimage import BoardImage
    from .komadetector import KomaDetector
    from .mochigomadetector import MochigomaDetector


class CsaConverter:
    KOMA_QTY = [99, 18, 4, 4, 4, 4, 2, 2, 2]

    def __init__(self, mochigoma_by_sente=True):
        self.komaDetector = KomaDetector()
        self.mochigoma_by_sente = mochigoma_by_sente
        if mochigoma_by_sente:
            self.mochiGomaDetector = MochigomaDetector(sample_dir="mochigoma_sente")
        else:
            self.mochiGomaDetector = MochigomaDetector(sample_dir="mochigoma")

    def from_file(self, file_name):
        """画像ファイルを読み込む"""
        board_image = BoardImage.from_file(file_name)
        return self.from_board_image(board_image)

    def from_board_image(self, board_image):
        """画像を解析する"""
        if board_image is None or not board_image.is_board:
            return None
        self.csalines = []
        self.koma_count = [0] * 9
        self.board_image = board_image
        self.__detect_koma()
        self.__detect_mochigoma()
        return self.__csa()

    def __detect_mochigoma(self):
        self.__detect_half_mochigoma(self.mochigoma_by_sente)
        self.__calc_rest_mochigoma(not self.mochigoma_by_sente)

    def __csa(self):
        """CSA形式の局面棋譜を返す"""
        return "\n".join(self.csalines) + "\n+"

    @staticmethod
    def koma_index(koma):
        """CSA棋譜中の駒の種類を数字に変換する"""
        if koma is None or koma == "" or koma == KomaDetector.KOMA_NAMES[0]:
            return 0
        koma = koma[-2:]
        if koma in KomaDetector.KOMA_NAMES:
            return KomaDetector.KOMA_NAMES.index(koma)
        if koma in KomaDetector.NARI_KOMA_NAMES:
            return KomaDetector.NARI_KOMA_NAMES.index(koma)

    def __add_koma(self, koma, qty=1):
        """駒の種類ごとの枚数を追加する"""
        idx = CsaConverter.koma_index(koma)
        self.koma_count[idx] = self.koma_count[idx] + qty

    def __detect_koma(self):
        """盤上の駒を検出する"""
        for i in range(9):
            csa = "P" + str(i + 1)
            for j in range(9):
                img = self.board_image.masume_box_image(i, j)
                koma = self.komaDetector.find_koma(img)
                csa = csa + koma
                self.__add_koma(koma)
            print(csa)
            self.csalines.append(csa)

    def __detect_half_mochigoma(self, is_for_sente):
        """先手/後手どちらかの持駒を検出する"""
        for i in range(7):
            img = self.board_image.mochigoma_box_image(i, True)
            (koma, qty) = self.mochiGomaDetector.find_koma_by_template(i, img)
            if qty > 0:
                csa = "P" + CsaConverter.teban_mark(is_for_sente) + ("00" + koma) * qty
                self.__add_koma(koma, qty)
                print(csa)
                self.csalines.append(csa)

    def __calc_rest_mochigoma(self, is_for_sente):
        """残りの駒数を計算する"""
        for i in range(1, 8):
            qty = self.KOMA_QTY[i] - self.koma_count[i]
            if qty > 0:
                csa = (
                    "P"
                    + CsaConverter.teban_mark(is_for_sente)
                    + ("00" + KomaDetector.KOMA_NAMES[i]) * qty
                )
                self.__add_koma(KomaDetector.KOMA_NAMES[i], qty)
                print(csa)
                self.csalines.append(csa)

    @staticmethod
    def teban_mark(is_for_sente):
        return "+" if is_for_sente else "-"


if __name__ == "__main__":
    converter = CsaConverter()
    files = glob.glob("./**/testin/trimmed0.jpg")
    for fname in files:
        csa = converter.from_file(fname)
        print(csa)
    files = glob.glob("./**/testin/full.jpg")
    for fname in files:
        csa = converter.from_file(fname)
        print(csa)
