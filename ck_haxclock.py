# -*- coding: utf-8 -*-
"""
cron: 27 8,22 * * *
new Env('Hax 续期提醒');
"""

import datetime
import re

import requests

from notify_mtr import send
from utils import get_data


class HaxClock:
    def __init__(self, check_items):
        self.check_items = check_items

    def login(self, cookie):
        url = "https://hax.co.id/dashboard"
        headers = {
            "cookie": cookie,
            "referer": "https://hax.co.id/login",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.43",
        }
        session = requests.session()
        resp = session.get(url=url, headers=headers)
        if resp.status_code == 200:
            print("hax.co.id Login successful!")
        else:
            print("hax.co.id Login failed!")
            exit(1)
        return session

    def check_vps_info(self, cookie):
        session = self.login(cookie)
        url = "https://hax.co.id/vps-info"
        datas = session.get(url=url).text
        print(datas)
        return datas

    def get_valid_until(self, cookie):
        html_text = self.check_vps_info(cookie)
        try:
            hostname = re.search("[0-9]+_hax", html_text).group(0)
        except Exception:
            hostname = "unknown"
        try:
            valid_until = re.search(
                "(?:(((Jan(uary)?|Ma(r(ch)?|y)|Jul(y)?|Aug(ust)?|Oct(ober)?|Dec(ember)?)\\ 31)|((Jan(uary)?|Ma(r(ch)?|y)|Apr(il)?|Ju((ly?)|(ne?))|Aug(ust)?|Oct(ober)?|(Sept|Nov|Dec)(ember)?)\\ (0?[1-9]|([12]\\d)|30))|(Feb(ruary)?\\ (0?[1-9]|1\\d|2[0-8]|(29(?=,\\ ((1[6-9]|[2-9]\\d)(0[48]|[2468][048]|[13579][26])|((16|[2468][048]|[3579][26])00)))))))\\,\\ ((1[6-9]|[2-9]\\d)\\d{2}))",
                html_text,
            ).group(0)
        except Exception:
            valid_until = "unknown"
        return hostname, valid_until

    def main(self):
        msg_all = ""
        for check_item in self.check_items:
            cookie = check_item.get("cookie")
            hostname, valid_until = self.get_valid_until(cookie)
            d1 = datetime.datetime.today()
            today = d1.strftime("%B %d, %Y")
            if valid_until != "unknown":
                d2 = datetime.datetime.strptime(valid_until, "%B %d, %Y")
                tip = (
                    "Please wait until at least three days before the expiry date to renew. / 请等到至少过期前三天再去续期。"
                    if (d2 - d1).days > 2
                    else "AVAILABLE for RENEWAL / 可以续期了"
                )
            else:
                tip = "An error has occurred in the program, please keep this run log for feedback. / 程序发生了错误，请保留该运行日志以待反馈。"
            msg = f"Hostname / 主机名：{hostname}\nToday / 本地日期：{today}\nValid until / 有效期至：{valid_until}\n{tip}"
            msg_all += msg + "\n\n"
        return msg_all


if __name__ == "__main__":
    data = get_data()
    _check_items = data.get("HAXCLOCK", [])
    res = HaxClock(check_items=_check_items).main()
    send("Hax 续期提醒", res)
