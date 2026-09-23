from cart import total


def test_total():
    items = [{"price": 10, "qty": 2}, {"price": 5, "qty": 1}]
    assert total(items) == 25
