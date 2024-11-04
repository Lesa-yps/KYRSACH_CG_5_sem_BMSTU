# Талышева Олеся ИУ7-55Б
# Курсач

# Импортируем библиотеки
import tkinter as tk
from tkinter import colorchooser
import tkinter.messagebox as mb
from tkinter import ttk
from typing import List, Optional, Tuple

from Add_interface import add_object_dialog, insert_delete_spinbox
from Load_scene import load_scene_file
from Del_change_object import delete_object_tree, change_object_tree
from Camera_work import rotate_camera
from Scene import Scene

MAX_SCENE_SIZE = 1000

list_of_objects = [(0, "стена"), (1, "дверь"), (2, "окно")]
# 
# Константы
MIN_WIDTH = 1300  # минимальная ширина окна приложения
MIN_HEIGHT = 910  # минимальная высота окна приложения
SIZE_OF_CANVAS = 500  # размер холста
STEP_CONST = 50  # шаг перемещения
# Переменные определяющие расположение/состояние окна
ZOOM = 1  # масштаб
SIDE_PLACE = 0  # переменная для определения сдвига в стороне
HEIGHT_PLACE = 0  # переменная для определения сдвига по высоте

color_scene = "#cccccc"  # цвет сцены по-умолчанию серый
is_painting = False  # идёт ли сейчас отрисовка
num_choose_object = 0  # номер выбранного объекта в выпадающем списке (стена / дверь / окно)
count_draw = 0 # номер отрисовки? (чтоб настроить сцену)


# сброс всего наработанного

def cleaning() -> None:
    global ZOOM, SIDE_PLACE, HEIGHT_PLACE, count_draw
    # Очистка всего содержимого на холсте
    cnv.delete("all")
    # Масштабирование холста до его стартового размера
    cnv.scale("all", 0, 0, 1, 1)
    # Установка положения прокрутки на начальное значение
    ds = 0
    cnv.xview_moveto(ds)
    cnv.yview_moveto(ds)
    ZOOM, SIDE_PLACE, HEIGHT_PLACE = 1, ds, ds
    # Очистка всех строк в таблице
    for item in tree.get_children():
        tree.delete(item)
    # Возвращаем сцену в стартовое состояние
    Facade.start_scene()
    # Устанавливаем размеры сцены в Spinbox
    x, y = Facade.take_floor_num_squares()
    insert_delete_spinbox(scene_width, x)
    insert_delete_spinbox(scene_height, y)
    count_draw = 1


# Функция вызывается в ответ на действия пользователя и выполняет требуемое или вызывает для этого другую функцию

def fork(text: str) -> None:
    global is_painting, count_draw
    if is_painting:
        mb.showerror('Ошибка!', "Дождитесь конца отрисовки!")
        return
    is_painting = True
    count_draw += 1
    if count_draw == 2:
        Facade.create_floor(int(scene_width.get()), int(scene_height.get()), color_scene)
    if text in ['X+', 'X-', 'Y+', 'Y-', 'Z+', 'Z-']:
        rotate_camera(Facade, text)
    elif text == 'Добавить объект':
        add_object_dialog(Facade, tree, chooser_object_combobox.get())
    elif text == 'Изменить объект':
        change_object_tree(Facade, tree)
    elif text == 'Изменить сцену':
        if not Facade.change_floor(int(scene_width.get()), int(scene_height.get()), color_scene):
            # возврат старых значений при недопустимых новых
            x, y = Facade.take_floor_num_squares()
            insert_delete_spinbox(scene_width, x)
            insert_delete_spinbox(scene_height, y)
    elif text == 'Удалить объект':
        delete_object_tree(Facade, tree)
    elif text == 'Загрузить сцену':
        fork('Очистить холст')
        rc = load_scene_file(Facade, tree, scene_width, scene_height, file_path_entry.get())
        if not rc:
            fork('Очистить холст')
    elif text == 'Выгрузить сцену':
        Facade.upload_scene(file_path_entry.get())
    # вращения камеры
    elif text == 'Очистить холст':
        cleaning()
    is_painting = False


# обработка события изменения размера окна
def resize_checker(event: tk.Event) -> None:
    # Получаем текущие размеры окна
    current_width = window.winfo_width()
    current_height = window.winfo_height()
    # Проверяем, если текущий размер меньше минимального, то устанавливаем его минимальным
    if current_width < MIN_WIDTH or current_height < MIN_HEIGHT:
        window.geometry(f'{MIN_WIDTH}x{MIN_HEIGHT}')


# Создаём окошко и обозначаем его параметры
window = tk.Tk()
window["bg"] = 'light pink'
window.title("КУРСОВАЯ РАБОТА ПО КОМПЬЮТЕРНОЙ ГРАФИКЕ")
window.geometry(f'{MIN_WIDTH}x{MIN_HEIGHT}')
# Устанавливается минимальный размер окна
window.minsize(MIN_WIDTH, MIN_HEIGHT)
# Привязываем обработчик события изменения размера окна
window.bind("<Configure>", resize_checker)


# Создаётся холст с установленными размерами
cnv = tk.Canvas(window, width=SIZE_OF_CANVAS, height=SIZE_OF_CANVAS, bg="white",
                cursor="plus", xscrollincrement=STEP_CONST, yscrollincrement=STEP_CONST)
cnv.grid(row=0, column=2, rowspan=5, sticky='nsew')
window.grid_columnconfigure(2, weight=1)


# Функция создаёт кнопку

def make_button(doing: str, button_frame: tk.Frame, width1: int) -> tk.Button:
    return tk.Button(button_frame, text=doing, bd=7, font=("Calibry", 12),
                     command=lambda: fork(doing),
                     activebackground="salmon", bg="khaki", height=1, width=width1, cursor="hand1")


# Функция для обработки события выбора функции в выпадающем списке
def what_choose_object(event: tk.Event):
    global num_choose_object
    num_choose_object = chooser_object_combobox.current()


# ДОБАВИТЬ ОБЪЕКТ

# Создаем фрейм для добавления объектов с обводкой
add_object_frame = tk.Frame(window, bg="lightpink", highlightbackground="PaleVioletRed", highlightcolor="IndianRed", highlightthickness=7)
add_object_frame.grid(row=0, column=0, padx=5, pady=10)



# Создаем поле для выбора объектов
choose_add_object_frame = tk.Frame(add_object_frame, bg="lightpink")
choose_add_object_frame.grid(row=0, column=0, padx=5, pady=2)
tk.Label(choose_add_object_frame, text="Добавить объект:", font=("Calibry", 12), bg="lightpink").grid(
    row=0, column=0, sticky="w")
# Создаем выпадающий список объектов
chooser_object_combobox = ttk.Combobox(choose_add_object_frame, width=32,
                            height=35, font=("Calibry", 12), state="readonly")
chooser_object_combobox["values"] = [i[-1]
                          for i in list_of_objects]  # Устанавливаем список вариантов
chooser_object_combobox.current(num_choose_object)  # Устанавливаем начальное значение (0)
# Привязываем обработчик события выбора элемента
chooser_object_combobox.bind("<<ComboboxSelected>>", what_choose_object)
chooser_object_combobox.grid(row=0, column=1, padx=5, pady=2, sticky="we")
# Создаем кнопку для построения
make_button('Добавить объект', add_object_frame, 20).grid(row=3, column=0, stick='we', padx=5, pady=2)


# Создаем фрейм для изменения объектов с их списком
change_object_frame = tk.Frame(window, bg="lightpink", highlightbackground="PaleVioletRed", highlightcolor="IndianRed", highlightthickness=7)
change_object_frame.grid(row=1, column=0, padx=5, pady=10)
tk.Label(change_object_frame, text="Изменить объект:", font=("Calibry", 12), bg="lightpink").grid(
    row=0, column=0, sticky="w")
# Создаем фрейм для таблицы объектов (стены, двери, окна) с прокруткой
table_frame = tk.Frame(change_object_frame, bg="lightpink")
table_frame.grid(row=1, column=0, columnspan=2, padx=0, pady=2)
# Создаем scrollbar
scrollbar = ttk.Scrollbar(table_frame)
scrollbar.grid(row=1, column=1, sticky="ns")
# Создаем таблицу
columns = ("type", "x", "y", "ширина", "высота", "глубина")
tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10, yscrollcommand=scrollbar.set)
# Определяем заголовки таблицы
tree.heading("type", text="Тип объекта")
tree.heading("x", text="X")
tree.heading("y", text="Y")
tree.heading("ширина", text="ширина")
tree.heading("высота", text="высота")
tree.heading("глубина", text="глубина")
# Настройка ширины колонок
tree.column("type", width=110)
tree.column("x", width=45)
tree.column("y", width=45)
tree.column("ширина", width=70)
tree.column("высота", width=70)
tree.column("глубина", width=70)
# Привязываем scrollbar к таблице
scrollbar.config(command=tree.yview)
# Размещаем таблицу
tree.grid(row=1, column=0, sticky="nsew")
# Настройка расширения таблицы при изменении размера окна
table_frame.grid_rowconfigure(1, weight=1)
table_frame.grid_columnconfigure(0, weight=1)

# УДАЛИТЬ ОБЪЕКТ
make_button('Удалить объект', change_object_frame, 20).grid(row=2, column=1, stick='we', pady=2)
# ИЗМЕНИТЬ ОБЪЕКТ
make_button('Изменить объект', change_object_frame, 20).grid(row=2, column=0, stick='we', pady=2)

# ИЗМЕНИТЬ РАЗМЕР СЦЕНЫ
make_button('Изменить сцену', change_object_frame, 20).grid(row=3, column=0, stick='we', pady=2)
# Создаем фрейм для размеров сцены
scene_size_frame = tk.Frame(change_object_frame, bg="lightpink")
scene_size_frame.grid(row=3, column=1, padx=0, pady=2)
tk.Label(scene_size_frame, text="размер:", font=("Calibry", 12), bg="lightpink").grid(
    row=0, column=0, stick='we', pady=2)
# Ширина х высота сцены
scene_width = tk.Spinbox(scene_size_frame, from_=1, to=MAX_SCENE_SIZE, width=5)
scene_width.grid(row=0, column=1, stick='we', pady=2)
tk.Label(scene_size_frame, text="x", font=("Calibry", 12), bg="lightpink").grid(
    row=0, column=2, stick='we', pady=2)
scene_height = tk.Spinbox(scene_size_frame, from_=1, to=MAX_SCENE_SIZE, width=5)
scene_height.grid(row=0, column=3, stick='we', pady=2)

# выбор цвета добавляемого объекта
def choose_color() -> None:
    global color_scene
    color = colorchooser.askcolor(title="Выберите цвет")
    # Используется второй элемент кортежа для получения выбранного цвета
    color_scene = color[1]
    color_display.config(bg=color_scene)  # Обновление цвета индикаторного Label

# Создаем фрейм для выбора цвета
color_choose_frame = tk.Frame(change_object_frame, bg="lightpink")
color_choose_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=2)
# кнопка выбора цвета
button_color = tk.Button(color_choose_frame, text="Выбрать цвет сцены", command=lambda: choose_color(), activebackground="salmon", bg="khaki",
                         width=26, height=1, bd=7, font=("Calibry", 12))
button_color.grid(row=0, column=0, stick='we')
# Область для отображения выбранного цвета
color_display = tk.Label(color_choose_frame, bg=color_scene, width=20, height=1, bd=7, relief="sunken")
color_display.grid(row=0, column=1, padx=5)



# ИЗМЕНЕНИЕ ПОЛОЖЕНИЯ КАМЕРЫ
# (вращение по х, y и по z изменять)
camera_rotate_frame = tk.Frame(window, bg="lightpink", highlightbackground="PaleVioletRed", highlightcolor="IndianRed", highlightthickness=7)
camera_rotate_frame.grid(row=2, column=0, padx=5, pady=10)
tk.Label(camera_rotate_frame, text="Вращать камеру:", font=("Calibry", 12), bg="lightpink").grid(
    row=0, column=0, columnspan=8, sticky="w")
# вращение по х
make_button('X+', camera_rotate_frame, 2).grid(row=1, column=0, stick='we')
make_button('X-', camera_rotate_frame, 2).grid(row=1, column=1, stick='we')
# Разделитель между X и Y
tk.Frame(camera_rotate_frame, width=20, bg="lightpink").grid(row=1, column=2, pady=2)
# вращение по y
make_button('Y+', camera_rotate_frame, 2).grid(row=1, column=3, stick='we')
make_button('Y-', camera_rotate_frame, 2).grid(row=1, column=4, stick='we')
# Разделитель между Y и Z
tk.Frame(camera_rotate_frame, width=20, bg="lightpink").grid(row=1, column=5, pady=2)
# вращение по z
make_button('Z+', camera_rotate_frame, 2).grid(row=1, column=6, stick='we')
make_button('Z-', camera_rotate_frame, 2).grid(row=1, column=7, stick='we')


# ЗАГРУЗКА И СОХРАНЕНИЕ СЦЕНЫ

scene_load_frame = tk.Frame(window, bg="lightpink", highlightbackground="PaleVioletRed", highlightcolor="IndianRed", highlightthickness=7)
scene_load_frame.grid(row=3, column=0, padx=5, pady=10)
tk.Label(scene_load_frame, text="Загрузить / выгрузить сцену в файл:", font=("Calibry", 12), bg="lightpink").grid(
    row=0, column=0, columnspan=2, sticky="w")
tk.Label(scene_load_frame, text="Путь к файлу:", font=("Calibry", 12), bg="lightpink").grid(
    row=1, column=0, sticky="w")
# путь к файлу для загрузки / выгрузки сцены
file_path_entry = tk.Entry(scene_load_frame, font=("Calibry", 12))
file_path_entry.grid(row=1, column=1, stick='we', pady=2)
make_button('Загрузить сцену', scene_load_frame, 20).grid(row=2, column=0, stick='we')
make_button('Выгрузить сцену', scene_load_frame, 20).grid(row=2, column=1, stick='we')


# ОЧИСТИТЬ СЦЕНУ

# Создаем кнопку для очиски холста
make_button('Очистить холст', window, 18).grid(row=4, column=0, stick='we', padx=10, pady=5)


# КРАСИВАЯ ПОДПИСЬ)

tk.Label(window, text="Талышева Олеся ИУ7-55Б", bg='light pink',
         fg='grey', font=("Arial", 12, 'italic')).grid(row=5, column=0)


# ФУНКЦИИ ДЛЯ ПЕРЕМЕЩЕНИЯ И ЗУМА В ОДНОЙ ПЛОСКОСТИ

# Функции для приближения и удаления

def zoom_in(event: Optional[tk.Event] = None) -> None:
    if not is_painting:
        global ZOOM
        ZOOM *= 1.1
        cnv.scale("all", 0, 0, 1.1, 1.1)
        Facade.redraw_scene()

def zoom_out(event: Optional[tk.Event] = None) -> None:
    if not is_painting:
        global ZOOM
        ZOOM *= 0.9
        cnv.scale("all", 0, 0, 0.9, 0.9)
        Facade.redraw_scene()

# Функции для перемещения

# Функция для перемещения влево

def move_left(event: Optional[tk.Event] = None) -> None:
    if not is_painting:
        global SIDE_PLACE
        SIDE_PLACE += 1
        cnv.xview_scroll(round(-1 * ZOOM), "units")
        Facade.redraw_scene()

# Функция для перемещения вправо

def move_right(event: Optional[tk.Event] = None) -> None:
    if not is_painting:
        global SIDE_PLACE
        SIDE_PLACE -= 1
        cnv.xview_scroll(round(1 * ZOOM), "units")
        Facade.redraw_scene()

# Функция для перемещения вверх

def move_up(event: Optional[tk.Event] = None) -> None:
    if not is_painting:
        global HEIGHT_PLACE
        HEIGHT_PLACE -= 1
        cnv.yview_scroll(round(-1 * ZOOM), "units")
        Facade.redraw_scene()

# Функция для перемещения вниз

def move_down(event: Optional[tk.Event] = None) -> None:
    if not is_painting:
        global HEIGHT_PLACE
        HEIGHT_PLACE += 1
        cnv.yview_scroll(round(1 * ZOOM), "units")
        Facade.redraw_scene()


# Функция создаёт кнопку (только ей передаётся функция которая вызывается при нажатии)


def make_cnv_button(doing: str, button_frame: tk.Frame, width1: int, func) -> None:
    return tk.Button(button_frame, text=doing, bd=7, font=("Calibry", 12),
                     command=lambda: func(), activebackground="salmon", bg="khaki", height=1, width=width1)


# Создаем кнопок для изменения конфигурации холста
button_move_plane1_frame = tk.Frame(window)
button_move_plane1_frame.grid(row=5, column=2, padx=0, pady=0)
make_cnv_button('вверх', button_move_plane1_frame, 10, move_up).grid(
    row=0, column=0, stick='we')
make_cnv_button('вниз', button_move_plane1_frame, 10, move_down).grid(
    row=0, column=1, stick='we')
make_cnv_button('вправо', button_move_plane1_frame, 10, move_right).grid(
    row=0, column=2, stick='we')
make_cnv_button('влево', button_move_plane1_frame, 10, move_left).grid(
    row=0, column=3, stick='we')
make_cnv_button('увеличить', button_move_plane1_frame, 10, zoom_in).grid(
    row=0, column=5, stick='we')
make_cnv_button('уменьшить', button_move_plane1_frame, 10, zoom_out).grid(
    row=0, column=6, stick='we')

for i in range(6):
    window.grid_rowconfigure(i, weight=1)

# Создаём меню
menu = tk.Menu(window)
window.config(menu=menu)

# Создаёт вкладку меню "Действия" с выпадающим меню с действиями
menu_in = tk.Menu(menu, tearoff=0)

menu_in.add_command(label='Выбрать цвет плоскости',
                    command=choose_color)
menu_in.add_command(label='Масштабировать',
                    command=lambda: fork('Масштабировать'))
menu_in.add_command(label='Повернуть по x',
                    command=lambda: fork('Повернуть по x'))
menu_in.add_command(label='Повернуть по y',
                    command=lambda: fork('Повернуть по y'))
menu_in.add_command(label='Повернуть по z',
                    command=lambda: fork('Повернуть по z'))
menu_in.add_command(label='Построить',
                    command=lambda: fork('Построить'))
menu_in.add_command(label='Очистить холст',
                    command=lambda: fork('Очистить холст'))

menu.add_cascade(label="Действия", menu=menu_in)


# Создаёт вкладку меню "Информация" с выпадающим меню с информацией об авторе и программе
menu_inf = tk.Menu(menu, tearoff=0)

menu_inf.add_command(label='Информация об авторе', command=lambda: mb.showinfo(
    'Информация об авторе', "Программу разработала студентка МГТУ им.Н.Э.Баумана группы ИУ7-55Б Талышева Олеся Николаевна."))
menu_inf.add_command(label='Информация о программе', command=lambda: mb.showinfo('Информация о программе',
                                                                                 "Проектирование цифровых моделей помещений различной планировки."))
menu_inf.add_command(label='Руководство пользователя', command=lambda: mb.showinfo('Руководство пользователя',
                                                                                   "Программа реализовывает курсовую мою..."
                                                                                   "Алгоритм запускается по нижитию на кнопку 'Построить'. "
                                                                                   "Можно перемещать и зумить холст, а также вернуть его в стартовое состояние (кнопка 'Очистить холст')."))
menu.add_cascade(label="Информация", menu=menu_inf)


# реакция на закрытие окна
def on_closing() -> None:
    if mb.askokcancel("Выход", "Вы уверены что хотите выйти из приложения?"):
        window.destroy()


window.protocol("WM_DELETE_WINDOW", on_closing)

# Функция для обработки события прокрутки колеса мыши


def scroll(event: tk.Event) -> None:
    if event.delta > 0:
        zoom_in()
    else:
        zoom_out()
# Функция для обработки события нажатия клавиш клавиатуры


def key_press(event: tk.Event) -> None:
    if event.keysym == "Up":
        move_up()
    elif event.keysym == "Down":
        move_down()
    elif event.keysym == "Left":
        move_left()
    elif event.keysym == "Right":
        move_right()


# Привязка обработчиков событий к холсту
cnv.bind("<MouseWheel>", scroll)
window.bind("<KeyPress>", key_press)

# Начальная конфигурация
Facade = Scene(cnv)
fork("Очистить холст")

# Включается обработчик событий
window.mainloop()
