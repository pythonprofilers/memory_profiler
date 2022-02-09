from memory_profiler import profile


@profile
def test_with_profile(arg1):
    """dummy doc"""
    return None


if __name__ == '__main__':
    assert test_with_profile.__doc__ == "dummy doc"
    assert test_with_profile.__name__ == "test_with_profile"
