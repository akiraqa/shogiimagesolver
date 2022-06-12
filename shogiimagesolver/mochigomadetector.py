#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import cv2
import os
import glob


class MochigomaDetector:
    IMG_SIZE = (115, 120)
    TEACHER_IMG_DIR = "mochigoma_sente"
    KOMA_NAMES = ["FU", "KY", "KE", "GI", "KI", "KA", "HI"]
    KOMA_QTY = [18, 4, 4, 4, 4, 2, 2]

    def __init__(self, sample_dir=TEACHER_IMG_DIR):
        self.sample_dir = sample_dir
        # self.__detector = cv2.AKAZE_create()
        self.__detector = cv2.ORB_create()
        self.__bf = cv2.BFMatcher(cv2.NORM_HAMMING)
        self.__teacher_list = self.__prepare_teacher()
        self.__num_image_list = self.__prepare_num_images()

    def __prepare_num_images(self):
        num_image_list = []
        for i in range(17):
            fname = self.sample_dir + "/num" + str(i + 2) + ".png"
            if not os.path.isfile(fname):
                break
            img = cv2.imread(fname, cv2.IMREAD_GRAYSCALE)
            num_image_list.append(img)
        return num_image_list

    def __prepare_teacher(self):
        """比較用のサンプル画像を読み込んで解析しておく"""
        teacher_list = []
        for i in range(0, 7):
            one_koma_list = []
            for j in range(3):
                # サンプル画像はハイフンあり/なしを試す
                (exists_sample, tmp_des, resized_img) = self.read_detect(
                    self.sample_dir + "/" + self.KOMA_NAMES[i] + str(j) + ".png"
                )
                if not exists_sample:
                    (exists_sample, tmp_des, resized_img) = self.read_detect(
                        self.sample_dir
                        + "/"
                        + self.KOMA_NAMES[i]
                        + "-"
                        + str(j)
                        + ".png"
                    )
                if exists_sample:
                    one_koma_list.append((j, tmp_des, resized_img))
            teacher_list.append(one_koma_list)
        return teacher_list

    def read_detect(self, fname):
        """駒画像を読み込んで同一サイズに揃えて特徴量解析"""
        if not os.path.isfile(fname):
            return (False, None, None)
        img = cv2.imread(fname, cv2.IMREAD_GRAYSCALE)
        (target_des, resized_img) = self.resize_detect(img)
        return (True, target_des, resized_img)

    def resize_detect(self, img):
        """CV2画像をリサイズして特徴量解析"""
        img = cv2.resize(img, self.IMG_SIZE)
        (target_kp, target_des) = self.__detector.detectAndCompute(img, None)
        return (target_des, img)

    def __find_koma_type_by_templete(self, mochigoma_idx, cv2greyimg):
        # 画像をリサイズ
        (target_des, resized_img) = self.resize_detect(cv2greyimg)
        if target_des is None:
            return (0, resized_img)
        qty = 0
        max_res = 0.0
        # 画像全体のテンプレートマッチングで最も似ている画像を見つける
        for (num, des, img) in self.__teacher_list[mochigoma_idx]:
            try:
                res = cv2.matchTemplate(img, resized_img, cv2.TM_CCOEFF_NORMED)
                if res > max_res:
                    max_res = res
                    qty = num
            except cv2.error:
                continue
        return (qty, resized_img)

    def __find_koma_qty_by_template(self, resized_img):
        qty = 1
        max_res = 0.5
        num_idx = 1
        for num_image in self.__num_image_list:
            try:
                num_idx += 1
                res = cv2.matchTemplate(num_image, resized_img, cv2.TM_CCOEFF_NORMED)
                if res.max() > max_res:
                    max_res = res.max()
                    qty = num_idx
            except cv2.error:
                continue
        return qty

    def find_koma(self, mochigoma_idx, cv2greyimg):
        """OpenCVグレースケール画像を元に、どの駒か判定する"""
        return self.find_koma_by_template(mochigoma_idx, cv2greyimg)

    def find_koma_by_template(self, mochigoma_idx, cv2greyimg):
        """OpenCVグレースケール画像を元に、テンプレートマッチングでどの駒か判定する"""
        (qty, resized_img) = self.__find_koma_type_by_templete(
            mochigoma_idx, cv2greyimg
        )
        # 最も似ている画像が枚数0なら終わり
        # 飛車角は画像全体のテンプレートマッチング結果を採用
        if qty == 0 or mochigoma_idx == 5 or mochigoma_idx == 6:
            return (self.KOMA_NAMES[mochigoma_idx], qty)
        # 飛車角以外で、駒があるなら枚数は数字部分のテンプレートマッチングで判定してみる
        qty = self.__find_koma_qty_by_template(resized_img)
        # 多すぎるなら1にしておく
        if qty > self.KOMA_QTY[mochigoma_idx]:
            qty = 1
        return (self.KOMA_NAMES[mochigoma_idx], qty)

    def find_koma_by_bfmatcher(self, mochigoma_idx, cv2greyimg):
        """OpenCVグレースケール画像を元に、特徴量解析でどの駒か判定する"""
        (target_des, resized_img) = self.resize_detect(cv2greyimg)
        if target_des is None:
            print("RESULT: no mochigoma:" + self.KOMA_NAMES[mochigoma_idx])
            return (self.KOMA_NAMES[mochigoma_idx], 0)
        min = 9999
        qty = 0
        for (num, des, img) in self.__teacher_list[mochigoma_idx]:
            try:
                if des is None:
                    ret = 9999
                else:
                    matches = self.__bf.match(target_des, des)
                    dist = [m.distance for m in matches]
                    ret = sum(dist) / len(dist)
            except cv2.error:
                ret = 9999
            if ret < min:
                min = ret
                qty = num
            print("num=" + str(num) + ", ret=" + str(ret))
        # 最も似ている画像を見つける
        print("RESULT: qty=" + str(qty) + ", ret=" + str(min))
        return (self.KOMA_NAMES[mochigoma_idx], qty)


# メイン
if __name__ == "__main__":
    # サンプル画像との類似度を求める
    mochigomaDetector = MochigomaDetector()
    files = glob.glob("./**/testin/sente_*.png")
    for fname in files:
        basename_without_ext = os.path.splitext(os.path.basename(fname))[0]
        koma_type_num = basename_without_ext[-3:]
        koma_type = koma_type_num[0:2].upper()
        koma_qty = int(koma_type_num[-1:])
        if koma_type not in koma_type:
            continue
        koma_idx = mochigomaDetector.KOMA_NAMES.index(koma_type)
        fname = os.path.abspath(fname)
        img = cv2.imread(fname, cv2.IMREAD_GRAYSCALE)
        (koma, qty) = mochigomaDetector.find_koma_by_template(koma_idx, img)
        if qty == koma_qty:
            print("bingo!!:" + fname)
        else:
            print("orz..:" + fname)
