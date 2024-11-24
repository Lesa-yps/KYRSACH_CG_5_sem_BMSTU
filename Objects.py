import tkinter as tk

from Point import Point

# с какой стороны объекта отверстие
X_SIDE = 0
Y_SIDE = 1


# Класс стена
class Wall:
    # Инициализирует стену по её обязательным параметрам (вниамние! единицы измерения этого всего - клеточки)
    # color, width, height, length, offset_x, offset_y
    def __init__(self, params):
        color, width, height, length, offset_x, offset_y = params
        self.color = color
        self.width = width
        self.height = height
        self.length = length
        self.offset_x = offset_x
        self.offset_y = offset_y
    # Возвращает массив из занятых клеточек в формате (х, у)
    def take_busy_coords(self):
        arr = []
        for x in range(self.offset_x, self.width + self.offset_x):
            for y in range(self.offset_y, self.length + self.offset_y):
                arr.append((x, y))
        return arr
    # проверяет идентичность базовых параметров текущему элементу
    def is_equals(self, data):
        offset_x, offset_y, width, height, length = data
        if (self.offset_x == offset_x) and (self.offset_y == offset_y) and (self.width == width) and (self.height == height) and (self.length == length):
            return True
        return False
    # получаем словарь со всеми параметрами object_data_all["type"], object_data_all["color"], object_data_all["sizes"])
    def take_dict_params(self):
        object_data_all = dict()
        object_data_all["type"] = "стена"
        object_data_all["color"] = self.color
        object_data_all["sizes"] = [self.width, self.height, self.length, self.offset_x, self.offset_y]
        return object_data_all
    # Функция выгрузки данных об объекте в файл (файл открыт)
    def upload_data(self, file):
        file.write(f"стена {self.color} {self.width} {self.height} {self.length} {self.offset_x} {self.offset_y}\n")
    # получение списка плоскостей с цветами
    def calc_list_planes(self):
        arr_planes = list()
        x0, y0, z0, x1, y1, z1 = self.offset_x, self.offset_y, 0, self.offset_x + self.width, self.offset_y + self.length, self.height
        # нижняя плоскость
        arr_planes += [(Point(x0, y0, z0), Point(x1, y0, z0), Point(x1, y1, z0), Point(x0, y1, z0), self.color)]
        # слева
        arr_planes += [(Point(x0, y0, z0), Point(x1, y0, z0), Point(x1, y0, z1), Point(x0, y0, z1), self.color)]
        # спереди
        arr_planes += [(Point(x1, y0, z0), Point(x1, y1, z0), Point(x1, y1, z1), Point(x1, y0, z1), self.color)]
        # справа
        arr_planes += [(Point(x0, y1, z0), Point(x1, y1, z0), Point(x1, y1, z1), Point(x0, y1, z1), self.color)]
        # сзади
        arr_planes += [(Point(x0, y0, z0), Point(x0, y1, z0), Point(x0, y1, z1), Point(x0, y0, z1), self.color)]
        # сверху
        arr_planes += [(Point(x0, y0, z1), Point(x1, y0, z1), Point(x1, y1, z1), Point(x0, y1, z1), self.color)]
        return arr_planes
        


# Класс дверь (наследник стены)
class Door(Wall):
    # Инициализирует дверь по её обязательным параметрам (вниамние! единицы измерения этого всего - клеточки)
    # color, width, height, length, offset_x, offset_y, width_hole, height_hole
    def __init__(self, params):
        color, width, height, length, offset_x, offset_y, width_hole, height_hole, side_hole = params
        super().__init__((color, width, height, length, offset_x, offset_y))
        self.width_hole = width_hole
        self.height_hole = height_hole
        self.side_hole = side_hole
    # получаем словарь со всеми параметрами object_data_all["type"], object_data_all["color"], object_data_all["sizes"])
    def take_dict_params(self):
        object_data_all = super().take_dict_params()
        object_data_all["type"] = "дверь"
        object_data_all["sizes"] += [self.width_hole, self.height_hole, self.side_hole]
        return object_data_all
    # Функция выгрузки данных об объекте в файл (файл открыт)
    def upload_data(self, file):
        file.write(f"дверь {self.color} {self.width} {self.height} {self.length} {self.offset_x} {self.offset_y} {self.width_hole} {self.height_hole} {self.side_hole}\n")
    # получение списка плоскостей с цветами
    def calc_list_planes(self):
        arr_planes = list()
        x0, y0, z0, x1, y1, z1 = self.offset_x, self.offset_y, 0, self.offset_x + self.width, self.offset_y + self.length, self.height
        if (self.side_hole == X_SIDE):
            width_wall_near_hole = (self.width - self.width_hole) // 2
            z11, y01, y11 = z0 + self.height_hole, y0 + width_wall_near_hole, y1 - width_wall_near_hole
            # нижняя плоскость
            arr_planes += [(Point(x0, y0, z0), Point(x1, y0, z0), Point(x1, y01, z0), Point(x0, y01, z0), self.color)]
            arr_planes += [(Point(x0, y11, z0), Point(x1, y11, z0), Point(x1, y1, z0), Point(x0, y1, z0), self.color)]
            # слева
            arr_planes += [(Point(x0, y0, z0), Point(x1, y0, z0), Point(x1, y0, z1), Point(x0, y0, z1), self.color)]
            # спереди
            arr_planes += [(Point(x1, y0, z0), Point(x1, y01, z0), Point(x1, y01, z1), Point(x1, y0, z1), self.color)]
            arr_planes += [(Point(x1, y11, z0), Point(x1, y1, z0), Point(x1, y1, z1), Point(x1, y11, z1), self.color)]
            arr_planes += [(Point(x1, y01, z11), Point(x1, y11, z11), Point(x1, y11, z1), Point(x1, y01, z1), self.color)]
            # справа
            arr_planes += [(Point(x0, y1, z0), Point(x1, y1, z0), Point(x1, y1, z1), Point(x0, y1, z1), self.color)]
            # сзади
            arr_planes += [(Point(x0, y0, z0), Point(x0, y01, z0), Point(x0, y01, z1), Point(x0, y0, z1), self.color)]
            arr_planes += [(Point(x0, y11, z0), Point(x0, y1, z0), Point(x0, y1, z1), Point(x0, y11, z1), self.color)]
            arr_planes += [(Point(x0, y01, z11), Point(x0, y11, z11), Point(x0, y11, z1), Point(x0, y01, z1), self.color)]
            # сверху
            arr_planes += [(Point(x0, y0, z1), Point(x1, y0, z1), Point(x1, y1, z1), Point(x0, y1, z1), self.color)]
            # внутри (двери)
            arr_planes += [(Point(x0, y01, z0), Point(x1, y01, z0), Point(x1, y01, z11), Point(x0, y01, z11), self.color)]
            arr_planes += [(Point(x0, y11, z0), Point(x1, y11, z0), Point(x1, y11, z11), Point(x0, y11, z11), self.color)]
            arr_planes += [(Point(x0, y01, z11), Point(x1, y01, z11), Point(x1, y11, z11), Point(x0, y11, z11), self.color)]
        elif self.side_hole == Y_SIDE:
            lenght_wall_near_hole = (self.length - self.width_hole) // 2
            z11, x01, x11 = z0 + self.height_hole, x0 + lenght_wall_near_hole, x1 - lenght_wall_near_hole
            # нижняя плоскость
            arr_planes += [(Point(x0, y0, z0), Point(x01, y0, z0), Point(x01, y1, z0), Point(x0, y1, z0), self.color)]
            arr_planes += [(Point(x11, y0, z0), Point(x1, y0, z0), Point(x1, y1, z0), Point(x11, y1, z0), self.color)]
            # слева
            arr_planes += [(Point(x0, y0, z0), Point(x01, y0, z0), Point(x01, y0, z1), Point(x0, y0, z1), self.color)]
            arr_planes += [(Point(x11, y0, z0), Point(x1, y0, z0), Point(x1, y0, z1), Point(x11, y0, z1), self.color)]
            arr_planes += [(Point(x01, y0, z11), Point(x11, y0, z11), Point(x11, y0, z1), Point(x01, y0, z1), self.color)]
            # спереди
            arr_planes += [(Point(x1, y0, z0), Point(x1, y1, z0), Point(x1, y1, z1), Point(x1, y0, z1), self.color)]
            # справа
            arr_planes += [(Point(x0, y1, z0), Point(x01, y1, z0), Point(x01, y1, z1), Point(x0, y1, z1), self.color)]
            arr_planes += [(Point(x11, y1, z0), Point(x1, y1, z0), Point(x1, y1, z1), Point(x11, y1, z1), self.color)]
            arr_planes += [(Point(x01, y1, z11), Point(x11, y1, z11), Point(x11, y1, z1), Point(x01, y1, z1), self.color)]
            # сзади
            arr_planes += [(Point(x0, y0, z0), Point(x0, y1, z0), Point(x0, y1, z1), Point(x0, y0, z1), self.color)]
            # сверху
            arr_planes += [(Point(x0, y0, z1), Point(x1, y0, z1), Point(x1, y1, z1), Point(x0, y1, z1), self.color)]
            # внутри (двери)
            arr_planes += [(Point(x01, y0, z0), Point(x01, y1, z0), Point(x01, y1, z11), Point(x01, y0, z11), self.color)]
            arr_planes += [(Point(x11, y0, z0), Point(x11, y1, z0), Point(x11, y1, z11), Point(x11, y0, z11), self.color)]
            arr_planes += [(Point(x01, y0, z11), Point(x11, y0, z11), Point(x11, y1, z11), Point(x01, y1, z11), self.color)]
        return arr_planes



# Класс окно (наследник двери)
class Window(Door):
    # Инициализирует окно по его обязательным параметрам (вниамние! единицы измерения этого всего - клеточки)
    # color, width, height, length, offset_x, offset_y, width_hole, height_hole, up_hole
    def __init__(self, params):
        color, width, height, length, offset_x, offset_y, width_hole, height_hole, side_hole, up_hole = params
        super().__init__((color, width, height, length, offset_x, offset_y, width_hole, height_hole, side_hole))
        self.up_hole = up_hole
    # получаем словарь со всеми параметрами object_data_all["type"], object_data_all["color"], object_data_all["sizes"])
    def take_dict_params(self):
        object_data_all = super().take_dict_params()
        object_data_all["type"] = "окно"
        object_data_all["sizes"] += [self.up_hole]
        return object_data_all
    # Функция выгрузки данных об объекте в файл (файл открыт)
    def upload_data(self, file):
        file.write(f"окно {self.color} {self.width} {self.height} {self.length} {self.offset_x} {self.offset_y} {self.width_hole} {self.height_hole} {self.side_hole} {self.up_hole}\n")
    # получение списка плоскостей с цветами
    def calc_list_planes(self):
        arr_planes = list()
        x0, y0, z0, x1, y1, z1 = self.offset_x, self.offset_y, 0, self.offset_x + self.width, self.offset_y + self.length, self.height
        height_wall_near_hole = (self.height - self.height_hole) // 2
        z11, z01 = z1 - height_wall_near_hole, z0 + height_wall_near_hole
        if (self.side_hole == X_SIDE):
            width_wall_near_hole = (self.width - self.width_hole) // 2
            y01, y11 = y0 + width_wall_near_hole, y1 - width_wall_near_hole
            # нижняя плоскость
            arr_planes += [(Point(x0, y0, z0), Point(x1, y0, z0), Point(x1, y1, z0), Point(x0, y1, z0), self.color)]
            # слева
            arr_planes += [(Point(x0, y0, z0), Point(x1, y0, z0), Point(x1, y0, z1), Point(x0, y0, z1), self.color)]
            # спереди
            arr_planes += [(Point(x1, y0, z0), Point(x1, y01, z0), Point(x1, y01, z1), Point(x1, y0, z1), self.color)]
            arr_planes += [(Point(x1, y11, z0), Point(x1, y1, z0), Point(x1, y1, z1), Point(x1, y11, z1), self.color)]
            arr_planes += [(Point(x1, y01, z11), Point(x1, y11, z11), Point(x1, y11, z1), Point(x1, y01, z1), self.color)]
            arr_planes += [(Point(x1, y01, z0), Point(x1, y11, z0), Point(x1, y11, z01), Point(x1, y01, z01), self.color)]
            # справа
            arr_planes += [(Point(x0, y1, z0), Point(x1, y1, z0), Point(x1, y1, z1), Point(x0, y1, z1), self.color)]
            # сзади
            arr_planes += [(Point(x0, y0, z0), Point(x0, y01, z0), Point(x0, y01, z1), Point(x0, y0, z1), self.color)]
            arr_planes += [(Point(x0, y11, z0), Point(x0, y1, z0), Point(x0, y1, z1), Point(x0, y11, z1), self.color)]
            arr_planes += [(Point(x0, y01, z11), Point(x0, y11, z11), Point(x0, y11, z1), Point(x0, y01, z1), self.color)]
            arr_planes += [(Point(x0, y01, z0), Point(x0, y11, z0), Point(x0, y11, z01), Point(x0, y01, z01), self.color)]
            # сверху
            arr_planes += [(Point(x0, y0, z1), Point(x1, y0, z1), Point(x1, y1, z1), Point(x0, y1, z1), self.color)]
            # внутри (окна)
            arr_planes += [(Point(x0, y01, z01), Point(x1, y01, z01), Point(x1, y01, z11), Point(x0, y01, z11), self.color)]
            arr_planes += [(Point(x0, y11, z01), Point(x1, y11, z01), Point(x1, y11, z11), Point(x0, y11, z11), self.color)]
            arr_planes += [(Point(x0, y01, z11), Point(x0, y11, z11), Point(x1, y11, z11), Point(x1, y01, z11), self.color)]
            arr_planes += [(Point(x0, y01, z01), Point(x0, y11, z01), Point(x1, y11, z01), Point(x1, y01, z01), self.color)]
        if (self.side_hole == Y_SIDE):
            lenght_wall_near_hole = (self.length - self.width_hole) // 2
            x01, x11 = x0 + lenght_wall_near_hole, x1 - lenght_wall_near_hole
            # нижняя плоскость
            arr_planes += [(Point(x0, y0, z0), Point(x1, y0, z0), Point(x1, y1, z0), Point(x0, y1, z0), self.color)]
            # слева
            arr_planes += [(Point(x0, y0, z0), Point(x01, y0, z0), Point(x01, y0, z1), Point(x0, y0, z1), self.color)]
            arr_planes += [(Point(x11, y0, z0), Point(x1, y0, z0), Point(x1, y0, z1), Point(x11, y0, z1), self.color)]
            arr_planes += [(Point(x01, y0, z11), Point(x11, y0, z11), Point(x11, y0, z1), Point(x01, y0, z1), self.color)]
            arr_planes += [(Point(x01, y0, z0), Point(x11, y0, z0), Point(x11, y0, z01), Point(x01, y0, z01), self.color)]
            # спереди
            arr_planes += [(Point(x1, y0, z0), Point(x1, y1, z0), Point(x1, y1, z1), Point(x1, y0, z1), self.color)]
            # справа
            arr_planes += [(Point(x0, y1, z0), Point(x01, y1, z0), Point(x01, y1, z1), Point(x0, y1, z1), self.color)]
            arr_planes += [(Point(x11, y1, z0), Point(x1, y1, z0), Point(x1, y1, z1), Point(x11, y1, z1), self.color)]
            arr_planes += [(Point(x01, y1, z11), Point(x11, y1, z11), Point(x11, y1, z1), Point(x01, y1, z1), self.color)]
            arr_planes += [(Point(x01, y1, z0), Point(x11, y1, z0), Point(x11, y1, z01), Point(x01, y1, z01), self.color)]
            # сзади
            arr_planes += [(Point(x0, y0, z0), Point(x0, y1, z0), Point(x0, y1, z1), Point(x0, y0, z1), self.color)]
            # сверху
            arr_planes += [(Point(x0, y0, z1), Point(x1, y0, z1), Point(x1, y1, z1), Point(x0, y1, z1), self.color)]
            # внутри (окна)
            arr_planes += [(Point(x01, y0, z01), Point(x01, y1, z01), Point(x01, y1, z11), Point(x01, y0, z11), self.color)]
            arr_planes += [(Point(x11, y0, z01), Point(x11, y1, z01), Point(x11, y1, z11), Point(x11, y0, z11), self.color)]
            arr_planes += [(Point(x01, y0, z11), Point(x11, y0, z11), Point(x11, y1, z11), Point(x01, y1, z11), self.color)]
            arr_planes += [(Point(x01, y0, z01), Point(x11, y0, z01), Point(x11, y1, z01), Point(x01, y1, z01), self.color)]
        return arr_planes


# Класс со всеми объектами на сцене
class Objects:
    # Инициализирует массив объектов на канвазе
    def __init__(self):
        self.clear()

    # Создаёт пустые массивы стен, дверей и окон
    def clear(self):
        self.walls = []
        self.windows = []
        self.doors = []

    # добавление стены
    def add_wall(self, params):
        self.walls += [Wall(params)]
    # добавление окна
    def add_window(self, params):
        self.windows += [Window(params)]
    # добавление двери
    def add_door(self, params):
        self.doors += [Door(params)]

    # удаление стены (по базовым параметрам из таблицы)
    def del_wall(self, data):
        for i in range(len(self.walls)):
            if self.walls[i].is_equals(data):
                self.walls.pop(i)
                break
    # удаление окна (по базовым параметрам из таблицы)
    def del_window(self, data):
        for i in range(len(self.windows)):
            if self.windows[i].is_equals(data):
                self.windows.pop(i)
                break
    # удаление двери (по базовым параметрам из таблицы)
    def del_door(self, data):
        for i in range(len(self.doors)):
            if self.doors[i].is_equals(data):
                self.doors.pop(i)
                break

    # Создаёт матрицу на которой уже есть элементы
    def make_busy_matrix(self, size_x, size_y):
        matrix = [[False for _ in range(size_x)] for _ in range(size_y)]
        for elem in self.walls + self.doors + self.windows:
            coords = elem.take_busy_coords()
            for (x, y) in coords:
                matrix[y][x] = True
        return matrix
    
    # Получаем все данные объекта по частичным данным из таблицы (получаем словарь object_data_all["type"], object_data_all["color"], object_data_all["sizes"])
    def take_dict_params(self, new_item_data):
        type, data = new_item_data[0], new_item_data[1:]
        if type == "стена":
            arr = self.walls
        elif type == "дверь":
            arr = self.doors
        elif type == "окно":
            arr = self.windows
        for elem in arr:
            if elem.is_equals(data):
                object_data_all = elem.take_dict_params()
                break
        return object_data_all
    
    # Функция выгрузки данных обо всех объектах в файл (файл открыт)
    def upload_data(self, file):
        for elem in self.walls + self.doors + self.windows:
            elem.upload_data(file)

    # получение списка плоскостей с цветами
    def calc_list_planes(self):
        arr_planes = list()
        for elem in self.walls + self.doors + self.windows:
            arr_planes += elem.calc_list_planes()
        return arr_planes



# Пример использования класса Objects
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Обьекты")

    canvas = tk.Canvas(root, width=800, height=600, bg="white")
    canvas.pack()

    objects = Objects(canvas)

    objects.add_wall(((Point(100, 100, 100), Point(300, 300, 300)), None, "yellow", "pink"))
    objects.add_window(((Point(150, 150, 150), Point(400, 400, 400)),))
    objects.add_door(((Point(500, 500, 500), Point(600, 600, 600)),))

    objects.draw()

    root.mainloop()