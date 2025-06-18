from memory_profiler import profile


@profile
def func_with_profile(arg1):
    """dummy doc"""
    return None


def test_with_profile():
    assert func_with_profile.__doc__ == "dummy doc"
    assert func_with_profile.__name__ == "func_with_profile"
