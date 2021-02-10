import datetime
import random
import time
import getpass

import locale
import json

sys_language = locale.getdefaultlocale()
sys_language = sys_language[0]
with open(sys_language+".json", "r", encoding="utf-8") as f:
    languages = json.load(f)

# 根据 discord 用户的建议
# as per suggestion of a discord user
stories = [
    [
        (0, languages["hhelper1"]),
        (2, languages["hhelper2"]),
        (6, languages["hhelper3"]),
        (8, languages["hhelper4"]),
        (10, languages["hhelper5"])
    ],
    [
        (0, languages["hhelper6"]),
        (4, languages["hhelper7"]),
        (5, languages["hhelper8"]),
        (8, languages["hhelper9"]),
        (10, languages["hhelper10"])
    ],
    [
        (0, languages["hhelper11"]),
        (2, languages["hhelper12"]),
        (4, languages["hhelper13"]),
        (8, languages["hhelper14"]),
        (10, languages["hhelper15"])
    ],
    [
        (0, languages["hhelper16"]),
        (2, languages["hhelper17"]),
        (5, languages["hhelper18"]),
        (6, languages["hhelper19"]),
        (7, languages["hhelper20"]),
        (10, languages["hhelper21"])
    ]
]

class HHelper:
    def __init__(self):
        # 如果要禁用，请将其更改为false
        enabled = True
        hour = datetime.datetime.now().hour
        enabled = enabled and ((hour >= 20) or (hour <= 7))
        self.enabled = enabled
        self.cursor = -1
        self.story = random.choice(stories)
    def username(self):
        return getpass.getuser()
    def sleep(self):
        time.sleep(0.5 + random.random())
    def forward(self, point):
        if not self.enabled:
            return
        while point > self.cursor:
            sentence = None
            for (i, s) in self.story:
                if i > self.cursor:
                    if point < i:
                        return
                    else:
                        self.cursor = i
                        sentence = s
                        break
            self.sleep()
            print(sentence.format(self.username()))
    def finish(self):
        self.forward(10)
        self.sleep()
        self.sleep()
