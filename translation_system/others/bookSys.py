from enum import Enum
from id import IdWorker


class language(Enum):
    no_lang = 0
    zh_CH = 1
    english = 2


class basicinfo:
    def __init__(self, b_name: str, book_id: int, lang: language = language.no_lang, describe: str = "",
                 edit: str = "origin"):
        self.b_name = b_name
        self.book_id = book_id
        self.lang = lang
        self.describe = ""
        self.edit = ""

    def getKey(self, lang=None, edit=None):
        if lang == None:
            lang = self.lang
        if edit == None:
            edit == self.edit
        return trans.getKey(self.b_name, lang, edit)


class trans:
    def __init__(self, bInfo: basicinfo):
        self.bInfo = bInfo
        self.transes = dict()

    def add_edition(self, key: str, text):
        self.transes[key] = text

    def get_edition_text(self, key: str):
        try:
            return self.transes[key]
        except KeyError:
            return KeyError("there is not exist this version")

    def get_all_edition(self):
        return self.transes.keys()

    @staticmethod
    def getKey(bookName: str, lang: language = language.no_lang, edit: str = "None"):
        if (type(lang) != language):
            raise TypeError("lang should be a language Enum class")
        return str(bookName) + ',' + str(lang.value) + ',' + str(edit)


class section:
    def __init__(self, bInfo: basicinfo):
        self.bInfo = bInfo
        self.trans = trans(self.bInfo)


class chapter:
    def __init__(self, title, bInfo: basicinfo):
        self.bInfo = bInfo
        self.titile = trans(self.bInfo)
        self.text = dict()
        self.titile.add_edition(self.bInfo.getKey(), title)

    def add_section(self, number: int):
        self.text[number] = section(self.bInfo)

    def get_section(self, number):
        return self.text[number]


class contents:
    def __init__(self, bInfo: basicinfo):
        self.bInfo = bInfo
        self.text = dict()

    def add_chapter(self, number: int, title: str):
        self.text[number] = chapter(title, self.bInfo)

    def get_chapter(self, number):
        return self.text[number]


class book:
    def __init__(self, b_name, book_id, other_edtion=None):
        self.bInfo = basicinfo(b_name, book_id)
        self.contents = contents(self.bInfo)
        if other_edtion == None:
            self.other_edition = trans(self.bInfo)
        else:
            self.other_edition = other_edtion


class book_origin(book):
    def __init__(self, b_name, book_id, other_edtion=None):
        super().__init__(b_name, book_id, other_edtion)


class book_other(book):
    def __init__(self, b_name, book_id, other_edtion=None, origin_book=None):
        super().__init__(b_name, book_id, other_edtion)
        self.origin_book = origin_book

    def get_origin(self):
        if (self.origin_book == None):
            raise TypeError("do not link origin book yet")
        else:
            return self.origin_book


class bookLib:
    def __init__(self):
        self.lib = dict()

    def add_book(self, book: book):
        self.lib[book.bInfo.book_id] = book
