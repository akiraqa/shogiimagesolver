#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import cv2


class KomaDetector:
    IMG_SIZE = (100, 100)
    TEACHER_IMG_DIR = "bankoma"
    KOMA_NAMES = [" * ", "FU", "KY", "KE", "GI", "KI", "KA", "HI", "OU"]
    NARI_KOMA_NAMES = ["", "TO", "NY", "NK", "NG", "", "UM", "RY"]

    def __init__(self, sample_dir=TEACHER_IMG_DIR):
        self.sample_dir = sample_dir
        # self.__detector = cv2.AKAZE_create()
        self.__detector = cv2.ORB_create()
        self.__bf = cv2.BFMatcher(cv2.NORM_HAMMING)
        self.__teacher_list = self.__prepare_teacher()

    def __prepare_teacher(self):
        """比較用のサンプル画像を読み込んで解析しておく"""
        teacher_list = []
        for i in range(0, 9):
            (tmp_des, resized_img) = self.read_detect(self.sample_dir + "/%02d.png" % i)
            teacher_list.append(("+" + self.KOMA_NAMES[i], tmp_des, resized_img))
        for i in [1, 2, 3, 4, 6, 7]:
            (tmp_des, resized_img) = self.read_detect(self.sample_dir + "/1%d.png" % i)
            teacher_list.append(("+" + self.NARI_KOMA_NAMES[i], tmp_des, resized_img))
        for i in range(1, 9):
            (tmp_des, resized_img) = self.read_detect(
                self.sample_dir + "/%02dr.png" % i
            )
            teacher_list.append(("-" + self.KOMA_NAMES[i], tmp_des, resized_img))
        for i in [1, 2, 3, 4, 6, 7]:
            (tmp_des, resized_img) = self.read_detect(self.sample_dir + "/1%dr.png" % i)
            teacher_list.append(("-" + self.NARI_KOMA_NAMES[i], tmp_des, resized_img))
        return teacher_list

    def read_detect(self, fname):
        """駒画像をグレースケールで読み込んで同一サイズに揃えて解析"""
        img = cv2.imread(fname, cv2.IMREAD_GRAYSCALE)
        return self.resize_detect(img)

    def resize_detect(self, img):
        """CV2画像をリサイズして解析"""
        if img is None:
            return (None, None)
        img = cv2.resize(img, self.IMG_SIZE)
        (target_kp, target_des) = self.__detector.detectAndCompute(img, None)
        return (target_des, img)

    def find_koma(self, cv2greyimg):
        """OpenCVグレースケール画像を元に、どの駒か判定する"""
        if cv2greyimg is None:
            self.KOMA_NAMES[0]
        (target_des, resized_img) = self.resize_detect(cv2greyimg)
        if target_des is None:
            # print("RESULT: koma=NN")
            return self.KOMA_NAMES[0]
        min = 9999
        koma_index = 0
        for i in range(len(self.__teacher_list)):
            (name, des, _) = self.__teacher_list[i]
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
                koma = name
                koma_index = i
            # print("koma="+name+", ret="+str(ret))
        # 最も似ている画像を見つける
        # print("RESULT: koma="+koma+", ret="+str(min))
        koma = self.check_koma_direction(resized_img, koma_index)
        return koma

    def check_koma_direction(self, resized_img, koma_index):
        """テンプレートマッチングで、駒の向きの類似度を比較"""
        if koma_index == 0:
            return self.KOMA_NAMES[0]
        # 逆方向の駒のkoma_indexを求める
        if koma_index <= 14:
            reverse_index = koma_index + 14
        else:
            reverse_index = koma_index - 14
        (name, _, img) = self.__teacher_list[koma_index]
        (reverse_name, _, reverse_img) = self.__teacher_list[reverse_index]
        res = cv2.matchTemplate(img, resized_img, cv2.TM_CCOEFF_NORMED)
        res_reverse = cv2.matchTemplate(reverse_img, resized_img, cv2.TM_CCOEFF_NORMED)
        if res >= res_reverse:
            return name
        else:
            return reverse_name


# メイン
if __name__ == "__main__":
    # サンプル画像との類似度を求める
    fname = "testin/koma62.png"
    fname = os.path.join(os.path.abspath(os.path.dirname(__file__)), fname)
    img = cv2.imread(fname, cv2.IMREAD_GRAYSCALE)
    komaDetector = KomaDetector()
    koma = komaDetector.find_koma(img)
    print(koma)
    # +GI
