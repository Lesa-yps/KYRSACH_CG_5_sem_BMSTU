
from Point import Point

# алгоритм реализующий Z-буфер
# на вход: кортеж - смещение экрана по х и у, кортеж - ширина и высота экрана +
# + массив из кортежей: 4 точки - координаты плоскости (расположены в порядке обхода по кругу) + цвет
# на выход: матрица пикселей - цветов

COORD_Z = 0
# в матрице
Z_PART = 0
COLOR_PART = 1

FON_COLOR = None
BORDER_COLOR = "#000000"    



# Рисуем граничную линию
def draw_border_line(matrix_pixels, point1, point2, log_file):
    # log_file.write(f"   border row: {(point1.coords(), point2.coords())}\n")
    Xa, Ya, Za = point1.coords()
    Xb, Yb, Zb = point2.coords()
    dx, dy, dz = Xb - Xa, Yb - Ya, Zb - Za
    dmax = max(abs(dx), abs(dy), abs(dz))
    add_point_to_Z_matrix(matrix_pixels, point1, BORDER_COLOR, log_file)
    if (dmax != 0):
        # шаг изменения по коодинатам
        dx, dy, dz = dx / dmax, dy / dmax, dz / dmax
        xi, yi, zi = Xa, Ya, Za
        i = 0
        while (i < dmax):
            xi, yi, zi = xi + dx, yi + dy, zi + dz
            add_point_to_Z_matrix(matrix_pixels, Point(xi, yi, zi), BORDER_COLOR, log_file)
            i += 1
    return matrix_pixels


# Добавляем в Z-буфер точку с проверкой близости
def add_point_to_Z_matrix(matrix_pixels, point, color, log_file):
    X, Y, Z = map(round, point.coords())
    # log_file.write(f"     TRY TO DRAW POINT ({X}, {Y}, {Z}) into matrix n = {len(matrix_pixels)} m = {len(matrix_pixels[0])}")
    if Y < len(matrix_pixels) and X < len(matrix_pixels[0]) and X >= 0 and Y >= 0:
        if matrix_pixels[Y][X][Z_PART] <= Z and not (matrix_pixels[Y][X][COLOR_PART] == BORDER_COLOR and matrix_pixels[Y][X][Z_PART] == Z):
            matrix_pixels[Y][X] = (Z, color)
            # log_file.write(f" - DONE")
    # log_file.write(f"\n")
    return matrix_pixels

# Добавляем в Z-буфер строку по у от point1 до point2 (по алгоритму рисования линии ЦДА) (y = const)
def add_row_to_Z_matrix(matrix_pixels, point1, point2, color, log_file):
    # log_file.write(f"   row: {(point1.coords(), point2.coords())}\n")
    Xa, Xb, Y, Za, Zb = point1.x, point2.x, point1.y, point1.z, point2.z
    dx = Xb - Xa
    dz = Zb - Za
    dmax = max(abs(dx), abs(dz))
    add_point_to_Z_matrix(matrix_pixels, point1, color, log_file)
    if (dmax != 0):
        # шаг изменения по коодинатам
        dx /= dmax
        dz /= dmax
        xi, zi = Xa, Za
        i = 0
        while (i < dmax):
            xi += dx
            zi += dz
            add_point_to_Z_matrix(matrix_pixels, Point(xi, Y, zi), color, log_file)
            i += 1
    return matrix_pixels


# Добавляем в Z-буфер треугольник
def add_triangle_to_Z_matrix(matrix_pixels, triangle, color, log_file):
    # сортируем точки по высоте (у)
    C, B, A = tuple(sorted(list(triangle), key=lambda point: point.y))
    # log_file.write(f"   triangle: {(A.coords(), B.coords(), C.coords())}\n")
    y_min, y_max = C.y, A.y

    dy_AC = C.y - A.y
    dx_AC = (C.x - A.x) / abs(dy_AC) if dy_AC != 0 else 0
    dz_AC = (C.z - A.z) / abs(dy_AC) if dy_AC != 0 else 0

    dy_AB = B.y - A.y
    dx_AB = (B.x - A.x) / abs(dy_AB) if dy_AB != 0 else 0
    dz_AB = (B.z - A.z) / abs(dy_AB) if dy_AB != 0 else 0

    dy_BC = C.y - B.y
    dx_BC = (C.x - B.x) / abs(dy_BC) if dy_BC != 0 else 0
    dz_BC = (C.z - B.z) / abs(dy_BC) if dy_BC != 0 else 0

    # log_file.write(f"   AC = {(dx_AC, -1, dz_AC)}, AB = {(dx_AB, -1, dz_AB)}, BC = {(dx_BC, -1, dz_BC)}\n")

    # Проходимся по всем строкам у
    point1 = Point(A.x, y_max, A.z) # одна из границ строки по у
    # вторая граница строки по у
    if dy_AB == 0:
        point2 = Point(B.x, y_max, B.z)
    else:
        point2 = Point(A.x, y_max, A.z) 
    while point1.y >= y_min:
        # обработка строки от point1 до point2
        matrix_pixels = add_row_to_Z_matrix(matrix_pixels, point1, point2, color, log_file)

        if point2.y < B.y:
            point2.add(dx_BC, -1, dz_BC)
        else:
            point2.add(dx_AB, -1, dz_AB)
        point1.add(dx_AC, -1, dz_AC)

    return matrix_pixels


# преобразования точек
def transform_plane_points(plane, offsets, dimensions, transform_matrix, center_point, scale_coef, size_square, max_z, log_file):
    # распаковка входных данных
    (dx_screen, dy_screen) = offsets
    (width_screen, height_screen) = dimensions
    point1, point2, point3, point4, color = plane
    # преобразуем координаты плоскости из "квадратовых" в мировые
    point1.multy(size_square).add(-dx_screen, -dy_screen, 0), point2.multy(size_square).add(-dx_screen, -dy_screen, 0)
    point3.multy(size_square).add(-dx_screen, -dy_screen, 0), point4.multy(size_square).add(-dx_screen, -dy_screen, 0)
    # разворачиваем у
    point1.y, point2.y, point3.y, point4.y = - point1.y, - point2.y, - point3.y, - point4.y
    # сдвиг в центр
    dx, dy, dz = center_point.coords()
    # print(dx, dy, dz)
    point1.add(-dx, -dy, -dz), point2.add(-dx, -dy, -dz), point3.add(-dx, -dy, -dz), point4.add(-dx, -dy, -dz)
    # добавляем поворот камеры и масштаб
    # log_file.write(f"\n   points before matrix: {(point1.coords(), point2.coords(), point3.coords(), point4.coords())}\n")
    point1, point2, point3, point4 = transform_matrix.transform_point(point1, scale_coef), transform_matrix.transform_point(point2, scale_coef),\
        transform_matrix.transform_point(point3, scale_coef), transform_matrix.transform_point(point4, scale_coef)
    point1.add(dx, dy, dz), point2.add(dx, dy, dz), point3.add(dx, dy, dz), point4.add(dx, dy, dz)
    # log_file.write(f"   points after matrix: {(point1.coords(), point2.coords(), point3.coords(), point4.coords())}\n")
    # опускаем у
    point1.y, point2.y, point3.y, point4.y = height_screen - 3 + point1.y, height_screen - 3 + point2.y, height_screen - 3 + point3.y, height_screen - 3 + point4.y
    # преобразование координат с помощью ортогональной проекции
    point1, point2, point3, point4 = point1.project(max_z), point2.project(max_z), point3.project(max_z), point4.project(max_z)
    return point1, point2, point3, point4, color


# Алгоритм Z-буфера для списка плоскостей
def Z_buffer_algo(offsets, dimensions, list_planes, transform_matrix, center_point, scale_coef, size_square, max_z, log_filename):

    log_file = open(log_filename, "w")

    # распаковка входных данных
    (dx_screen, dy_screen) = offsets
    (width_screen, height_screen) = dimensions
    # матрица кортежей (буфер кадра - фоновое значение, Z-буфер - минус бесконечность)
    matrix_pixels = [[(float('-inf'), FON_COLOR) for _ in range(width_screen)] for _ in range(height_screen)]

    # преобразуем координаты центра из "квадратовых" в мировые
    center_point.multy(size_square).add(-dx_screen, -dy_screen, 0)
    # разворачиваем у
    center_point.y = - center_point.y

    # сам алгоритм:
    # проходимся по всем плоскостям
    i = 0
    for plane in list_planes:
        # преобразования точек
        point1, point2, point3, point4, color = transform_plane_points(plane, offsets, dimensions, transform_matrix, center_point, scale_coef, size_square, max_z, log_file)
        # разделим каждую квадрат-плоскость на 2 треугольника для упрощения
        triangle_1 = (point1, point2, point3)
        triangle_2 = (point3, point4, point1)
        # Запись треугольников в лог-файл
        # log_file.write(f"\ni = {i}\nPoints: {(point1.coords(), point2.coords(), point3.coords(), point4.coords())}\n")
        # Добавляем в Z-буфер треугольники
        matrix_pixels = add_triangle_to_Z_matrix(matrix_pixels, triangle_1, color, log_file)
        matrix_pixels = add_triangle_to_Z_matrix(matrix_pixels, triangle_2, color, log_file)
        # обводим квадратик
        draw_border_line(matrix_pixels, point1, point2, log_file)
        draw_border_line(matrix_pixels, point2, point3, log_file)
        draw_border_line(matrix_pixels, point3, point4, log_file)
        draw_border_line(matrix_pixels, point4, point1, log_file)

        i += 1

    log_file.close()

    # # Матрица для перемещения в центр координат
    # to_center = np.array([[1, 0, 0, 0],
    #                       [0, 1, 0, 0],
    #                       [0, 0, 1, 0],
    #                       [-X_CENTER, -Y_CENTER, -PLATE_Z - 5, 1]])

    # # Матрица для возвращения в исходные координаты
    # back_to_start = np.array([[1, 0, 0, 0],
    #                            [0, 1, 0, 0],
    #                            [0, 0, 1, 0],
    #                            [X_CENTER, Y_CENTER, PLATE_Z + 5, 1]])

    # # Итоговая матрица трансформации для точек
    # dot_trans_mat = np.dot(to_center, np.dot(trans_mat, back_to_start))
    
    # # Создание матриц для источника света
    # illum_dot_matrices = [np.dot(to_center, np.dot(scene.get_illuminant(i).get_trans_mat(), back_to_start))
    #                       for i in range(scene.get_illum_num())]


    return matrix_pixels