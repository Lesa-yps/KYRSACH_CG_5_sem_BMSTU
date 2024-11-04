import numpy as np

def z_buf_for_model(facets, vertices, trans_mat, color, scene, buf_width, buf_height):
    # Матрица для перемещения в центр координат
    to_center = np.array([[1, 0, 0, 0],
                          [0, 1, 0, 0],
                          [0, 0, 1, 0],
                          [-X_CENTER, -Y_CENTER, -PLATE_Z - 5, 1]])

    # Матрица для возвращения в исходные координаты
    back_to_start = np.array([[1, 0, 0, 0],
                               [0, 1, 0, 0],
                               [0, 0, 1, 0],
                               [X_CENTER, Y_CENTER, PLATE_Z + 5, 1]])

    # Итоговая матрица трансформации для точек
    dot_trans_mat = np.dot(to_center, np.dot(trans_mat, back_to_start))
    
    # Создание матриц для каждого источника света
    illum_dot_matrices = [np.dot(to_center, np.dot(scene.get_illuminant(i).get_trans_mat(), back_to_start))
                          for i in range(scene.get_illum_num())]

    # Проходим по всем граням модели
    for cur_face_num in range(len(facets)):
        dots_arr = [None] * 3  # Массив для хранения трех точек грани
        cur_dots = facets[cur_face_num].get_used_vertices()  # Получаем индексы вершин грани
        # Получаем координаты вершин
        dots_arr[0] = vertices[cur_dots[0]].get_position()
        dots_arr[1] = vertices[cur_dots[1]].get_position()
        dots_arr[2] = vertices[cur_dots[2]].get_position()

        # Формируем матрицу координат для точек
        coordinates_vec = np.array([[dots_arr[0].get_x_coordinate(), dots_arr[0].get_y_coordinate(), dots_arr[0].get_z_coordinate(), 1],
                                     [dots_arr[1].get_x_coordinate(), dots_arr[1].get_y_coordinate(), dots_arr[1].get_z_coordinate(), 1],
                                     [dots_arr[2].get_x_coordinate(), dots_arr[2].get_y_coordinate(), dots_arr[2].get_z_coordinate(), 1]])

        # Применяем трансформацию
        coordinates_vec = np.dot(coordinates_vec, dot_trans_mat)

        # Обновляем массив точек после трансформации
        for i in range(3):
            dots_arr[i] = Dot3D(coordinates_vec[i, 0], coordinates_vec[i, 1], coordinates_vec[i, 2])

        # Сортируем точки по координате Y (снизу вверх)
        dots_arr.sort(key=lambda dot: dot.get_y_coordinate())

        # Получаем округленные значения координат
        x1, x2, x3 = map(round, [dots_arr[0].get_x_coordinate(), dots_arr[1].get_x_coordinate(), dots_arr[2].get_x_coordinate()])
        z1, z2, z3 = [dot.get_z_coordinate() for dot in dots_arr]
        y1, y2, y3 = map(round, [dots_arr[0].get_y_coordinate(), dots_arr[1].get_y_coordinate(), dots_arr[2].get_y_coordinate()])

        # Основной цикл для нижней половины треугольника
        for cur_y in range(max(y1, 0), min(y2, buf_height - 1)):
            a_inc = (cur_y - y1) / (y2 - y1) if y1 != y2 else 0
            b_inc = (cur_y - y1) / (y3 - y1) if y1 != y3 else 0

            x_a = round(x1 + (x2 - x1) * a_inc)
            x_b = round(x1 + (x3 - x1) * b_inc)
            z_a = z1 + (z2 - z1) * a_inc
            z_b = z1 + (z3 - z1) * b_inc

            # Если x_a больше x_b, меняем их местами
            if x_a > x_b:
                x_a, x_b = x_b, x_a
                z_a, z_b = z_b, z_a

            # Ограничиваем границы по ширине буфера
            x_a = max(x_a, 0)
            x_b = min(x_b, buf_width - 1)

            # Проходим по всем пикселям в пределах границ
            for cur_x in range(x_a, x_b + 1):
                cur_z = z_a + (z_b - z_a) * (cur_x - x_a) / (x_b - x_a)

                # Проверяем, виден ли пиксель
                if cur_z >= depth_buffer[cur_x][cur_y]:
                    visible = 0  # Изначально не видимый
                    new_coordinates = np.array([[cur_x, cur_y, cur_z, 1]])

                    # Проверяем видимость для каждого источника света
                    for i in range(scene.get_illum_num()):
                        new_coordinates = np.dot(new_coordinates, illum_dot_matrices[i])
                        shadow_map = scene.get_illuminant(i).get_shadow_map()

                        x = round(new_coordinates[0, 0])
                        y = round(new_coordinates[0, 1])

                        # Проверка на наличие тени
                        if (0 <= x < len(shadow_map)) and (0 <= y < len(shadow_map[0])) and \
                                abs(shadow_map[x][y] - new_coordinates[0, 2]) < 2:
                            visible = 1  # Пиксель в тени
                            break

                    # Обновляем буфер глубины и цветовой буфер
                    depth_buffer[cur_x][cur_y] = cur_z
                    frame_buffer[cur_x][cur_y] = color + visible if scene.get_illum_num() > 0 else color + 1

        # Основной цикл для верхней половины треугольника
        for cur_y in range(max(y2, 0), min(y3, buf_height - 1) + 1):
            a_inc = (cur_y - y2) / (y3 - y2) if y2 != y3 else 0
            b_inc = (cur_y - y1) / (y3 - y1) if y1 != y3 else 0

            x_a = round(x2 + (x3 - x2) * a_inc)
            x_b = round(x1 + (x3 - x1) * b_inc)
            z_a = z2 + (z3 - z2) * a_inc
            z_b = z1 + (z3 - z1) * b_inc

            # Если x_a больше x_b, меняем их местами
            if x_a > x_b:
                x_a, x_b = x_b, x_a
                z_a, z_b = z_b, z_a

            # Ограничиваем границы по ширине буфера
            x_a = max(x_a, 0)
            x_b = min(x_b, buf_width - 1)

            # Проходим по всем пикселям в пределах границ
            for cur_x in range(x_a, x_b + 1):
                cur_z = z_a + (z_b - z_a) * (cur_x - x_a) / (x_b - x_a)

                # Проверяем, виден ли пиксель
                if cur_z >= depth_buffer[cur_x][cur_y]:
                    visible = 0  # Изначально не видимый
                    new_coordinates = np.array([[cur_x, cur_y, cur_z, 1]])

                    # Проверяем видимость для каждого источника света
                    for i in range(scene.get_illum_num()):
                        new_coordinates = np.dot(new_coordinates, illum_dot_matrices[i])
                        shadow_map = scene.get_illuminant(i).get_shadow_map()
                        x = round(new_coordinates[0, 0])
                        y = round(new_coordinates[0, 1])

                        # Проверка на наличие тени
                        if (0 <= x < len(shadow_map)) and (0 <= y < len(shadow_map[0])) and \
                                abs(shadow_map[x][y] - new_coordinates[0, 2]) < 2:
                            visible = 1  # Пиксель в тени
                            break

                    # Обновляем буфер глубины и цветовой буфер
                    depth_buffer[cur_x][cur_y] = cur_z
                    frame_buffer[cur_x][cur_y] = color + visible if scene.get_illum_num() > 0 else color + 1

        # Вызовы функции для отрисовки границ треугольника
        dda_borders_for_polygon(x1, y1, z1, x2, y2, z2)
        dda_borders_for_polygon(x1, y1, z1, x3, y3, z3)
        dda_borders_for_polygon(x2, y2, z2, x3, y3, z3)
