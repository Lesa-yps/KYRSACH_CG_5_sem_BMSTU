import tkinter as tk
from tkinter import messagebox
import time as t

from Objects import Objects
from Point import Point, DEF_MAX_Z
from Z_buffer_algo import Z_buffer_algo, COLOR_PART

DEF_SIZE_SQARES = 40 # Размер одного квадрата
DEF_COUNT_SQARES = 10 # Количество квадратов пола по-умолчанию

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

    # отрисовывает начальную сцену (зачищая все объекты) с полом DEF_COUNT_SQARES x DEF_COUNT_SQARES
    def start_scene(self):
        self.objects.clear()
        # координаты источника света по х, y и z
        self.light = (0, 0, DEF_MAX_Z)
        # координаты зрителя
        self.point_look = (0, 0, DEF_MAX_Z)
        # пол
        self.create_floor()
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
        return floor_coords
        
    # Возвращает число клеточек на полу (х и у)
    def take_floor_num_squares(self):
        return self.floor_num_squares

    # !!! работает только из (0,0,далеко)
    # алгоритм z буфера для рисования плоскостей
    def calc_draw_objects_Z_bufer(self, offsets, dimensions, list_planes):
        return Z_buffer_algo(offsets, dimensions, list_planes, DEF_SIZE_SQARES, DEF_MAX_Z)

    # !!!
    # алгоритм Z буффера для добавления теней
    def calc_draw_objects_Z_bufer_light(self, offsets, dimensions, list_planes):
        dx, dy = offsets
        width, height = dimensions
        # Остальной код функции


    # Вычисляет координаты видимого пользователю экрана (размеры и смещения)
    def calc_coords_screen(self):
        # Получаем ширину и высоту canvas
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        # Получаем текущее смещение (если используется прокрутка или другие методы смещения)
        dx = self.canvas.xview()[0] * width  # Координата x смещения
        dy = self.canvas.yview()[0] * height  # Координата y смещения
        return (dx, dy), (width, height)

    # наложение матрицы теней на основную матрицу
    # !!!
    def combo_matrix(self, matrix, matrix_light):
        return matrix
    
    # отрисовка готовой матрицы с подсчетом закрашенных клеток и времени работы
    def draw_matrix(self, matrix, height_screen):
        # таймер
        start_time = t.time()
        # счетчик закрашенных клеток
        filled_cells = 0
        for y, row in enumerate(matrix):
            for x, elem in enumerate(row):
                color = elem[COLOR_PART]
                if color:
                    # отрисовка закрашенной клетки (height_screen - 3 - чтоб развернуть у вверх и чуть приподнять)
                    self.canvas.create_rectangle(x, height_screen - 3 - y, x + 1, height_screen - 3 - (y + 1), outline=color, fill=color)
                    filled_cells += 1
        end_time = t.time()
        elapsed_time = end_time - start_time
        # Вывод числа закрашенных клеток и времени работы в командную строку
        print(f"Время закраски {filled_cells} клеток = {elapsed_time:.4f} секунд")


    # получение списка плоскостей с цветами
    def calc_list_planes(self):
        return self.objects.calc_list_planes()
        

    # Зарисовка всех объектов сцены
    def draw_scene(self):
        (dx, dy), (width, height) = self.calc_coords_screen()
        # получение списка плоскостей с цветами
        list_planes = self.calc_list_planes()
        # добавляем плоскости к полу
        list_planes += self.create_floor_coords()
        # алгоритм z буфера для рисования плоскостей
        # print(f"size of list_planes matrix = {len(list_planes)}")
        matrix = self.calc_draw_objects_Z_bufer((dx, dy), (width, height), list_planes)
        # алгоритм Z буффера для добавления теней
        # matrix_light = self.calc_draw_objects_Z_bufer_light((dx, dy), (width, height), list_planes)
        # наложение матрицы теней на основную матрицу
        # matrix = self.combo_matrix(matrix, matrix_light)
        # отрисовка готовой матрицы (время работы выводится в командную строку)
        self.draw_matrix(matrix, height)

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
            if rc:
                self.create_floor(new_width, new_height, new_color)
                self.redraw_scene()
        return rc

    
    # ПОВОРОТЫ КАМЕРЫ (надо сделать !!!)
        






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