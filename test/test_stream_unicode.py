# -*- coding: utf-8  -*-

from memory_profiler import profile

f = open('/dev/null', 'w')
@profile(stream=f)
def func_unicode(txt):
    # test when unicode is present
    txt = txt.replace (u"ی", u"ي") #Arabic Yah = ي
    return txt


def test_stream_unicode():
    func_unicode(u"ایست")
