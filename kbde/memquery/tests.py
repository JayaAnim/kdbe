import unittest
from types import SimpleNamespace

from .manager import DictManager, ObjectManager


NUMBERS = range(100000)
WORDS = [
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    ]

def generateDict():
    obj_list = []
    for number in NUMBERS:
        for word in WORDS:
            obj = {
                "number": number,
                "word": word,
                }
            obj_list.append(obj)
    return obj_list

def generateObjects():
    obj_list = []
    for number in NUMBERS:
        for word in WORDS:
            obj = SimpleNamespace()
            obj.number = number
            obj.word = word
            obj_list.append(obj)
    return obj_list


class ManagerTest(unittest.TestCase):
    def testDict(self):
        self.obj_list = generateDict()
        manager = DictManager(self.obj_list)
        self.query(manager)
        new = {
            "number": 2,
            "word": "2",
            }
        manager.add(new)
        self.query(manager)

    def testObj(self):
        obj_list = generateObjects()
        manager = ObjectManager(obj_list)
        self.query(manager)
        new = SimpleNamespace()
        new.number = 2
        new.word = "2"
        manager.add(new)
        self.query(manager)

    def query(self,manager):
        #filter
        print(manager.filter(number=2))
        print(manager.filter(number=-1))

        #get
        print(manager.get(number=2,word="two"))

        #count
        print(manager.count())
        print(manager.count(number=2))
        print(manager.count(word="two"))
