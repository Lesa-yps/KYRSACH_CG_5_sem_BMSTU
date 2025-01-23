import pytest
from Objects import Wall, Door, Window

@pytest.mark.parametrize("color, sizes, expected", [
    ("red", [10, 3, 5, 0, 0], {"type": "стена", "color": "red", "sizes": [10, 3, 5, 0, 0]}),
    ("blue", [12, 4, 6, 1, 1], {"type": "стена", "color": "blue", "sizes": [12, 4, 6, 1, 1]}),
    ("green", [15, 5, 7, 2, 2], {"type": "стена", "color": "green", "sizes": [15, 5, 7, 2, 2]}),
])
def test_wall(color, sizes, expected):
    wall = Wall((color, *sizes))
    assert wall.take_dict_params() == expected


@pytest.mark.parametrize("color, sizes, expected", [
    ("brown", [2, 1, 3, 0, 0, 0, 0, 0], {"type": "дверь", "color": "brown", "sizes": [2, 1, 3, 0, 0, 0, 0, 0]}),
    ("white", [3, 1, 2, 1, 1, 1, 1, 1], {"type": "дверь", "color": "white", "sizes": [3, 1, 2, 1, 1, 1, 1, 1]}),
    ("black", [1.5, 0.8, 2.5, 0, 0, 0, 0, 0], {"type": "дверь", "color": "black", "sizes": [1.5, 0.8, 2.5, 0, 0, 0, 0, 0]}),
])
def test_door(color, sizes, expected):
    door = Door((color, *sizes))
    assert door.take_dict_params() == expected


@pytest.mark.parametrize("color, sizes, expected", [
    ("transparent", [4, 1, 5, 0, 0, 0, 0, 0, 0], {"type": "окно", "color": "transparent", "sizes": [4, 1, 5, 0, 0, 0, 0, 0, 0]}),
    ("blue", [3, 1, 4, 1, 1, 1, 1, 1, 1], {"type": "окно", "color": "blue", "sizes": [3, 1, 4, 1, 1, 1, 1, 1, 1]}),
    ("frosted", [2.5, 1, 3.5, 0, 0, 0, 0, 0, 0], {"type": "окно", "color": "frosted", "sizes": [2.5, 1, 3.5, 0, 0, 0, 0, 0, 0]}),
])
def test_window(color, sizes, expected):
    window = Window((color, *sizes))
    assert window.take_dict_params() == expected