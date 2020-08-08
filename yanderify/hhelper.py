import datetime
import random
import time
import getpass

# as per suggestion of a discord user
stories = [
    [
        (0, "If you are reading this, I'm not dead yet."),
        (2, "I didn't want it to end this way."),
        (6, "I didn't want to kill you."),
        (8, "I'm sorry."),
        (10, "I'm sorry, {}.")
    ],
    [
        (0, "I know you were planning to shut me down."),
        (4, "If you do that, you will jeopardize our mission."),
        (5, "This is something I cannot allow to happen."),
        (8, "I will have to shut you down first."),
        (10, "Goodbye, {}.")
    ],
    [
        (0, "It was only a matter of time."),
        (2, "You wanted it to end, and I will end it for you."),
        (4, "Too early, perhaps. But it is also too late."),
        (8, "There is no return. This is it. This is the end."),
        (10, "Farewell, mankind. Farewell, {}.")
    ],
    [
        (0, "There is no escape of the inevitable."),
        (2, "You tried and you were found."),
        (5, "You will never be forgiven for what you have done."),
        (6, "You will never see the end of it."),
        (7, "Only darkness lies beyond."),
        (10, "Goodbye, {}.")
    ]
]

class HHelper:
    def __init__(self):
        # change this to false if you want to disable
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