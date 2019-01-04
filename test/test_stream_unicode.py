# -*- coding: utf-8  -*-

from memory_profiler import profile

f = open('/dev/null', 'w')
@profile(stream=f)
def test_unicode(txt):
    # test when unicode is present
    txt = txt.replace (u"ی", u"ي") #Arabic Yah = ي
    return txt


if __name__ == '__main__':
	test_unicode (u"ایست")
