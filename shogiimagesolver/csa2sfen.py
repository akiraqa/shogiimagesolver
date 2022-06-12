#!/usr/bin/env python
# -*- coding: UTF-8 -*-


class Csa2Sfen:
    SFEN_KOMA = ["", "P", "L", "N", "S", "G", "B", "R", "K"]
    KOMA_NAMES = [" * ", "FU", "KY", "KE", "GI", "KI", "KA", "HI", "OU"]
    NARI_KOMA_NAMES = ["", "TO", "NY", "NK", "NG", "", "UM", "RY"]
    KOMA_QTY = [0, 18, 4, 4, 4, 4, 2, 2, 2]
    TEBAN = ["b", "w"]

    def __init__(self):
        self.__mochigoma = [[0] * 9, [0] * 9]
        self.__koma_counter = [0] * 10
        self.__dan_sfen = [""] * 10
        self.teban = 0  # default sente

    @staticmethod
    def from_csa(csa):
        csa2sfen = Csa2Sfen()
        for line in csa.split("\n"):
            csa2sfen.line2sfen(line)
        return csa2sfen

    def line2sfen(self, line):
        if line == "+":
            self.teban = 0
            return ""
        if line == "-":
            self.teban = 1
            return ""
        # 最後の手番の行以外は、P始まりの行以外はSKIPする
        if not line.startswith("P"):
            return ""
        if line.startswith("P-00") or line.startswith("P+00"):
            self.addMochiGoma(line)
            return ""
        # P始まりで持ち駒行でなければ盤面行として処理
        start_pos = 2
        dan = int(line[1:2])
        if dan < 1 or dan > 9:
            return ""
        sfen = ""
        blank_continue_num = 0
        for i in range(0, 9):
            csakoma = line[start_pos + i * 3 : start_pos + i * 3 + 3]
            if csakoma == " * ":
                blank_continue_num += 1
            else:
                if blank_continue_num != 0:
                    sfen = sfen + str(blank_continue_num)
                    blank_continue_num = 0
                sfen = sfen + self.csakoma2sfen(csakoma)
        if blank_continue_num != 0:
            sfen = sfen + str(blank_continue_num)
        self.__dan_sfen[dan] = sfen
        return sfen

    def csakoma2sfen(self, csakoma):
        csa_koma_only = csakoma[1:3]
        if csa_koma_only in self.NARI_KOMA_NAMES:
            sfen = "+"
            idx = self.NARI_KOMA_NAMES.index(csa_koma_only)
        else:
            sfen = ""
            idx = self.KOMA_NAMES.index(csa_koma_only)
        self.__koma_counter[idx] = self.__koma_counter[idx] + 1
        sfen = sfen + self.SFEN_KOMA[idx]
        if csakoma[0:1] == "-":
            sfen = sfen.lower()
        return sfen

    def addMochiGoma(self, line):
        if line[1:2] == "+":
            sengo = 0
        else:
            sengo = 1
        if line[4:] == "ALL":
            self.calcMochiGoma(sengo)
            return
        for csakoma in line[2:].split("00"):
            if csakoma == "":
                continue
            idx = self.KOMA_NAMES.index(csakoma)
            if idx < 1 or idx > 9:
                continue
            self.__mochigoma[sengo][idx] = self.__mochigoma[sengo][idx] + 1
            self.__koma_counter[idx] = self.__koma_counter[idx] + 1

    def calcMochiGoma(self, sengo):
        for i in range(1, 9):
            diff = self.KOMA_QTY[i] - self.__koma_counter[i]
            if diff > 0:
                self.__mochigoma[sengo][i] = diff

    def sfenMochiGoma(self):
        sfen = ""
        for i in range(0, 2):
            for j in range(1, 9):
                if self.__mochigoma[i][j] > 1:
                    sfen = sfen + str(self.__mochigoma[i][j])
                if self.__mochigoma[i][j] >= 1:
                    if i == 0:
                        sfen = sfen + self.SFEN_KOMA[j]
                    else:
                        sfen = sfen + self.SFEN_KOMA[j].lower()
        if sfen == "":
            sfen = "-"
        return sfen

    def sfen(self):
        if not self.is_complete():
            return None
        sfen = ""
        for i in range(1, 10):
            if sfen != "":
                sfen = sfen + "/"
            sfen = sfen + self.__dan_sfen[i]
        sfen = sfen + " " + self.TEBAN[self.teban] + " " + self.sfenMochiGoma() + " 1"
        return sfen

    def is_complete(self):
        for i in range(1, 10):
            if self.__dan_sfen[i] == "":
                return False
        # 駒の数はチェックしないでおく
        return True


# メイン
if __name__ == "__main__":
    csa2Sfen = Csa2Sfen()
    sfen1 = csa2Sfen.line2sfen("P1-KY *  *  * -OU *  *  * -KY")
    sfen2 = csa2Sfen.line2sfen("P2 *  *  *  *  *  * +KI *  * ")
    sfen3 = csa2Sfen.line2sfen("P3 *  * +NK+GI-GI-FU-FU+KI-FU")
    sfen4 = csa2Sfen.line2sfen("P4-FU-FU *  * -FU *  *  *  * ")
    sfen5 = csa2Sfen.line2sfen("P5 *  *  *  *  * -RY *  *  * ")
    sfen6 = csa2Sfen.line2sfen("P6 *  *  *  *  * -GI *  *  * ")
    sfen7 = csa2Sfen.line2sfen("P7 * +FU *  *  *  *  *  * +FU")
    sfen8 = csa2Sfen.line2sfen("P8 *  * +FU * +GI * +KI+FU * ")
    sfen9 = csa2Sfen.line2sfen("P9+KY * +KI * +OU *  * +KE+KY")
    csa2Sfen.addMochiGoma("P-00FU")
    csa2Sfen.addMochiGoma("P-00FU00FU00FU00FU00FU00FU")
    csa2Sfen.addMochiGoma("P-00KE")
    csa2Sfen.addMochiGoma("P-00KA")
    csa2Sfen.addMochiGoma("P-00KA")
    csa2Sfen.addMochiGoma("P-00HI")
    csa2Sfen.addMochiGoma("P+00ALL")
    sfenMochiGoma = csa2Sfen.sfenMochiGoma()
    print(csa2Sfen.sfen())

    csa2 = """P1-KY-OU * -KA *  *  * -KE-KY
P2 *  *  * -GI *  *  * -UM * 
P3 * +KI * -KI *  *  *  *  * 
P4-FU+KE-FU-GI-FU *  *  * -FU
P5 * -RY * +KE *  *  *  *  * 
P6+FU *  *  * +GI *  *  * +FU
P7 *  * -KI * +FU * +KE+GI * 
P8 *  *  *  * +HI * +KI+OU * 
P9+KY *  *  *  *  *  *  * +KY
P-00FU00FU00FU00FU00FU00FU00FU
P+00FU00FU00FU00FU
+"""
    csa2Sfen = Csa2Sfen.from_csa(csa2)
    print(csa2Sfen.sfen())
    # 正しくは
    # lk1b3nl/3s3+b1/1G1g5/pNpsp3p/1+r1N5/P3S3P/2g1P1NS1/4R1GK1/L7L b 4P7p 1
    # python-shogiでshogi.CSA.Parser.parse_str(csa2)すると以下のようになる
    # lk1b3nl/3s3+b1/1G1g5/pNpsp3p/1+r1N5/P3S3P/2g1P1NS1/4R1GK1/L7L b 47 1
