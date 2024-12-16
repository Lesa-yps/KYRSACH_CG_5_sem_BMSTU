import tkinter as tk
from tkinter import messagebox
from concurrent.futures import ProcessPoolExecutor
import time as t

from Objects import Objects
from Point import Point, DEF_MAX_Z
from Z_buffer_algo import Z_buffer_algo, COLOR_PART, Z_PART, anti_transform_plane_point, transform_plane_point
from Matrix import Matrix
from Change_color import darken_color

DEF_SIZE_SQARES = 30 # Размер одного квадрата
DEF_COUNT_SQARES = 20 # Количество квадратов пола по-умолчанию

# с этим уже общается пользователь (ну, правда надо несколько функций сделать приватными, а так... почему нет?;)

# внимание! тени на невидимых гранях объектов это тоже, что бы человек смотрел на
# эти объекты! теневая грань будет невидима! можно переиспользовать алгоритм Z-буфера!


# Фасад
class Scene:

    def __init__(self, canvas):
        self.objects = Objects()
        self.canvas = canvas
        # координаты источника света по х, y и z
        self.point_light = Point(0, 0, 100000)
        # координаты зрителя
        self.point_look = Point(0, 0, DEF_MAX_Z)
        # пол
        self.create_floor()
        # матрица поворотов
        self.transform_matrix = Matrix()
        # матрица поворотов источника света
        self.transform_matrix_light = Matrix()
        # Переменные определяющие расположение/состояние окна
        self.SIDE_PLACE = 0  # переменная для определения сдвига в стороне
        self.HEIGHT_PLACE = 0  # переменная для определения сдвига по высоте
        # коэффициент приближения
        self.ZOOM = 1

    # отрисовывает начальную сцену (зачищая все объекты) с полом DEF_COUNT_SQARES x DEF_COUNT_SQARES
    def start_scene(self):
        self.start_scene_not_redraw()
        self.draw_scene()
    
    # возвращает сцену в начальное состояние (зачищая все объекты) с полом DEF_COUNT_SQARES x DEF_COUNT_SQARES
    def start_scene_not_redraw(self):
        self.objects.clear()
        # координаты источника света по х, y и z
        self.point_light = Point(0, 0, 100000)
        # координаты зрителя
        self.point_look = (0, 0, DEF_MAX_Z)
        # пол
        self.create_floor()
        # коэффициент приближения
        self.ZOOM = 1
        self.SIDE_PLACE = 0 
        self.HEIGHT_PLACE = 0
        # возвращаем матрицу преобразований в стартовое состояние
        self.transform_matrix.make_one()
        self.transform_matrix_light.make_one()
        self.canvas.delete("all")

    # Задаёт новые количество клеточек и цвет "пола" и высчитывает координаты всех его клеточек
    def create_floor(self, num_squares_x = DEF_COUNT_SQARES, num_squares_y = DEF_COUNT_SQARES, scene_color = "#cccccc"):
        self.floor_num_squares = (num_squares_x, num_squares_y)
        self.floor_color = scene_color

    # Высчитывает координаты всех квадратиков пола
    def create_floor_coords(self):
        num_squares_x, num_squares_y = self.floor_num_squares
        floor_coords = []
        for i in range(num_squares_x):
            for j in range(num_squares_y):
                x1, y1 = i, j
                x2, y2 = x1 + 1, y1 + 1
                floor_coords.append((Point(x1, y1, 0), Point(x1, y2, 0), Point(x2, y2, 0), Point(x2, y1, 0), self.floor_color))
        return floor_coords, Point(num_squares_x / 2, num_squares_y / 2, 0)
        
    # Возвращает число клеточек на полу (х и у)
    def take_floor_num_squares(self):
        return self.floor_num_squares


    # Вычисляет координаты видимого пользователю экрана (размеры и смещения)
    def calc_coords_screen(self):
        # Получаем ширину и высоту canvas
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        return (width, height)

    # преобразуем координаты x, y, z из вида наблюдателя в координаты из вида источника света
    def transform_to_light_view(self, point, params):
        offsets, dimensions, center_point1, scale_coef, size_square, max_z = params
        center_point = center_point1.copy()
        center_point.multy(size_square).add(-offsets[0], -offsets[1], 0)
        # разворачиваем у
        center_point.y = - center_point.y
        #center_point = transform_plane_point(center_point1.copy(), offsets, dimensions, None, scale_coef, size_square, max_z, self.transform_matrix)
        #center_point_light = transform_plane_point(center_point1.copy(), offsets, dimensions, None, scale_coef, size_square, max_z, self.transform_matrix_light)
        # преобразуем точку из системы координат наблюдателя в мировую систему координат
        point_world = anti_transform_plane_point(point, offsets, dimensions, center_point, scale_coef, size_square, max_z, self.transform_matrix)
        #print(f"    point_world {round(point_world.x), round(point_world.y), round(point_world.z)}")
        # преобразуем точку из мировой системы координат в систему координат источника света
        point_light = transform_plane_point(point_world, offsets, dimensions, center_point, scale_coef, size_square, max_z, self.transform_matrix_light)
        return point_light.coords()

    # наложение матрицы теней на основную матрицу
    def combo_matrix(self, matrix, d_x_y, matrix_light, d_x_y_light, params):
        #print("Matrix", self.transform_matrix.print_matrix(), self.transform_matrix_light.print_matrix(), sep = "\n")
        #print("\nT-matrix:", self.transform_matrix.print_matrix())
        #print("T-matrix light:", self.transform_matrix_light.print_matrix())
        # проходимся по всей матрице наблюдателя
        #print("\nMatrix:", '\n'.join(' '.join(map(str, row)) for row in matrix))
        #print("LIGHT Matrix:", '\n'.join(' '.join(map(str, row)) for row in matrix_light))
        for y in range(len(matrix)):
            for x in range(len(matrix[0])):
                # глубина текущей точки наблюдателя
                z = matrix[y][x][Z_PART]
                base_color, color = matrix[y][x][COLOR_PART]
                matrix[y][x] = (z, color)
                if z == float("-inf"):
                    continue
                new_x = x + d_x_y[0]
                new_y = y + d_x_y[1]
                # координаты точки x, y, z из вида наблюдателя линейно преобразуются в координаты x', y', z' на виде из источника света
                x_light, y_light, z_light = self.transform_to_light_view(Point(new_x, new_y, z), params)
                x_light -= d_x_y_light[0]
                y_light -= d_x_y_light[1]
                if (x_light == float("-inf")) or (y_light == float("-inf")):
                    #print(f"Infinity point: {x_light}, {y_light}")
                    continue
                #print((y, x, z), "->", (round(y_light), round(x_light), z_light))
                x_light, y_light = round(x_light), round(y_light)
                if not (0 <= x_light < len(matrix_light[0]) and 0 <= y_light < len(matrix_light)):
                    #print(f"Out of bounds: {x_light}, {y_light}")
                    continue
               
                z_light_matrix = matrix_light[y_light][x_light][Z_PART]
                if z_light + 5 < z_light_matrix:
                    #print(f"Shadow added at y = {y}, x = {x} with z_light={z_light}, z_light_matrix={z_light_matrix}")
                    # затеняем пиксель
                    matrix[y][x] = (matrix[y][x][Z_PART], darken_color(base_color, 0.8))
                    #print("тень")
                    #if (z_light_matrix == float("-inf")):
                    #    #print(".", end = "")
        #print("RES Matrix:", '\n'.join(' '.join(map(str, row)) for row in matrix))
        return matrix
    
    # отрисовка готовой матрицы с подсчетом закрашенных клеток и времени работы
    def draw_matrix(self, matrix, dx_start_draw, dy_start_draw):
        # таймер
        start_time = t.time()
        # счетчик закрашенных клеток
        filled_cells = 0
        for y, row in enumerate(matrix):
            for x, elem in enumerate(row):
                color = elem[COLOR_PART]
                if color:
                    # отрисовка закрашенной клетки
                    xi = dx_start_draw + x
                    yi = dy_start_draw + y
                    self.canvas.create_rectangle(xi, yi, xi + 1, yi + 1, outline=color, fill=color)
                    filled_cells += 1
        end_time = t.time()
        elapsed_time = end_time - start_time
        # Вывод числа закрашенных клеток и времени работы в командную строку
        print(f"\nВремя закраски {filled_cells} клеток = {elapsed_time:.4f} секунд")


    # получение списка плоскостей с цветами
    def calc_list_planes(self):
        return self.objects.calc_list_planes()
    
    # вычисляет матрицу пикселей (Z-буфер) для экрана
    def calc_pixel_matrix(self, params_Z_buffer, is_parallel = True):
        if is_parallel:
            # расчет matrix и matrix_light параллельно
            with ProcessPoolExecutor() as executor:
                # алгоритм z буфера для рисования плоскостей
                future_matrix = executor.submit(Z_buffer_algo, *params_Z_buffer, self.transform_matrix, "log_file_Z.txt")
                # алгоритм Z буффера для добавления теней
                future_matrix_light = executor.submit(Z_buffer_algo, *params_Z_buffer,  self.transform_matrix_light, "log_file_Z_light.txt")
                # получение результатов из будущих объектов
                matrix, d_x_y = future_matrix.result()
                matrix_light, d_x_y_light = future_matrix_light.result()
        else:
            # алгоритм z буфера для рисования плоскостей
            matrix, d_x_y = Z_buffer_algo(*params_Z_buffer, self.transform_matrix, "log_file_Z.txt")
            # алгоритм Z буффера для добавления теней
            matrix_light, d_x_y_light = Z_buffer_algo(*params_Z_buffer,  self.transform_matrix_light, "log_file_Z_light.txt")
        #print("---\n", matrix, "\n", matrix_light)
        # наложение матрицы теней на основную матрицу
        matrix_res = self.combo_matrix(matrix, d_x_y, matrix_light, d_x_y_light, params_Z_buffer[1:-1])
        return matrix_res, d_x_y

    # зарисовка всех объектов сцены
    def draw_scene(self, is_draw = True, is_parallel = True):
        print('     draw_scene!', self.transform_matrix.print_matrix())
        (width, height) = self.calc_coords_screen()
        # получение списка плоскостей с цветами
        list_planes = self.calc_list_planes()
        # добавляем плоскости к полу
        floor_planes, center_point = self.create_floor_coords()
        list_planes += floor_planes
        point_light = self.transform_matrix_light.transform_point(self.point_light)
        print((self.SIDE_PLACE, self.HEIGHT_PLACE), (width, height), center_point.coords(), self.ZOOM, DEF_SIZE_SQARES, DEF_MAX_Z, point_light.coords())
        params_Z_buffer = (list_planes, (self.SIDE_PLACE, self.HEIGHT_PLACE), (width, height), center_point, self.ZOOM, DEF_SIZE_SQARES, DEF_MAX_Z, point_light)
        # вычисляет матрицу пикселей (Z-буфер) для экрана
        print("TYT")
        print("list_planes", [(i1.coords(), i2.coords(), i3.coords(), i4.coords(), color) for (i1, i2, i3, i4, color) in list_planes])
        matrix, d_x_y = self.calc_pixel_matrix(params_Z_buffer, is_parallel)
        # отрисовка готовой матрицы (время работы выводится в командную строку)
        if is_draw:
            self.draw_matrix(matrix, self.SIDE_PLACE + d_x_y[0], self.HEIGHT_PLACE + d_x_y[1])

    # перерисовка всех объектов сцены
    def redraw_scene(self):
        self.canvas.delete("all")
        self.draw_scene()

    # Проверка пересечений координат переданного объекта с уже существующими
    def check_intersection(self, entry_arr):
        rc = False
        width, _, length, offset_x, offset_y = entry_arr
        scene_x, scene_y = self.take_floor_num_squares()
        if width + offset_x > scene_x or length + offset_y > scene_y:
            messagebox.showerror("Ошибка", "Обнаружен выход за границы сцены.")
            rc = True
        else:
            matrix = self.objects.make_busy_matrix(scene_x, scene_y)
            for y in range(offset_y, length + offset_y):
                for x in range(offset_x, width + offset_x):
                    if matrix[y][x]:
                        messagebox.showerror("Ошибка", f"Обнаружено пересечение ({x}, {y}). Измените размеры или позицию.")
                        rc = True
                        break
                if rc:
                    break
        return rc
    
    # Удаляем объект по частичным данным из таблицы
    def delele_object(self, new_item_data):
        type, data = new_item_data[0], new_item_data[1:]
        if type == "стена":
            self.objects.del_wall(data)
        elif type == "дверь":
            self.objects.del_door(data)
        elif type == "окно":
            self.objects.del_window(data)
        self.redraw_scene()

    # Добавляем объект
    def add_object(self, type, params, is_redraw = True):
        if type == "стена":
            self.objects.add_wall(params)
        elif type == "дверь":
            self.objects.add_door(params)
        elif type == "окно":
            self.objects.add_window(params)
        if is_redraw:
            self.redraw_scene()

    # Получаем все данные объекта по частичным данным из таблицы (получаем словарь object_data_all["type"], object_data_all["color"], object_data_all["sizes"])
    def take_data_object(self, new_item_data):
        object_data_all = self.objects.take_dict_params(new_item_data)
        return object_data_all

    # Выгрузить сцену в файл (дан путь к файлу)
    def upload_scene(self, file_path):
        try:
            with open(file_path, "w") as file:
                # Запись данных о сцене
                file.write(f"сцена {self.floor_color} {self.floor_num_squares[0]} {self.floor_num_squares[1]}\n")
                # Вызов функции выгрузки данных у self.objects и запись этих данных
                self.objects.upload_data(file)
                messagebox.showinfo("Успех", f"Сцена успешно выгружена в файл {file_path}!")          
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выгрузить сцену: {e}")

    def change_floor(self, new_width, new_height, new_color):
        rc = True
        old_width, old_height = self.floor_num_squares
        # #print(old_width, new_width, old_height, new_height, self.floor_color, new_color)
        if old_width != new_width or old_height != new_height or self.floor_color != new_color:
            if new_width < old_width or new_height < old_height:
                matrix = self.objects.make_busy_matrix(old_width, old_height)
                for x in range(old_height):
                    for y in range(old_width):
                        if matrix[x][y] and (x >= new_width or y >= new_height):
                            messagebox.showerror("Ошибка", f"Освободите удаляемые клетки! {(x, y)}")
                            rc = False
                            break
                    if not rc:
                        break
            # #print("change_floor")
            if rc:
                self.create_floor(new_width, new_height, new_color)
                self.redraw_scene()
        return rc

    # изменение переменных, определяющих расположение/состояние окна
    def multy_zoom(self, coef):
        self.ZOOM *= coef
    def add_side_place(self, place):
        self.SIDE_PLACE += place
    def add_height_place(self, place):
        self.HEIGHT_PLACE += place
    
    # ПОВОРОТЫ КАМЕРЫ

    # Ворочает камеру
    def rotate_camera(self, text, angle):
        if angle == 0:
            return
        self.transform_matrix.rotate_axis(text, angle)
        # self.transform_matrix.print_matrix()
        self.redraw_scene()

    # Ворочает свет
    def rotate_light(self, text, angle):
        if angle == 0:
            return
        self.transform_matrix_light.rotate_axis(text, angle)
        self.redraw_scene()

    
        






# Пример использования класса Parallelepiped
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Сцена (объекты + свет + пол)")

    canvas = tk.Canvas(root, width=800, height=600, bg="white")
    canvas.pack()

    scene = Scene(canvas)

    scene.add_wall(((Point(100, 100, 100), Point(300, 300, 300)), None, "yellow", "pink"))
    scene.add_window(((Point(150, 150, 150), Point(400, 400, 400)),))
    scene.add_door(((Point(500, 500, 500), Point(600, 600, 600)),))

    root.mainloop()