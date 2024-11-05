import tkinter as tk
from tkinter import messagebox
from concurrent.futures import ProcessPoolExecutor
import time as t
import numpy as np

from Objects import Objects
from Point import Point, DEF_MAX_Z
from Z_buffer_algo import Z_buffer_algo, COLOR_PART, Z_PART
from Matrix import Matrix
from Change_color import darken_color

DEF_SIZE_SQARES = 30 # Размер одного квадрата
DEF_COUNT_SQARES = 20 # Количество квадратов пола по-умолчанию
EPS = 0.1

# с этим уже общается пользователь (ну, правда надо несколько функций сделать приватными, а так... почему нет?;)

# внимание! тени на невидимых гранях объектов это тоже, что бы человек смотрел на
# эти объекты! теневая грань будет невидима! можно переиспользовать алгоритм Z-буфера!


# Фасад
class Scene:

    def __init__(self, canvas):
        self.objects = Objects()
        self.canvas = canvas
        # координаты источника света по х, y и z
        self.light = (0, 0, DEF_MAX_Z)
        # координаты зрителя
        self.point_look = (0, 0, DEF_MAX_Z)
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
        self.objects.clear()
        # координаты источника света по х, y и z
        self.light = (0, 0, DEF_MAX_Z)
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
        self.redraw_scene()

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

    # алгоритм Z-буфера для рисования плоскостей
    def calc_draw_objects_Z_bufer(self, offsets, dimensions, list_planes, center_point):
        return Z_buffer_algo(offsets, dimensions, list_planes, self.transform_matrix, center_point, self.ZOOM, DEF_SIZE_SQARES, DEF_MAX_Z, "log_file_Z.txt")

    # алгоритм Z буффера для добавления теней (то же что и обычный Z-буфер, только наблюдатель помещается в местоположение источника света)
    def calc_draw_objects_Z_bufer_light(self, offsets, dimensions, list_planes, center_point):
        return Z_buffer_algo(offsets, dimensions, list_planes, self.transform_matrix_light, center_point, self.ZOOM, DEF_SIZE_SQARES, DEF_MAX_Z,  "log_file_Z_light.txt")


    # Вычисляет координаты видимого пользователю экрана (размеры и смещения)
    def calc_coords_screen(self):
        # Получаем ширину и высоту canvas
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        return (width, height)

    # преобразуем координаты x, y, z из вида наблюдателя в координаты из вида источника света
    def transform_to_light_view(self, x, y, z):
        point = np.array([x, y, z, 1])
        # преобразуем точку из системы координат наблюдателя в мировую систему координат
        point_world = np.dot(self.transform_matrix.get_inverse_matrix(), point)
        # преобразуем точку из мировой системы координат в систему координат источника света
        point_light = np.dot(self.transform_matrix_light.matrix, point_world)
        x_light, y_light, z_light = [float(i) for i in point_light[:3]]
        return x_light, y_light, z_light

    # наложение матрицы теней на основную матрицу
    def combo_matrix(self, matrix, matrix_light):
        # проходимся по всей матрице наблюдателя
        for y in range(len(matrix)):
            for x in range(len(matrix[0])):
                # глубина текущей точки наблюдателя
                z = matrix[y][x][Z_PART]
                if z == float("-inf"):
                    continue
                # координаты точки x, y, z из вида наблюдателя линейно преобразуются в координаты x', y', z' на виде из источника света
                x_light, y_light, z_light = self.transform_to_light_view(x, y, z)
                # oкругляем x и y для индексации
                x_light, y_light = int(x_light), int(y_light)
                # проверяем границы
                if 0 <= y_light < len(matrix_light) and 0 <= x_light < len(matrix_light[0]):
                    z_light = matrix_light[y_light][x_light][Z_PART]
                    # проверка на нахождение в тени (глубина в наблюдателе больше глубины из источника + EPS)
                    if z > z_light + EPS:
                        # затеняем пиксель
                        matrix[y][x] = (matrix[y][x][Z_PART], darken_color(matrix[y][x][COLOR_PART], 0.8))
                        # print(".", end = "")
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
        

    # Зарисовка всех объектов сцены
    def draw_scene(self):
        (width, height) = self.calc_coords_screen()
        # print((self.ZOOM, self.SIDE_PLACE, self.HEIGHT_PLACE), (width, height))
        # получение списка плоскостей с цветами
        list_planes = self.calc_list_planes()
        # добавляем плоскости к полу
        floor_planes, center_point = self.create_floor_coords()
        list_planes += floor_planes
        # print(f"size of list_planes matrix = {len(list_planes)}")
        params_Z_buffer = (self.SIDE_PLACE, self.HEIGHT_PLACE), (width, height), list_planes, center_point
        # расчет matrix и matrix_light параллельно
        with ProcessPoolExecutor() as executor:
            # алгоритм z буфера для рисования плоскостей
            future_matrix = executor.submit(Z_buffer_algo, (self.SIDE_PLACE, self.HEIGHT_PLACE), (width, height), list_planes, self.transform_matrix, center_point, self.ZOOM, DEF_SIZE_SQARES, DEF_MAX_Z, "log_file_Z.txt")
            # алгоритм Z буффера для добавления теней
            future_matrix_light = executor.submit(Z_buffer_algo, (self.SIDE_PLACE, self.HEIGHT_PLACE), (width, height), list_planes, self.transform_matrix_light, center_point, self.ZOOM, DEF_SIZE_SQARES, DEF_MAX_Z,  "log_file_Z_light.txt")
            # получение результатов из будущих объектов
            matrix = future_matrix.result()
            matrix_light = future_matrix_light.result()
        # наложение матрицы теней на основную матрицу
        matrix = self.combo_matrix(matrix, matrix_light)
        # отрисовка готовой матрицы (время работы выводится в командную строку)
        self.draw_matrix(matrix, self.SIDE_PLACE, self.HEIGHT_PLACE)

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
    def add_object(self, type, params):
        if type == "стена":
            self.objects.add_wall(params)
        elif type == "дверь":
            self.objects.add_door(params)
        elif type == "окно":
            self.objects.add_window(params)
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
        # print(old_width, new_width, old_height, new_height, self.floor_color, new_color)
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
            # print("change_floor")
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