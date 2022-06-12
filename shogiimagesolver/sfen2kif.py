#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import shogi

SUJI_NAMES = [
    "",
    "１",
    "２",
    "３",
    "４",
    "５",
    "６",
    "７",
    "８",
    "９",
]

DAN_NAMES = [
    "一",
    "二",
    "三",
    "四",
    "五",
    "六",
    "七",
    "八",
    "九",
]
DAN1 = 97  # ord("a")

TEBAN = ["▲", "△"]


class Sfen2kif:
    @staticmethod
    def str2pos(suji, dan):
        dan_num = ord(dan) - DAN1
        return SUJI_NAMES[int(suji)] + DAN_NAMES[dan_num]

    @staticmethod
    def parse_moves(sfen, sfen_moves):
        board = shogi.Board(sfen)
        moves = sfen_moves.split()
        teban = 0 if " b " in sfen else 1
        pre_pos = None
        kif = ""
        for move in moves:
            from1 = move[0:1]
            from2 = move[1:2]
            to_pos = move[2:4]
            to1 = move[2:3]
            to2 = move[3:4]
            to3 = move[4:5]
            if pre_pos == to_pos:
                pos_str = "同"
            else:
                pos_str = Sfen2kif.str2pos(to1, to2)
            if from2 == "*":
                koma = shogi.Piece.from_symbol(from1)
            else:
                dan_num = ord(from2) - DAN1
                koma = board.piece_at((9 - int(from1)) + 9 * (dan_num))
            koma_str = koma.japanese_symbol()
            if to3 == "+":
                koma_str = koma_str + "成"
            if from2 == "*":
                kif = kif + TEBAN[teban] + pos_str + koma_str + "打 "
            else:
                kif = (
                    kif
                    + TEBAN[teban]
                    + pos_str
                    + koma_str
                    + "("
                    + Sfen2kif.str2pos(from1, from2)
                    + ") "
                )
            pre_pos = to_pos
            board.push(shogi.Move.from_usi(move))
            teban = 1 if teban == 0 else 0
        return kif


if __name__ == "__main__":
    sfen = "l3k3l/6G2/2+NSsppGp/pp2p4/5+r3/5s3/1P6P/2P1S1GP1/L1G1K2NL b NPr2bn7p 1"
    kif = Sfen2kif.parse_moves(sfen, "P*5b 5a6a 7c7b")
    print(kif)
