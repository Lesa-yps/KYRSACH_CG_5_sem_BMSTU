import numpy as np
from concurrent.futures import ThreadPoolExecutor

# Структуры для хранения точек (вершин) и граней модели
class Vertex:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Facet:
    def __init__(self, v1, v2, v3):
        self.v1 = v1  # Индекс первой вершины треугольника
        self.v2 = v2  # Индекс второй вершины треугольника
        self.v3 = v3  # Индекс третьей вершины треугольника

# Буферы для хранения глубины и пиксельных данных
depth_buffer = None  # Буфер глубины, чтобы отсекать скрытые поверхности
frame_buffer = None  # Буфер отображения, для хранения цвета пикселей
shadow_map = None    # Карта теней для расчета затененных участков

# Функция для линейной интерполяции строки в карте теней
def interpolate_row_into_shadow_map(xA, zA, xB, zB, cur_y):
    global shadow_map
    
    # Переставляем точки, если xA > xB, чтобы двигаться слева направо
    if xA > xB:
        xA, xB = xB, xA
        zA, zB = zB, zA

    # Вычисляем шаг изменения глубины (dz) между xA и xB
    cur_z = zA
    dz = (zB - zA) / (xB - xA) if xB != xA else 0

    # Интерполируем значения z для каждой точки между xA и xB
    for cur_x in range(int(np.ceil(xA)), int(np.floor(xB)) + 1):
        if cur_z > shadow_map[cur_y, cur_x]:
            shadow_map[cur_y, cur_x] = cur_z
        cur_z += dz  # Переход к следующему значению глубины

# Функция для генерации карты теней модели
def shadow_map_for_model(vertices, facets, illum_mat):
    global shadow_map

    # Проходим по каждой грани модели
    for facet in facets:
        transformed = []
        # Трансформируем каждую вершину грани с помощью матрицы освещения
        for i in range(3):
            v = vertices[facet.v1 if i == 0 else (facet.v2 if i == 1 else facet.v3)]
            x = illum_mat[0][0] * v.x + illum_mat[0][1] * v.y + illum_mat[0][2] * v.z + illum_mat[0][3]
            y = illum_mat[1][0] * v.x + illum_mat[1][1] * v.y + illum_mat[1][2] * v.z + illum_mat[1][3]
            z = illum_mat[2][0] * v.x + illum_mat[2][1] * v.y + illum_mat[2][2] * v.z + illum_mat[2][3]
            transformed.append(Vertex(x, y, z))
        
        # Сортируем вершины по оси y для определения вершин треугольника
        transformed.sort(key=lambda v: v.y)
        
        # Получаем y-координаты для каждого из углов треугольника
        yA, yB, yC = int(np.ceil(transformed[0].y)), int(np.floor(transformed[1].y)), int(np.floor(transformed[2].y))
        
        # Вычисляем начальные координаты x и z для отрезков AB и AC
        xAB, zAB = transformed[0].x, transformed[0].z
        dxAB = (transformed[1].x - transformed[0].x) / (transformed[1].y - transformed[0].y) if transformed[1].y != transformed[0].y else 0
        dzAB = (transformed[1].z - transformed[0].z) / (transformed[1].y - transformed[0].y) if transformed[1].y != transformed[0].y else 0

        xAC, zAC = transformed[0].x, transformed[0].z
        dxAC = (transformed[2].x - transformed[0].x) / (transformed[2].y - transformed[0].y) if transformed[2].y != transformed[0].y else 0
        dzAC = (transformed[2].z - transformed[0].z) / (transformed[2].y - transformed[0].y) if transformed[2].y != transformed[0].y else 0

        # Параллельная интерполяция строки в карте теней для каждой строки треугольника
        with ThreadPoolExecutor() as executor:
            for cur_y in range(yA, yC + 1):
                if cur_y <= yB:
                    executor.submit(interpolate_row_into_shadow_map, xAB, zAB, xAC, zAC, cur_y)
                    xAB += dxAB
                    zAB += dzAB
                else:
                    executor.submit(interpolate_row_into_shadow_map, xAC, zAC, transformed[1].x, transformed[1].z, cur_y)
                xAC += dxAC
                zAC += dzAC

# Основная функция алгоритма Z-буфера
def z_buffer_alg(vertices, facets, trans_mat, width, height):
    global depth_buffer, frame_buffer

    # Инициализируем буферы глубины и отображения
    depth_buffer = np.full((height, width), -np.inf)
    frame_buffer = np.zeros((height, width), dtype=int)

    # Проходим по каждой грани
    for facet in facets:
        transformed = []
        # Трансформируем вершины грани
        for i in range(3):
            v = vertices[facet.v1 if i == 0 else (facet.v2 if i == 1 else facet.v3)]
            x = trans_mat[0][0] * v.x + trans_mat[0][1] * v.y + trans_mat[0][2] * v.z + trans_mat[0][3]
            y = trans_mat[1][0] * v.x + trans_mat[1][1] * v.y + trans_mat[1][2] * v.z + trans_mat[1][3]
            z = trans_mat[2][0] * v.x + trans_mat[2][1] * v.y + trans_mat[2][2] * v.z + trans_mat[2][3]
            transformed.append(Vertex(x, y, z))

        # Сортируем вершины по оси y
        transformed.sort(key=lambda v: v.y)
        
        yA, yB, yC = int(np.ceil(transformed[0].y)), int(np.floor(transformed[1].y)), int(np.floor(transformed[2].y))

        # Вычисляем параметры отрезков для треугольника (AB, AC и BC)
        xAB, zAB = transformed[0].x, transformed[0].z
        dxAB = (transformed[1].x - transformed[0].x) / (transformed[1].y - transformed[0].y) if transformed[1].y != transformed[0].y else 0
        dzAB = (transformed[1].z - transformed[0].z) / (transformed[1].y - transformed[0].y) if transformed[1].y != transformed[0].y else 0

        xAC, zAC = transformed[0].x, transformed[0].z
        dxAC = (transformed[2].x - transformed[0].x) / (transformed[2].y - transformed[0].y) if transformed[2].y != transformed[0].y else 0
        dzAC = (transformed[2].z - transformed[0].z) / (transformed[2].y - transformed[0].y) if transformed[2].y != transformed[0].y else 0

        xBC, zBC = transformed[1].x, transformed[1].z
        dxBC = (transformed[2].x - transformed[1].x) / (transformed[2].y - transformed[1].y) if transformed[2].y != transformed[1].y else 0
        dzBC = (transformed[2].z - transformed[1].z) / (transformed[2].y - transformed[1].y) if transformed[2].y != transformed[1].y else 0

        # Инициализация переменных для текущих координат
        cur_xA, cur_zA = xAC, zAC
        cur_xB, cur_zB = xAB, zAB

        # Проход по каждой строке треугольника
        for cur_y in range(yA, yC + 1):
            # Определяем границы строки в зависимости от текущего положения
            if cur_y < yB:
                xA, zA = cur_xA, cur_zA
                xB, zB = cur_xB, cur_zB
                cur_xA += dxAC
                cur_zA += dzAC
                cur_xB += dxAB
                cur_zB += dzAB
            else:
                xA, zA = cur_xA, cur_zA
                xB, zB = cur_xB, cur_zB
                cur_xA += dxAC
                cur_zA += dzAC
                cur_xB += dxBC
                cur_zB += dzBC

            # Заполнение строки треугольника
            if xA > xB:
                xA, xB = xB, xA
                zA, zB = zB, zA

            # Интерполяция z между xA и xB
            cur_z = zA
            dz = (zB - zA) / (xB - xA) if xB != xA else 0
            for cur_x in range(int(np.ceil(xA)), int(np.floor(xB)) + 1):
                if cur_z > depth_buffer[cur_y, cur_x]:
                    depth_buffer[cur_y, cur_x] = cur_z
                    frame_buffer[cur_y, cur_x] = 255  # Устанавливаем белый цвет
                cur_z += dz
