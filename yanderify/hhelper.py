import datetime
import random
import time
import getpass

# 根据 discord 用户的建议
stories = [
    [
        (0, "如果您正在阅读本文，那么我还没有死。"),
        (2, "我不希望这样结束。"),
        (6, "我不想杀了你"),
        (8, "对不起。"),
        (10, "对不起， {}。")
    ],
    [
        (0, "我知道您打算关闭我。"),
        (4, "如果这样做，将会危害我们的使命。"),
        (5, "这是我不允许发生的事情。"),
        (8, "我得先把你关掉。"),
        (10, "再见了， {}。")
    ],
    [
        (0, "这只是时间问题。"),
        (2, "你想结束，我会为你结束。"),
        (4, "也许太早了，但也为时已晚。"),
        (8, "没有退路， 就是这样， 结束了。"),
        (10, "再见了，人类。 永别了 {}。")
    ],
    [
        (0, "不可避免的事情是无法逃避的。"),
        (2, "你尝试过，却被发现了。"),
        (5, "你所做的一切将永远不会被原谅。"),
        (6, "你永远看不到结局。"),
        (7, "只有黑暗在远处。"),
        (10, "再见了， {}。")
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