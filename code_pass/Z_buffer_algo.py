from Point import Point
from Change_color import lighten_color

# алгоритм реализующий Z-буфер
# на вход: кортеж - смещение экрана по х и у, кортеж - ширина и высота экрана +
# + массив из кортежей: 4 точки - координаты плоскости (расположены в порядке обхода по кругу) + цвет
# на выход: матрица пикселей - глубины и цветов

COORD_Z = 0
# в матрице
Z_PART = 0
COLOR_PART = 1

FON_COLOR = None
BORDER_COLOR = "#000000"    
BORDER_WIDTH = 2

# вычисляет диффузное освещение
def compute_diffuse_light(point, normal, light_source, light_intensity=0.9, k_d=0.3):
    # вектор к источнику света
    light_vector = Point(
        light_source.x - point.x,
        light_source.y - point.y,
        light_source.z - point.z
    ).normalize()
    # угол между нормалью и направлением света
    cos_theta = max(0, normal.dot(light_vector))
    # итоговая интенсивность цвета
    intensity = k_d * light_intensity * cos_theta
    return intensity

# рассчитывает нормаль к плоскости
def calculate_normal(p1, p2, p3):
    # векторы на гранях
    v1 = Point(p2.x - p1.x, p2.y - p1.y, p2.z - p1.z)
    v2 = Point(p3.x - p1.x, p3.y - p1.y, p3.z - p1.z)
    # векторное произведение
    normal = v1.cross(v2).normalize()
    return normal



# Рисуем граничную линию
def draw_border_line(matrix_pixels, point1, point2, width_line = BORDER_WIDTH):
    Xa, Ya, Za = point1.coords()
    Xb, Yb, Zb = point2.coords()
    dx, dy, dz = Xb - Xa, Yb - Ya, Zb - Za
    dmax = max(abs(dx), abs(dy), abs(dz))
    add_point_to_Z_matrix(matrix_pixels, point1, (BORDER_COLOR, BORDER_COLOR), width_line)
    if (dmax != 0):
        # шаг изменения по коодинатам
        dx, dy, dz = dx / dmax, dy / dmax, dz / dmax
        xi, yi, zi = Xa, Ya, Za
        i = 0
        while (i < dmax):
            xi, yi, zi = xi + dx, yi + dy, zi + dz
            add_point_to_Z_matrix(matrix_pixels, Point(xi, yi, zi), (BORDER_COLOR, BORDER_COLOR), width_line)
            i += 1
    return matrix_pixels


# Добавляем в Z-буфер точку с проверкой близости
def add_point_to_Z_matrix(matrix_pixels, point, color, size_point = 1):
    X, Y, Z = map(round, point.coords())
    i = 0
    while Y < len(matrix_pixels) and X < len(matrix_pixels[0]) and X >= 0 and Y >= 0 and i < size_point:
        if matrix_pixels[Y][X][Z_PART] <= Z and not (matrix_pixels[Y][X][COLOR_PART][0] == BORDER_COLOR and abs(matrix_pixels[Y][X][Z_PART] - Z) < 5):
            matrix_pixels[Y][X] = (Z, color)
        X, Y, Z = X + 1, Y + 1, Z + 1
        i += 1
    return matrix_pixels

# Добавляем в Z-буфер строку по у от point1 до point2 (по алгоритму рисования линии ЦДА) (y = const)
def add_row_to_Z_matrix(matrix_pixels, point1, point2, color):
    Xa, Xb, Y, Za, Zb = point1.x, point2.x, point1.y, point1.z, point2.z
    dx = Xb - Xa
    dz = Zb - Za
    dmax = max(abs(dx), abs(dz))
    add_point_to_Z_matrix(matrix_pixels, point1, color)
    if (abs(dmax) > 0.001):
        # шаг изменения по коодинатам
        dx /= dmax
        dz /= dmax
        xi, zi = Xa + dx, Za + dz
        while (abs(xi - Xa) <= dmax and abs(zi - Za) <= dmax):
            add_point_to_Z_matrix(matrix_pixels, Point(xi, Y, zi), color)
            xi += dx
            zi += dz
    return matrix_pixels


# Добавляем в Z-буфер треугольник
def add_triangle_to_Z_matrix(matrix_pixels, triangle, color):
    # сортируем точки по высоте (у)
    C, B, A = tuple(sorted(list(triangle), key=lambda point: point.y))
    y_min, y_max = C.y, A.y

    #draw_border_line(matrix_pixels, A, B)
    #draw_border_line(matrix_pixels, A, C)
    #draw_border_line(matrix_pixels, B, C)

    # вычисляем приращения (dx, dy, dz) вдоль сторон треугольника
    def compute_deltas(p1, p2):
        dy = p2.y - p1.y
        # eps для предотвращения деления на 0
        if abs(dy) >= 1: 
            dx = (p2.x - p1.x) / abs(dy)
            dz = (p2.z - p1.z) / abs(dy)
            return dx, dy, dz
        # Если dy почти 0, приращений нет
        return 0, 0, 0  

    dx_AC, _, dz_AC = compute_deltas(A, C)
    dx_AB, dy_AB, dz_AB = compute_deltas(A, B)
    dx_BC, _, dz_BC = compute_deltas(B, C)

    # Проходимся по всем строкам у
    point1 = Point(A.x, y_max, A.z) # одна из границ строки по у
    # вторая граница строки по у
    if abs(dy_AB) < 0.001:
        point2 = Point(B.x, y_max, B.z)
        is_change_side = True
    else:
        point2 = Point(A.x, y_max, A.z)
        is_change_side = False

    diff_p2B = point2.y - B.y
    while not is_change_side and not (diff_p2B < 0.001):
        # обработка строки от point1 до point2
        matrix_pixels = add_row_to_Z_matrix(matrix_pixels, point1, point2, color)
        if diff_p2B < 1:
            point2.add(dx_AB * diff_p2B, -diff_p2B, dz_AB * diff_p2B)
            point1.add(dx_AC * diff_p2B, -diff_p2B, dz_AC * diff_p2B)
        else:
            point2.add(dx_AB, -1, dz_AB)
            point1.add(dx_AC, -1, dz_AC)
        diff_p2B = point2.y - B.y

    diff_p1min = point1.y - y_min
    while not diff_p1min < 0.001:
        # обработка строки от point1 до point2
        matrix_pixels = add_row_to_Z_matrix(matrix_pixels, point1, point2, color)
        if diff_p1min < 1:
            point2.add(dx_BC * diff_p1min, -diff_p1min, dz_BC * diff_p1min)
            point1.add(dx_AC * diff_p1min, -diff_p1min, dz_AC * diff_p1min)
        else:
            point2.add(dx_BC, -1, dz_BC)
            point1.add(dx_AC, -1, dz_AC)
        diff_p1min = point1.y - y_min

    return matrix_pixels


# преобразования точек
def transform_plane_point(point1, offsets, dimensions, center_point, scale_coef, size_square, max_z, transform_matrix):
    # распаковка входных данных
    (dx_screen, dy_screen) = offsets
    (_, height_screen) = dimensions
    # преобразуем координаты плоскости из "квадратовых" в мировые
    point1.multy(size_square).add(-dx_screen, -dy_screen, 0)
    # разворачиваем у
    point1.y = - point1.y
    # сдвиг в центр
    dx, dy, dz = center_point.coords()
    # добавляем поворот камеры и масштаб
    point1.add(-dx, -dy, -dz)
    point1 = transform_matrix.transform_point(point1, scale_coef)
    point1.add(dx, dy, dz)
    # опускаем у
    point1.y += height_screen - 3
    # преобразование координат с помощью ортогональной проекции
    point1 = point1.project(max_z)
    return point1

# обратные преобразования точек
def anti_transform_plane_point(point1, offsets, dimensions, center_point, scale_coef, size_square, max_z, transform_matrix):
    # распаковка входных данных
    (dx_screen, dy_screen) = offsets
    (_, height_screen) = dimensions
    # преобразование координат с помощью анти-ортогональной проекции
    point1 = point1.anti_project(max_z)
    # поднимаем у
    point1.y -= height_screen - 3
    # сдвиг в центр
    dx, dy, dz = center_point.coords()
    #  отнимаем камеры и масштаб
    point1.add(-dx, -dy, -dz)
    point1 = transform_matrix.anti_transform_point(point1, scale_coef)
    point1.add(dx, dy, dz)
    # разворачиваем у
    point1.y = - point1.y
    # преобразуем координаты плоскости из "квадратовых" в мировые
    point1.add(dx_screen, dy_screen, 0).multy(1/size_square)
    return point1


# преобразования точек
def transform_plane_points(plane, params, transform_matrix):
    point1, point2, point3, point4, color = plane
    point1 = transform_plane_point(point1, *params, transform_matrix)
    point2 = transform_plane_point(point2, *params, transform_matrix)
    point3 = transform_plane_point(point3, *params, transform_matrix)
    point4 = transform_plane_point(point4, *params, transform_matrix)
    return point1, point2, point3, point4, color

# находим прямоугольную область, в которой находятся все плоскости
def calc_min_max_x_y(rect_x_y, plane):
    points = plane[:-1]
    for point in points:
        rect_x_y["max_x"] = max(rect_x_y["max_x"], round(point.x) + 1)
        rect_x_y["min_x"] = min(rect_x_y["min_x"], round(point.x) - 1)
        rect_x_y["max_y"] = max(rect_x_y["max_y"], round(point.y) + 1)
        rect_x_y["min_y"] = min(rect_x_y["min_y"], round(point.y) - 1)
    return rect_x_y


# Алгоритм Z-буфера для списка плоскостей
def Z_buffer_algo(list_planes_old, offsets, dimensions, center_point1, scale_coef, size_square, max_z, light_point, transform_matrix):

    # распаковка входных данных
    (dx_screen, dy_screen) = offsets

    # преобразуем координаты центра из "квадратовых" в мировые
    center_point = center_point1.copy()
    center_point.multy(size_square).add(-dx_screen, -dy_screen, 0)
    # разворачиваем у
    center_point.y = - center_point.y

    rect_x_y = {"max_x": float("-inf"), "max_y": float("-inf"), "min_x": float("+inf"), "min_y": float("+inf")}
    list_planes = list()

    # сам алгоритм:
    # проходимся по всем плоскостям
    for i in range(len(list_planes_old)):
        # преобразования точек
        params = (offsets, dimensions, center_point, scale_coef, size_square, max_z)
        point1, point2, point3, point4, base_color = list_planes_old[i]
        # считаем интенсивность освещения для плоскости
        normal = calculate_normal(point1, point2, point3)
        diffuse_intensity = compute_diffuse_light(point1, normal, light_point)
        color = lighten_color(base_color, diffuse_intensity)
        #color = base_color
        new_plane = (point1, point2, point3, point4, (base_color, color))
        list_planes.append(transform_plane_points(new_plane, params, transform_matrix))
        rect_x_y = calc_min_max_x_y(rect_x_y, list_planes[i])

    # матрица кортежей (буфер кадра - фоновое значение, Z-буфер - минус бесконечность)
    matrix_pixels = [[(float('-inf'), (FON_COLOR, FON_COLOR)) for _ in range(rect_x_y["max_x"] - rect_x_y["min_x"] + 1)] for _ in range(rect_x_y["max_y"] - rect_x_y["min_y"] + 1)]
        
    for plane in list_planes:
        point1, point2, point3, point4, color = plane
        point1.add(-rect_x_y["min_x"], -rect_x_y["min_y"], 0), point2.add(-rect_x_y["min_x"], -rect_x_y["min_y"], 0)
        point3.add(-rect_x_y["min_x"], -rect_x_y["min_y"], 0), point4.add(-rect_x_y["min_x"], -rect_x_y["min_y"], 0)
        # разделим каждую квадрат-плоскость на 2 треугольника для упрощения
        triangle_1 = (point1, point2, point3)
        triangle_2 = (point3, point4, point1)
        # Запись треугольников в лог-файл
        # Добавляем в Z-буфер треугольники
        matrix_pixels = add_triangle_to_Z_matrix(matrix_pixels, triangle_1, color)
        matrix_pixels = add_triangle_to_Z_matrix(matrix_pixels, triangle_2, color)
        # обводим квадратик
        draw_border_line(matrix_pixels, point1, point2,)
        draw_border_line(matrix_pixels, point2, point3)
        draw_border_line(matrix_pixels, point3, point4)
        draw_border_line(matrix_pixels, point4, point1)

    return matrix_pixels, (rect_x_y["min_x"], rect_x_y["min_y"])