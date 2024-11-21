from Objects import Wall

def test_wall():
    wall = Wall(("red", 10, 3, 5, 0, 0))
    assert wall.take_dict_params() == {
        "type": "стена",
        "color": "red",
        "sizes": [10, 3, 5, 0, 0]
    }
    print("Wall test passed!")

test_wall()