from Point import Point
from Scene import Scene

# фейковый canvas, чтобы инициализировать Scene
class FakeCanvas:
    pass


def test_combo_matrix():

    canvas = FakeCanvas()
    scene = Scene(canvas)

    params_Z_buffer = ((0, 0), (3, 3), Point(1, 1, 0), 1, 1, 1000)

    matrix = [[(0, "#333333"), (0, "#333333"), (0, "#333333")],
              [(0, "#333333"), (1, "#222222"), (0, "#333333")],
              [(0, "#333333"), (0, "#333333"), (0, "#333333")]]
    
    neg_inf = float("-inf")
    matrix_light = [[(neg_inf, "#111111"), (0, "#222222"), (neg_inf, "#111111")],
                    [(1, "#333333"), (1, "#333333"), (1, "#333333")],
                    [(neg_inf, "#111111"), (neg_inf, "#111111"), (neg_inf, "#111111")]]
    
    right_res_matrix = [[(0, '#282828'), (0, '#282828'), (0, '#282828')],
                        [(0, '#282828'), (1, '#222222'), (0, '#282828')],
                        [(0, '#333333'), (0, '#333333'), (0, '#333333')]]

    # наложение матрицы теней на основную матрицу
    matrix_res = scene.combo_matrix(matrix, matrix_light, params_Z_buffer)

    print(matrix_res)
    print(matrix_res == right_res_matrix)

test_combo_matrix()