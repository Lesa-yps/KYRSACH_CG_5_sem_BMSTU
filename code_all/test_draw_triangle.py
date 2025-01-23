import pytest
import re
from Z_buffer_algo import add_point_to_Z_matrix, add_row_to_Z_matrix, add_triangle_to_Z_matrix, Point, calc_min_max_x_y


def read_points_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    points = []
    point_pattern = r"Point\(([^,]+), ([^,]+), ([^)]+)\)"
    for line in lines:
        matches = re.findall(point_pattern, line)
        if matches:
            triangle = [Point(float(x), float(y), float(z)) for x, y, z in matches]
            points.append(triangle)
    return points

# Mock для лог-файла
class MockLogFile:
    def __init__(self):
        self.content = []
    
    def write(self, message):
        self.content.append(message)
    
    def get_content(self):
        return self.content

# Хелпер для создания пустого Z-буфера
def create_z_buffer(width, height, z_default=float('-inf')):
    return [[(z_default, [0, 0, 0]) for _ in range(width)] for _ in range(height)]
"""
# Тест для функции add_point_to_Z_matrix
def test_add_point_to_Z_matrix():
    matrix = create_z_buffer(10, 10)
    log_file = MockLogFile()
    point = Point(5, 5, 5)
    color = [255, 0, 0]
    
    # Добавляем точку
    result = add_point_to_Z_matrix(matrix, point, color, log_file)

    # Проверяем, что точка добавилась правильно
    assert result[5][5] == (5, color)

    # Проверяем, что другие точки не изменились
    for y in range(10):
        for x in range(10):
            if (x, y) != (5, 5):
                assert result[y][x] == (float('-inf'), [0, 0, 0])
                

# Тест для функции add_row_to_Z_matrix
def test_add_row_to_Z_matrix():
    matrix = create_z_buffer(10, 10)
    log_file = MockLogFile()
    point1 = Point(2, 5, 5)
    point2 = Point(7, 5, 10)
    color = [0, 255, 0]

    # Добавляем строку
    result = add_row_to_Z_matrix(matrix, point1, point2, color, log_file)

    # Проверяем, что строка закрашена правильно
    for x in range(2, 8):
        z_value = 5 + (10 - 5) * (x - 2) / (7 - 2)  # Линейная интерполяция по Z
        assert result[5][x] == (round(z_value), color)

    # Проверяем, что остальные точки не закрашены
    for y in range(10):
        for x in range(10):
            if y != 5 or x < 2 or x > 7:
                assert result[y][x] == (float('-inf'), [0, 0, 0])
"""

# Тест для функции add_triangle_to_Z_matrix
@pytest.mark.parametrize("point1, point2, point3, color", [
    #(Point(60, 30, -40), Point(30, 30, -45), Point(60, 1, -40), [0, 0, 255]),
    #(Point(5.9380890410646096, 3.1674717108046025, -4.1675562640063276), Point(2.994201987002377, 3.150905674655172, -4.6885007970071186), Point(5.9380890410646096, 0.1799743795966208, -4.1675562640063276), [0, 0, 255]),
    *[(point1, point2, point3, [255, 0, 0]) for point1, point2, point3 in read_points_from_file("log_file_Z.txt")]
    #(Point(548.95, 308.15, 77.01), Point(442.07, 304.93, 17.01), Point(562.83, 254.53, 51.03), [0, 0, 255])
])
def test_add_triangle_to_Z_matrix(point1, point2, point3, color):
    log_file = MockLogFile()
    triangle = [point1, point2, point3]
    rect_x_y = {"max_x": float("-inf"), "max_y": float("-inf"), "min_x": float("+inf"), "min_y": float("+inf")}
    rect_x_y = calc_min_max_x_y(rect_x_y, triangle + [color])
    print(rect_x_y)
    matrix = create_z_buffer(rect_x_y["max_x"] + 4, rect_x_y["max_y"] + 4)

    # Добавляем треугольник
    result = add_triangle_to_Z_matrix(matrix, triangle, color, log_file)
    #print("\nMatrix:\n", '\n'.join(' '.join(map(str, row)) for row in matrix), end = "\n\n")

    # Проверяем точки вне треугольника
    #count = 0
    for y in range(len(result)):
        for x in range(len(result[0])):
            if x < rect_x_y["min_x"] or y < rect_x_y["min_y"] or x > rect_x_y["max_x"] or y > rect_x_y["max_y"]:
                if result[y][x][1] != [0, 0, 0]:
                    #count += 1
                    #print(f"y = {y}, x = {x}")
                    print(f"Ошибка на точке вне треугольника: x={x}, y={y}, color={result[y][x][1]}")
                    print(f"Треугольник: {point1.coords()}, {point2.coords()}, {point3.coords()}, Ожидаемый цвет: {[0, 0, 0]}")
                assert result[y][x][1] == [0, 0, 0]
    #assert count == 0
