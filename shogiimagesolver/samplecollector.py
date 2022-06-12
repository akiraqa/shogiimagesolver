#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import glob
import os
import cv2
from boardimage import BoardImage
from komadetector import KomaDetector
from mochigomadetector import MochigomaDetector


"""指定場所の画像をマス・駒ごとに分割・分類して出力するツール"""
if __name__ == "__main__":
    files = glob.glob("./**/testin/*.jpg")
    for file_name in files:
        print("start:" + file_name)
        board_image = BoardImage.from_file(file_name)
        basename = os.path.splitext(os.path.basename(file_name))[0]
        komaDetector = KomaDetector()
        for i in range(9):
            for j in range(9):
                img = board_image.masume_box_image(i, j)
                if img is None:
                    continue
                koma = komaDetector.find_koma(img)
                if koma == " * ":
                    koma = "ban"
                dirname = "./testout/bankoma" + koma.replace("+", "P")
                os.makedirs(dirname, exist_ok=True)
                cv2.imwrite(dirname + "/" + basename + str(i) + str(j) + ".png", img)
        mochiGomaDetector = MochigomaDetector(sample_dir="mochigoma")
        for i in range(7):
            img = board_image.gote_mochigoma_box_image(i)
            if img is None:
                continue
            (koma, qty) = mochiGomaDetector.find_koma_by_template(i, img)
            dirname = "./testout/mochigoma" + str(i) + "/" + str(qty)
            os.makedirs(dirname, exist_ok=True)
            cv2.imwrite(dirname + "/" + basename + "gm" + str(i) + ".png", img)
        mochiGomaDetector = MochigomaDetector(sample_dir="mochigoma_sente")
        for i in range(7):
            img = board_image.sente_mochigoma_box_image(i)
            if img is None:
                continue
            (koma, qty) = mochiGomaDetector.find_koma_by_template(i, img)
            dirname = "./testout/mochigoma_sente" + str(i) + "/" + str(qty)
            os.makedirs(dirname, exist_ok=True)
            cv2.imwrite(dirname + "/" + basename + "sm" + str(i) + ".png", img)
        print("end:" + file_name)
