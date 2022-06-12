#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import asyncio
import sys
from asyncio.subprocess import PIPE
import locale
import os.path


class UsiEngine:
    """timeout秒以上無応答が続くと、打ち切って結果を返すUSIプロトコル将棋エンジンクライアント"""

    def __init__(self, engine_cmd, timeout=3, debug=False, listener=None):
        self.engine_cmd = engine_cmd
        self.debug = debug
        self.listener = listener
        if debug and not listener:
            self.listener = print
        self.timeout = timeout
        if sys.platform == "win32":
            self.loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(self.loop)
        else:
            self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.run_engine())

    async def run_engine(self):
        self.proc = await asyncio.create_subprocess_exec(
            self.engine_cmd, stdout=PIPE, stderr=PIPE, stdin=PIPE
        )

    async def usi_cmd(self, cmd):
        if self.listener:
            self.listener(cmd)
        self.proc.stdin.write(cmd.encode(locale.getpreferredencoding()) + b"\n")

    async def wait_until(self, end_responses, timeout=None):
        if not timeout:
            timeout = self.timeout
        lines = []
        while True:
            try:
                line = await asyncio.wait_for(self.proc.stdout.readline(), timeout)
            except asyncio.TimeoutError:
                if self.listener:
                    self.listener("timeout")
            else:
                if not line:  # EOF
                    break
                line = line.strip().decode(locale.getpreferredencoding())
                lines.append(line)
                if self.listener:
                    self.listener(line)
                for end_res in end_responses:
                    if line.startswith(end_res):
                        break
                else:
                    continue
            break
        return lines

    def usi(self):
        self.loop.run_until_complete(self.usi_cmd("usi"))
        return self.loop.run_until_complete(self.wait_until(["usiok"]))

    def isready(self):
        self.loop.run_until_complete(self.usi_cmd("isready"))
        return self.loop.run_until_complete(self.wait_until(["readyok"]))

    def setoption(self, name, value):
        cmd = "setoption name " + name + " value " + str(value)
        self.loop.run_until_complete(self.usi_cmd(cmd))

    def position(self, moves=None, sfen="startpos"):
        cmd = "position " + sfen
        if moves:
            cmd += " moves " + " ".join(moves)
        self.loop.run_until_complete(self.usi_cmd(cmd))

    def go(self, ponder=False, infinite=False, btime=None, wtime=None):
        cmd = "go"
        if ponder:
            cmd += " ponder"
        if infinite:
            cmd += " infinite"
        else:
            if btime is not None:
                cmd += " btime " + str(btime)
            if wtime is not None:
                cmd += " wtime " + str(wtime)
        self.loop.run_until_complete(self.usi_cmd(cmd))
        return self.loop.run_until_complete(self.wait_until(["bestmove", "checkmate"]))

    def go_mate(self, byoyomi=None):
        cmd = "go mate"
        if byoyomi is not None:
            cmd += " " + str(byoyomi)
        else:
            cmd += " infinite"
        self.loop.run_until_complete(self.usi_cmd(cmd))
        return self.loop.run_until_complete(
            self.wait_until(["checkmate"], timeout=int(byoyomi / 1000))
        )

    def stop(self):
        """go infiniteの後のstopではbestmoveを待つ"""
        self.stop_nowait()
        return self.loop.run_until_complete(self.wait_until(["bestmove", "checkmate"]))

    def stop_nowait(self):
        """go infiniteの後でないstopでは待たない"""
        self.loop.run_until_complete(self.usi_cmd("stop"))

    async def __quit(self):
        # self.usi_cmd("quit")
        self.proc.kill()
        return await self.proc.wait()

    def quit(self):
        self.loop.run_until_complete(self.__quit())
        # self.loop.close()
        self.proc = None
        self.loop = None


if __name__ == "__main__":
    engine = "./YaneuraOu-by-gcc"
    usi = UsiEngine(os.path.abspath(os.path.expanduser(engine)), debug=True)
    lines = usi.usi()
    lines = usi.isready()
    lines = usi.position(
        sfen="sfen ln2kg1nl/2gs1s1b1/2ppppppp/1r7/pp7/2P1P3P/PPBP1PPP1/3SR1K2/LN1G1GSNL b - 17"
    )
    lines = usi.go(infinite=True)
    lines = usi.stop()
    usi.quit()

    engine = "./YaneuraOu-mate"
    usi = UsiEngine(os.path.abspath(os.path.expanduser(engine)), debug=True)
    usi.setoption("USI_HASH", 128)
    lines = usi.isready()
    lines = usi.position(
        sfen="sfen l3k3l/6G2/2+NSsppGp/pp2p4/5+r3/5s3/1P6P/2P1S1GP1/L1G1K2NL b NPr2bn7p 1"
    )
    lines = usi.go_mate(10000)
    usi.stop_nowait()
    usi.quit()
