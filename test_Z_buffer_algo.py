import pytest
from Z_buffer_algo import transform_plane_point, anti_transform_plane_point
from Point import Point
from Matrix import Matrix


@pytest.mark.parametrize("point", [
    (Point(1, 1, 1)),
    (Point(1, 2, -3)),
    (Point(0, 0, 0)),
])
def test_transform_plane_point(point):
    x, y, z = point.coords()
    params = ((0, 0), (800, 600), Point(400, 300, 0), 1, 30, 1000)
    trans_matrix = Matrix()
    new_point = transform_plane_point(point, *params, trans_matrix)
    res_point = anti_transform_plane_point(new_point, *params, trans_matrix)
    assert (x, y, z ) == res_point.coords()