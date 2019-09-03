# -*- coding: utf-8  -*-
@profile
def test_unicode(txt):
    # test when unicode is present
    txt = txt.replace (u"ی", u"ي") #Arabic Yah = ي
    return txt
if __name__ == '__main__':
	test_unicode (u"ایست")