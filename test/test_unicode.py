# -*- coding: utf-8  -*-
from memory_profiler import profile


@profile
def run_unicode(txt):
    # test when unicode is present
    txt = txt.replace (u"ی", u"ي") #Arabic Yah = ي
    return txt

def test_unicode():
    run_unicode(u"ایست")
