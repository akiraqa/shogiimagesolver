#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import numpy as np
import cv2
from PIL import Image
import glob


class BoardImage:
    def __init__(self, image):
        self.image = image
        # imageが将棋盤かどうかはまだわからない
        self.is_board = False
        (self.width, self.height) = self.image.size
        if self.width > self.height:
            # 横長画像には非対応
            return
        # 白黒変換
        self.image_gray = self.image.convert("L")
        self.__findHolizontalLine()
        if not self.is_board:
            # 横線が見つからなければ解析を中止
            return
        self.__findVerticalLine()
        self.__calc_block()

    @staticmethod
    def from_file(file_name):
        im = Image.open(file_name)
        return BoardImage(im)

    def trimmed_image(self):
        """持ち駒と盤の部分を切り抜いた画像(Pillow形式)を返す"""
        if not self.is_board:
            return self.image
        sente_mochigoma_bottom = self.ban_bottom + int(self.block_height * 1.5)
        self.gote_mochigoma_box(0)
        return self.image.crop(
            (
                self.board_left,
                self.gote_mochigoma_top,
                self.board_right,
                sente_mochigoma_bottom,
            )
        )

    def __is_dark_point(self, x, y):
        return BoardImage.is_dark(self.image_gray.getpixel((x, y)))

    def __is_bright_point(self, x, y):
        return BoardImage.is_bright(self.image_gray.getpixel((x, y)))

    def __findUpperHolizontalLine(self):
        mid_h = int(self.height / 2)
        board_top = None  # 盤の縁も含めた上辺
        ban_top = None  # 盤内の線の上辺
        for y in range(mid_h, 0, -1):
            if self.__is_horizontal_line(y):
                # 横線であるなら上辺かも
                ban_top = y
            elif ban_top and self.__is_horizontal_blank(y):
                # 上辺かもしれないものが見つかっていて、
                # 画面横幅の半分以上の範囲で縦線がないなら、盤の縁
                board_top = y
                break
        if not board_top:
            # 盤内の線の上辺が見当たらない
            return (None, None)
        print(ban_top)
        # 上辺から縦方向に上向きに走査して、盤の上端を見つける
        for y in range(board_top, 0, -1):
            if not self.__is_horizontal_blank(y):
                print(y)
                return (y, ban_top)
        # 盤の上端が見当たらない
        return (None, None)

    def __findLowerHolizontalLine(self):
        # 中心から縦方向に上向きに走査して、盤の上端の横線を見つける
        # 盤の下端の横線を見つける
        board_bottom = None
        ban_bottom = None
        for y in range(int(self.height / 2), self.height):
            if self.__is_horizontal_line(y):
                # 横線であるなら下辺かも
                ban_bottom = y
            elif ban_bottom and self.__is_horizontal_blank(y):
                # 下辺かもしれないものが見つかっていて、
                # 画面横幅の半分以上の範囲で縦線がないなら、盤の縁
                board_bottom = y
                break
        if not board_bottom:
            # 盤内の線の下辺が見当たらない
            return (None, None)
        print(ban_bottom)
        # 下辺から縦方向に下向きに走査して、盤の下端を見つける
        for y in range(board_bottom, self.height):
            if not self.__is_horizontal_blank(y):
                print(y)
                return (y, ban_bottom)
        # 盤の上端が見当たらない
        return (None, None)

    def __findHolizontalLine(self):
        (board_top, ban_top) = self.__findUpperHolizontalLine()
        if board_top is None or ban_top is None:
            self.is_board = False
            return
        if board_top >= ban_top:
            self.is_board = False
            return
        (board_bottom, ban_bottom) = self.__findLowerHolizontalLine()
        if board_bottom is None or ban_bottom is None:
            self.is_board = False
            return
        if board_bottom <= ban_bottom:
            self.is_board = False
            return
        self.board_top = board_top
        self.ban_top = ban_top
        self.ban_bottom = ban_bottom
        self.board_bottom = board_bottom
        self.is_board = True

    def __findVerticalLine(self):
        # 盤の左端を見つける
        ban_top = self.ban_top
        ban_left = 0
        for x in range(int(self.width / 4), 0, -1):
            if self.__is_bright_point(x, ban_top):
                ban_left = x + 1
                break
        print(ban_left)
        board_left = 0
        for x in range(ban_left - 1, 0, -1):
            if not self.__is_bright_point(x, ban_top):
                board_left = x + 1
                break
        # 盤の右端を見つける
        ban_right = self.width - 1
        for x in range(int(self.width / 4 * 3), self.width):
            if self.__is_bright_point(x, ban_top):
                ban_right = x - 1
                break
        print(ban_right)
        board_right = ban_right
        for x in range(ban_right + 1, self.width):
            if self.__is_bright_point(x, ban_top):
                board_right = x
            else:
                break
        self.ban_left = ban_left
        self.board_left = board_left
        self.ban_right = ban_right
        self.board_right = board_right

    @staticmethod
    def is_dark(brightness):
        return brightness < 50

    @staticmethod
    def is_bright(brightness):
        return brightness > 100

    def __is_horizontal_line(self, y):
        """横幅の半分以上が黒いこと"""
        for x in range(int(self.width / 4), int(self.width / 4 * 3)):
            if not self.__is_dark_point(x, y):
                return False
        return True

    def __is_horizontal_blank(self, y):
        """横幅の半分以上が盤面色かどうか"""
        for x in range(int(self.width / 4), int(self.width / 4 * 3)):
            if not self.__is_bright_point(x, y):
                return False
        return True

    def __calc_block(self):
        if not self.is_board:
            return
        # 9x9に切り出す
        self.ban_height = self.ban_bottom - self.ban_top
        self.ban_width = self.ban_right - self.ban_left
        if self.ban_height < self.ban_width:
            # 盤は縦長のはず,正方形はありうるが横長ならエラー
            self.is_board = False
            return
        self.block_height = int(self.ban_height / 9)
        self.block_width = int(self.ban_width / 9)
        # 端を切り落とす
        self.edge_y = int(self.block_height * 0.05)
        if self.edge_y < 1:
            self.edge_y = 1
        self.edge_x = int(self.block_width * 0.05)
        if self.edge_x < 1:
            self.edge_x = 1

    def masume_box(self, i, j):
        if not self.is_board:
            return None
        y = self.ban_top + int(self.ban_height / 9 * i)
        x = self.ban_left + int(self.ban_width / 9 * j)
        return (
            x + self.edge_x,
            y + self.edge_y,
            x + self.block_width - self.edge_x,
            y + self.block_height - self.edge_y,
        )

    def masume_box_image(self, i, j):
        """OpenCv形式でグレー画像をひとマス分取得する"""
        if not self.is_board:
            return None
        img = self.image_gray.crop(self.masume_box(i, j))
        return BoardImage.pil2cv(img)

    def gote_mochigoma_box(self, i):
        if not self.is_board:
            return None
        gote_mochigoma_top = (
            self.board_top
            - int((self.ban_top - self.board_top) * 1.2)
            - self.block_height
        )
        self.gote_mochigoma_top = gote_mochigoma_top
        mochigoma_width = int(self.block_width * 0.99)
        edge_x = 0
        edge_y = 0
        y = gote_mochigoma_top
        x = self.ban_left + mochigoma_width * i
        return (
            x + edge_x,
            y + edge_y,
            x + mochigoma_width - edge_x,
            y + self.block_height - edge_y,
        )

    def sente_mochigoma_box(self, i):
        if not self.is_board:
            return None
        edge_x = 0
        edge_y = int((self.ban_top - self.board_top) * 1.2)
        sente_mochigoma_bottom = self.board_bottom + edge_y + self.block_height
        self.sente_mochigoma_bottom = sente_mochigoma_bottom
        mochigoma_width = int(self.block_width * 0.99)
        x = self.ban_left + mochigoma_width * i
        return (
            x + edge_x,
            self.board_bottom + edge_y,
            x + mochigoma_width - edge_x,
            sente_mochigoma_bottom,
        )

    def gote_mochigoma_box_image(self, i):
        """OpenCv形式でグレー画像を後手持ち駒をひとつ取得する"""
        if not self.is_board:
            return None
        img = self.image_gray.crop(self.gote_mochigoma_box(i))
        return BoardImage.pil2cv(img)

    def sente_mochigoma_box_image(self, i):
        """OpenCv形式でグレー画像を先手持ち駒をひとつ取得する"""
        if not self.is_board:
            return None
        img = self.image_gray.crop(self.sente_mochigoma_box(i))
        return BoardImage.pil2cv(img)

    def mochigoma_box_image(self, i, is_for_sente):
        """OpenCv形式でグレー画像を持ち駒をひとつ取得する"""
        if not self.is_board:
            return None
        if is_for_sente:
            img = self.image_gray.crop(self.sente_mochigoma_box(i))
        else:
            img = self.image_gray.crop(self.gote_mochigoma_box(i))
        return BoardImage.pil2cv(img)

    @staticmethod
    def pil2cv(image):
        """PIL型 -> OpenCV型"""
        new_image = np.array(image, dtype=np.uint8)
        if new_image.ndim == 2:  # モノクロ
            pass
        elif new_image.shape[2] == 3:  # カラー
            new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
        elif new_image.shape[2] == 4:  # 透過
            new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)
        return new_image


if __name__ == "__main__":
    files = glob.glob("./**/testin/full*.jpg")
    for fname in files:
        board_image = BoardImage.from_file(fname)
        for i in range(9):
            for j in range(9):
                img = board_image.masume_box_image(i, j)
                cv2.imwrite("testout/_koma" + str(i) + str(j) + ".png", img)
        for i in range(7):
            img = board_image.gote_mochigoma_box_image(i)
            cv2.imwrite("testout/_gote" + str(i) + ".png", img)
        trimmedimg = board_image.trimmed_image()
        trimmedimg.save("testout/trimmed_full.jpg")
