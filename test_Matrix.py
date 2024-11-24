import pytest
from Matrix import Matrix
from Point import Point


@pytest.mark.parametrize("point, matrix", [
    (Point(0, 0, 0), Matrix()),
    (Point(1, 1, 1), Matrix()),
    (Point(0, 0, 0), Matrix().rotate_axis("X", 30)),
    (Point(1, 1, 1), Matrix().rotate_axis("X", 30)),
    (Point(1, 1, 1), Matrix().rotate_axis("Y", -30)),
    (Point(1, 2, -3), Matrix().rotate_axis("X", 30)),
    (Point(0, 1, -7), Matrix().rotate_axis("Y", -30)),
])
def test_transform_matrix(point, matrix):
    new_point = matrix.transform_point(point)
    res_point = matrix.anti_transform_point(new_point)
    assert point.is_same(res_point)

