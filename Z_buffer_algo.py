from Point import Point
from Change_color import lighten_color

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
def draw_border_line(matrix_pixels, point1, point2, log_file, width_line = BORDER_WIDTH):
    # #log_file.write(f"   border row: {(point1.coords(), point2.coords())}\n")
    Xa, Ya, Za = point1.coords()
    Xb, Yb, Zb = point2.coords()
    dx, dy, dz = Xb - Xa, Yb - Ya, Zb - Za
    dmax = max(abs(dx), abs(dy), abs(dz))
    add_point_to_Z_matrix(matrix_pixels, point1, (BORDER_COLOR, BORDER_COLOR), log_file, width_line)
    if (dmax != 0):
        # шаг изменения по коодинатам
        dx, dy, dz = dx / dmax, dy / dmax, dz / dmax
        xi, yi, zi = Xa, Ya, Za
        i = 0
        while (i < dmax):
            xi, yi, zi = xi + dx, yi + dy, zi + dz
            add_point_to_Z_matrix(matrix_pixels, Point(xi, yi, zi), (BORDER_COLOR, BORDER_COLOR), log_file, width_line)
            i += 1
    return matrix_pixels


# Добавляем в Z-буфер точку с проверкой близости
def add_point_to_Z_matrix(matrix_pixels, point, color, log_file, size_point = 1):
    X, Y, Z = map(round, point.coords())
    # #log_file.write(f"     TRY TO DRAW POINT ({X}, {Y}, {Z}) into matrix n = {len(matrix_pixels)} m = {len(matrix_pixels[0])}")
    i = 0
    while Y < len(matrix_pixels) and X < len(matrix_pixels[0]) and X >= 0 and Y >= 0 and i < size_point:
        if matrix_pixels[Y][X][Z_PART] <= Z and not (matrix_pixels[Y][X][COLOR_PART][0] == BORDER_COLOR and matrix_pixels[Y][X][Z_PART] == Z):
            matrix_pixels[Y][X] = (Z, color)
            # #log_file.write(f" - DONE")
        X, Y, Z = X + 1, Y + 1, Z + 1
        i += 1
    # #log_file.write(f"\n")
    return matrix_pixels

# Добавляем в Z-буфер строку по у от point1 до point2 (по алгоритму рисования линии ЦДА) (y = const)
def add_row_to_Z_matrix(matrix_pixels, point1, point2, color, log_file):
    # #log_file.write(f"   row: {(point1.coords(), point2.coords())}\n")
    Xa, Xb, Y, Za, Zb = point1.x, point2.x, point1.y, point1.z, point2.z
    dx = Xb - Xa
    dz = Zb - Za
    dmax = max(abs(dx), abs(dz))
    add_point_to_Z_matrix(matrix_pixels, point1, color, log_file)
    if (abs(dmax) > 0.001):
        # шаг изменения по коодинатам
        dx /= dmax
        dz /= dmax
        xi, zi = Xa + dx, Za + dz
        while (abs(xi - Xa) <= dmax and abs(zi - Za) <= dmax):
            add_point_to_Z_matrix(matrix_pixels, Point(xi, Y, zi), color, log_file)
            xi += dx
            zi += dz
    return matrix_pixels


# Добавляем в Z-буфер треугольник
def add_triangle_to_Z_matrix(matrix_pixels, triangle, color, log_file):
    # сортируем точки по высоте (у)
    C, B, A = tuple(sorted(list(triangle), key=lambda point: point.y))
    log_file.write(f"Point{A.coords()}, Point{B.coords()}, Point{C.coords()}\n")
    y_min, y_max = C.y, A.y

    #draw_border_line(matrix_pixels, A, B, log_file)
    #draw_border_line(matrix_pixels, A, C, log_file)
    #draw_border_line(matrix_pixels, B, C, log_file)

    # вычисляем приращения (dx, dy, dz) вдоль сторон треугольника
    def compute_deltas(p1, p2):
        dy = p2.y - p1.y
        # eps для предотвращения деления на 0
        if abs(dy) >= 1:  
            dx = (p2.x - p1.x) / abs(dy)
            dz = (p2.z - p1.z) / abs(dy)
            #print(p1.coords(), p2.coords(), dy, p2.x - p1.x, dx, p2.z - p1.z, dz)
            return dx, dy, dz
        # Если dy почти 0, приращений нет
        return 0, 0, 0  

    dx_AC, dy_AC, dz_AC = compute_deltas(A, C)
    dx_AB, dy_AB, dz_AB = compute_deltas(A, B)
    dx_BC, dy_BC, dz_BC = compute_deltas(B, C)

    #print((f"   AC = {(dx_AC, -1, dz_AC)}, AB = {(dx_AB, -1, dz_AB)}, BC = {(dx_BC, -1, dz_BC)}\n"))
    # #log_file.write(f"   AC = {(dx_AC, -1, dz_AC)}, AB = {(dx_AB, -1, dz_AB)}, BC = {(dx_BC, -1, dz_BC)}\n")

    # Проходимся по всем строкам у
    point1 = Point(A.x, y_max, A.z) # одна из границ строки по у
    is_change_side = False
    # вторая граница строки по у
    if dy_AB == 0:
        point2 = Point(B.x, y_max, B.z)
        is_change_side = True
    else:
        point2 = Point(A.x, y_max, A.z) 
    while point1.y >= y_min:
        # обработка строки от point1 до point2
        matrix_pixels = add_row_to_Z_matrix(matrix_pixels, point1, point2, color, log_file)
        #print((f"        ROW: {point1.coords()} to {point2.coords()}\n"))
        #log_file.write(f"        ROW: {point1.coords()} to {point2.coords()}\n")

        if point2.y <= B.y:
            is_change_side = True
        
        if is_change_side:
            point2.add(dx_BC, -1, dz_BC)
        else:
            point2.add(dx_AB, -1, dz_AB)

        point1.add(dx_AC, -1, dz_AC)

    return matrix_pixels


# преобразования точек
def transform_plane_point(point1, offsets, dimensions, center_point, scale_coef, size_square, max_z, transform_matrix):
    # распаковка входных данных
    (dx_screen, dy_screen) = offsets
    (width_screen, height_screen) = dimensions
    # преобразуем координаты плоскости из "квадратовых" в мировые
    point1.multy(size_square).add(-dx_screen, -dy_screen, 0)
    #print("T", point1.coords())
    # разворачиваем у
    point1.y = - point1.y
    #print("T", point1.coords())
    # сдвиг в центр
    dx, dy, dz = center_point.coords()
    # добавляем поворот камеры и масштаб
    point1.add(-dx, -dy, -dz)
    point1 = transform_matrix.transform_point(point1, scale_coef)
    point1.add(dx, dy, dz)
    #print("T", point1.coords())
    # опускаем у
    point1.y += height_screen - 3
    #print("T", point1.coords())
    # преобразование координат с помощью ортогональной проекции
    point1 = point1.project(max_z)
    #print("T", point1.coords())
    return point1

# обратные преобразования точек
def anti_transform_plane_point(point1, offsets, dimensions, center_point, scale_coef, size_square, max_z, transform_matrix):
    # распаковка входных данных
    (dx_screen, dy_screen) = offsets
    (width_screen, height_screen) = dimensions
    # преобразование координат с помощью анти-ортогональной проекции
    point1 = point1.anti_project(max_z)
    #print("A", point1.coords())
    # поднимаем у
    point1.y -= height_screen - 3
    #print("A", point1.coords())
    # сдвиг в центр
    dx, dy, dz = center_point.coords()
    #  отнимаем камеры и масштаб
    point1.add(-dx, -dy, -dz)
    point1 = transform_matrix.anti_transform_point(point1, scale_coef)
    point1.add(dx, dy, dz)
    #print("A", point1.coords())
    # разворачиваем у
    point1.y = - point1.y
    #print("A", point1.coords())
    # преобразуем координаты плоскости из "квадратовых" в мировые
    point1.add(dx_screen, dy_screen, 0).multy(1/size_square)
    #print("A", point1.coords())
    return point1


# преобразования точек
def transform_plane_points(plane, params, transform_matrix, log_file):
    point1, point2, point3, point4, color = plane
    #log_file.write(f"was = {point1.coords()}")
    point1 = transform_plane_point(point1, *params, transform_matrix)
    #log_file.write(f" now = {point1.coords()}\n")
    point2 = transform_plane_point(point2, *params, transform_matrix)
    point3 = transform_plane_point(point3, *params, transform_matrix)
    point4 = transform_plane_point(point4, *params, transform_matrix)
    return point1, point2, point3, point4, color

# находим прямоугольную область, в которой находятся все плоскости
def calc_min_max_x_y(rect_x_y, plane):
    points = plane[:-1]
    for point in points:
        #print(point.coords(), rect_x_y)
        rect_x_y["max_x"] = max(rect_x_y["max_x"], round(point.x) + 1)
        rect_x_y["min_x"] = min(rect_x_y["min_x"], round(point.x) - 1)
        rect_x_y["max_y"] = max(rect_x_y["max_y"], round(point.y) + 1)
        rect_x_y["min_y"] = min(rect_x_y["min_y"], round(point.y) - 1)
        #print("-", point.coords(), rect_x_y)
    return rect_x_y


# Алгоритм Z-буфера для списка плоскостей
def Z_buffer_algo(list_planes, offsets, dimensions, center_point1, scale_coef, size_square, max_z, light_point, transform_matrix, log_filename):

    log_file = open(log_filename, "w")

    #log_file.write(f"{offsets, dimensions, center_point, scale_coef, size_square, max_z, transform_matrix}\n")

    # распаковка входных данных
    (dx_screen, dy_screen) = offsets
    (width_screen, height_screen) = dimensions

    # преобразуем координаты центра из "квадратовых" в мировые
    center_point = center_point1.copy()
    center_point.multy(size_square).add(-dx_screen, -dy_screen, 0)
    # разворачиваем у
    center_point.y = - center_point.y

    rect_x_y = {"max_x": float("-inf"), "max_y": float("-inf"), "min_x": float("+inf"), "min_y": float("+inf")}

    # сам алгоритм:
    # проходимся по всем плоскостям
    for i in range(len(list_planes)):
        # преобразования точек
        params = (offsets, dimensions, center_point, scale_coef, size_square, max_z)
        point1, point2, point3, point4, base_color = list_planes[i]
        # считаем интенсивность освещения для плоскости
        normal = calculate_normal(point1, point2, point3)
        diffuse_intensity = compute_diffuse_light(point1, normal, light_point)
        color = lighten_color(base_color, diffuse_intensity)
        #color = base_color
        list_planes[i] = (point1, point2, point3, point4, (base_color, color))
        #print(f"Plane {i}: Normal={normal}, DiffuseIntensity={diffuse_intensity}, BaseColor={base_color}, FinalColor={color}")
        list_planes[i] = transform_plane_points(list_planes[i], params, transform_matrix, log_file)
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
        #log_file.write(f"\ni = {i}\nPoints: {(point1.coords(), point2.coords(), point3.coords(), point4.coords())}\n")
        # Добавляем в Z-буфер треугольники
        matrix_pixels = add_triangle_to_Z_matrix(matrix_pixels, triangle_1, color, log_file)
        matrix_pixels = add_triangle_to_Z_matrix(matrix_pixels, triangle_2, color, log_file)
        # обводим квадратик
        draw_border_line(matrix_pixels, point1, point2, log_file)
        draw_border_line(matrix_pixels, point2, point3, log_file)
        draw_border_line(matrix_pixels, point3, point4, log_file)
        draw_border_line(matrix_pixels, point4, point1, log_file)

    log_file.close()

    return matrix_pixels, (rect_x_y["min_x"], rect_x_y["min_y"])