import datetime
import random
import time
import getpass

import locale
sys_language = locale.getdefaultlocale()
if "zh" in sys_language[0]:
    sys_language = "chinese"
else:
    sys_language = "english"
import json
with open("languages.json", "r", encoding="utf-8") as f:
    languages = json.load(f)

# 根据 discord 用户的建议
# as per suggestion of a discord user
stories = [
    [
        (0, languages["hhelper1"][sys_language]),
        (2, languages["hhelper2"][sys_language]),
        (6, languages["hhelper3"][sys_language]),
        (8, languages["hhelper4"][sys_language]),
        (10, languages["hhelper5"][sys_language])
    ],
    [
        (0, languages["hhelper6"][sys_language]),
        (4, languages["hhelper7"][sys_language]),
        (5, languages["hhelper8"][sys_language]),
        (8, languages["hhelper9"][sys_language]),
        (10, languages["hhelper10"][sys_language])
    ],
    [
        (0, languages["hhelper11"][sys_language]),
        (2, languages["hhelper12"][sys_language]),
        (4, languages["hhelper13"][sys_language]),
        (8, languages["hhelper14"][sys_language]),
        (10, languages["hhelper15"][sys_language])
    ],
    [
        (0, languages["hhelper16"][sys_language]),
        (2, languages["hhelper17"][sys_language]),
        (5, languages["hhelper18"][sys_language]),
        (6, languages["hhelper19"][sys_language]),
        (7, languages["hhelper20"][sys_language]),
        (10, languages["hhelper21"][sys_language])
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
        