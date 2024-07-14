def square(num):
    return num * num


def test_square_positive_number():
    assert square(2) == 4


def test_square_negative_number():
    assert square(-3) == 9


def test_square_zero():
    assert square(0) == 0


def test_square_float():
    assert square(2.5) == 6.25


def test_square_large_number():
    assert square(1000) == 1000000
