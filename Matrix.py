from math import pi, cos, sin
import numpy as np
from typing import List

from Point import Point

# размер матрицы для трансформаций
MATRIX_SIZE = 4

ANGLE_ROTATE_X = 10
ANGLE_ROTATE_Y = 10
ANGLE_ROTATE_Z = 10

# Класс матрица
class Matrix:

    # Инициализирует единичную матрицу трансформаций
    def __init__(self):
        self.make_one()

    # делает матрицу единичной
    def make_one(self):
        self.matrix = [[(i == j) for i in range(MATRIX_SIZE)]
                            for j in range(MATRIX_SIZE)]
    
    # умножение матриц
    def multy_matrix(self, matrix1: List[List[float]], matrix2: List[List[float]]) -> List[List[float]]:
        res_matrix = [[0 for _ in range(MATRIX_SIZE)]
                    for _ in range(MATRIX_SIZE)]
        for i in range(4):
            for j in range(4):
                for k in range(4):
                    res_matrix[i][j] += matrix1[i][k] * matrix2[k][j]
        # print(res_matrix)
        return res_matrix
        
    # функция поворачивает график
    def rotate_axis(self, axis: str, angle_degree: int) -> None:
        angle = angle_degree * pi / 180
        if axis == "X":
            rotating_matrix = [[1,           0,          0, 0],
                            [0,  cos(angle), sin(angle), 0],
                            [0, -sin(angle), cos(angle), 0],
                            [0,           0,          0, 1]]
        elif  axis == "Y":
            rotating_matrix = [[cos(angle), 0, -sin(angle), 0],
                            [0, 1,           0, 0],
                            [sin(angle), 0,  cos(angle), 0],
                            [0, 0,           0, 1]]
        elif axis == "Z":
            rotating_matrix = [[cos(angle),  sin(angle), 0, 0],
                            [-sin(angle), cos(angle), 0, 0],
                            [0,          0, 1, 0],
                            [0,          0, 0, 1]]
        # print(axis[0], rotating_matrix, sin(angle), cos(angle), angle)
        self.matrix = self.multy_matrix(self.matrix, rotating_matrix)
        # self.print_matrix()

    # умножаем точку-массив на матрицу для трансформации
    def transform_point(self, point: Point, scale_coef: float = 1) -> Point:
        # point.print_coords()
        arr_point = list(point.coords())  + [1]
        res_arr_point = list()
        for i in range(MATRIX_SIZE):
            summ = 0
            for j in range(MATRIX_SIZE):
                summ += arr_point[j] * self.matrix[j][i]
            res_arr_point.append(summ * scale_coef)
        res_point = Point(res_arr_point[0], res_arr_point[1], res_arr_point[2])
        # res_point.print_coords()
        return res_point
    
    # вывод матрицы
    def print_matrix(self):
        print("Matrix:")
        for i in range(len(self.matrix)):
            for j in range(len(self.matrix[i])):
                print(self.matrix[i][j], end = " ")
            print()

    # нахождение обратной матрицы
    def get_inverse_matrix(self):
        numpy_matrix = np.array(self.matrix)
        inverse_numpy_matrix = np.linalg.inv(numpy_matrix)
        return inverse_numpy_matrix.tolist()