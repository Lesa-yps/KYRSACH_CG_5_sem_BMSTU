import tkinter as tk
from tkinter import messagebox, colorchooser

from Objects import X_SIDE, Y_SIDE

# идёт ли сейчас отрисовка
from multiprocessing import Value
is_painting = Value('b', False)  # Создание общей переменной типа bool

# цвет объекта по-умолчанию синий
plane_color = "#0000ff"


# Задаёт новое значение spinbox
def insert_delete_spinbox(spinbox, x):
    spinbox.delete(0, "end")
    spinbox.insert(0, x)


# Функция, проверяющая корректность размеров и расположения дырки
def check_sizes(entry_arr, obj_type):
    rc = False   # Флаг успешности проверки

    pos_entry_arr = entry_arr[:3] + entry_arr[5:]
    if obj_type == "окно" or obj_type == "дверь":
        pos_entry_arr.pop(5)

    for x in pos_entry_arr:
        if x <= 0:
            messagebox.showerror("Ошибка", "Неположительные размеры! Проверьте границы объекта.")
            rc = True
            return rc

    width, height, lenght = entry_arr[0], entry_arr[1], entry_arr[2]

    if obj_type == "дверь" or obj_type == "окно":

        width_hole, height_hole, side_hole = entry_arr[5], entry_arr[6], entry_arr[7]
        # Проверка, чтобы отверстие не было шире или выше объекта + что его положение корректно
        if (side_hole == X_SIDE and (width - width_hole) < 2) or (side_hole == Y_SIDE and (lenght - width_hole) < 2) or height_hole >= height or (side_hole != X_SIDE and side_hole != Y_SIDE):
            rc = True

        elif obj_type == "окно":
            up_hole = entry_arr[8]
            # Проверка, чтобы окно не вылезло за границы объекта
            if up_hole + height_hole >= height or up_hole <= 0:
                rc = True

    if rc:
        messagebox.showerror("Ошибка", "Неверные размеры! Проверьте границы объекта.")

    return rc

# поворот объекта на 90 градусов
def rotate_object(obj_type, entry_arr):
    width_spin, height_spin, length_spin, offset_x_spin, offset_y_spin = tuple(entry_arr[:5])
    new_entry_arr = [length_spin, height_spin, width_spin, offset_x_spin, offset_y_spin]
    if obj_type == "дверь" or obj_type == "окно":
        width_hole, height_hole, side_hole = entry_arr[5], entry_arr[6], entry_arr[7]
        new_entry_arr += [width_hole, height_hole, Y_SIDE - side_hole]
        if obj_type == "окно":
            up_hole = entry_arr[8]
            new_entry_arr += [up_hole]
    return new_entry_arr

# проверяет заполнены ли поля ввода координат числами
def check_input_field(arr_entry, help_str, is_float = False, echo_err = True):
    try:
        for elem in arr_entry:
            if is_float:
                float(elem)
            else:
                int(elem)
    except ValueError:
        if echo_err:
            messagebox.showerror(
                'Ошибка!', f"Поля ввода некорректно заполнены ({help_str}).")
        return False
    else:
        return True


# Определяем функцию для и добавления объекта
def submit(Facade, table, obj_type, color, entry_arr, is_rotate = False, dialog = None):
    #print("entry_arr", entry_arr)
    global is_painting
    # Флаг успешности проверок
    rc = check_input_field(entry_arr, f"добавление объекта '{obj_type}'")
    if not rc:
        return rc
    if dialog:
        entry_arr = [int(i) for i in entry_arr]
    # Если пользователь запросил поворот - поворачиваем
    if is_rotate:
        entry_arr = rotate_object(obj_type, entry_arr)
    # Проверка пересечений и размеров
    if not Facade.check_intersection(entry_arr[:5]) and not check_sizes(entry_arr, obj_type):
        # Добавляем объект
        Facade.add_object(obj_type, tuple([color] + entry_arr), is_redraw = (dialog is not None))

        # Добавляем строку в таблицу
        new_data = (obj_type, entry_arr[3], entry_arr[4], entry_arr[0], entry_arr[1], entry_arr[2])
        # Добавление строки в конец таблицы
        table.insert("", "end", values=new_data)

        # Реакция диалогового окна если оно есть
        if (dialog):
            messagebox.showinfo("Успех", f"Объект '{obj_type}' успешно добавлен!")
            dialog.destroy()  # Закрываем окно после добавления
            is_painting.value = False

    else:
        rc = False
    return rc    
    



# Основной метод для добавления объекта (data_arr используется для задания значений по умолчанию в полях, если передан)
def add_object_dialog(Facade, table, obj_type, color = None, data_arr = None):
    global plane_color
    if color is not None:
        plane_color = color

    # Создаем новое окно для ввода параметров объекта
    dialog = tk.Toplevel()
    dialog.title(obj_type)
    dialog["bg"] = 'light pink'

    # Размеры окна
    SIZE_X, SIZE_Y = 200, 338
    
    # Число клеточек на доске
    floor_num_squares = Facade.take_floor_num_squares()

    # Поля ввода для параметров объекта
    # ДЛЯ ВСЕХ
    tk.Label(dialog, text="Ширина объекта:", bg='light pink').pack()
    width_spin = tk.Spinbox(dialog, from_=1, to=floor_num_squares[0], width=5)
    width_spin.pack()
    if data_arr is not None:
        insert_delete_spinbox(width_spin, data_arr[0])

    tk.Label(dialog, text="Высота объекта:", bg='light pink').pack()
    height_spin = tk.Spinbox(dialog, from_=1, to=100, width=5)
    height_spin.pack()
    if data_arr is not None:
        insert_delete_spinbox(height_spin, data_arr[1])

    tk.Label(dialog, text="Длина объекта:", bg='light pink').pack()
    length_spin = tk.Spinbox(dialog, from_=1, to=floor_num_squares[1], width=5)
    length_spin.pack()
    if data_arr is not None:
        insert_delete_spinbox(length_spin, data_arr[2])

    tk.Label(dialog, text="Смещение объекта по X:", bg='light pink').pack()
    offset_x_spin = tk.Spinbox(dialog, from_=0, to=floor_num_squares[0], width=5)
    offset_x_spin.pack()
    if data_arr is not None:
        insert_delete_spinbox(offset_x_spin, data_arr[3])

    tk.Label(dialog, text="Смещение объекта по Y:", bg='light pink').pack()
    offset_y_spin = tk.Spinbox(dialog, from_=0, to=floor_num_squares[1], width=5)
    offset_y_spin.pack()
    if data_arr is not None:
        insert_delete_spinbox(offset_y_spin, data_arr[4])

    entry_arr = [width_spin, height_spin, length_spin, offset_x_spin, offset_y_spin]

    # ОКНО или ДВЕРЬ
    if obj_type == "дверь" or obj_type == "окно":

        # Переменная для хранения выбранного значения
        if data_arr is not None:
            side_hole_radbut = tk.StringVar(value=data_arr[7])
        else:
            side_hole_radbut = tk.StringVar(value=X_SIDE)  # значение по умолчанию

        # Создаем радиокнопки
        width_radio = tk.Radiobutton(dialog, text="Отверстие по ширине", variable=side_hole_radbut, value=X_SIDE, bg='light pink')
        length_radio = tk.Radiobutton(dialog, text="Отверстие по длине", variable=side_hole_radbut, value=Y_SIDE, bg='light pink')

        # Размещаем радиокнопки
        width_radio.pack(anchor="w")
        length_radio.pack(anchor="w")

        tk.Label(dialog, text="Ширина отверстия:", bg='light pink').pack()
        width_hole_spin = tk.Spinbox(dialog, from_=1, to=floor_num_squares[0], width=5)
        width_hole_spin.pack()
        if data_arr is not None:
            insert_delete_spinbox(width_hole_spin, data_arr[5])

        tk.Label(dialog, text="Высота отверстия:", bg='light pink').pack()
        height_hole_spin = tk.Spinbox(dialog, from_=1, to=100, width=5)
        height_hole_spin.pack()
        if data_arr is not None:
            insert_delete_spinbox(height_hole_spin, data_arr[6])

        SIZE_Y += 145
        entry_arr += [width_hole_spin, height_hole_spin, side_hole_radbut]

    # ОКНО
    if obj_type == "окно":
        tk.Label(dialog, text="Поднятие отверстия:", bg='light pink').pack()
        up_hole_spin = tk.Spinbox(dialog, from_=1, to=98, width=5)
        up_hole_spin.pack()
        if data_arr is not None and len(data_arr) > 7:
            insert_delete_spinbox(up_hole_spin, data_arr[7])

        SIZE_Y += 50
        entry_arr += [up_hole_spin]

    # выбор цвета добавляемого объекта
    def choose_color() -> None:
        global plane_color
        plane_color = colorchooser.askcolor(title="Выберите цвет")[1]
        button_color.config(bg=plane_color)  # Обновление цвета индикаторного Label

    # кнопка выбора цвета
    button_color = tk.Button(dialog, text="Выбрать цвет", command=lambda: choose_color(), activebackground="salmon", width=20, height=1, bg=plane_color, font=("Calibry", 12), bd=7, cursor="hand1")
    button_color.pack()

    # Переменная для хранения состояния галочки (0 - снята, 1 - установлена)
    is_rotate = tk.BooleanVar(value=False)
    # если это изменение объекта добавляем возможность поворота на 90 градусов
    if data_arr is not None:
        check_button = tk.Checkbutton(dialog, text="повернуть на 90 гр.", variable=is_rotate, bg='light pink', font=("Calibry", 12))
        check_button.pack()
        SIZE_Y += 40

    if data_arr is not None:
        res_button_text = "Изменить объект"
    else:
        res_button_text = "Добавить объект"

    # Кнопка для подтверждения
    tk.Button(dialog, text=res_button_text, command=lambda: submit(Facade, table, obj_type, plane_color, [i.get() for i in entry_arr], is_rotate.get(), dialog), width=20, height=1, bd=7, font=("Calibry", 12), activebackground="salmon", bg="khaki", cursor="hand1").pack()

    # Устанавливаем фиксированный размер окна
    dialog.geometry(f"{SIZE_X}x{SIZE_Y}")
    dialog.resizable(False, False)  # Запрещаем изменение размера окна

    # Определяем функцию для закрытия окна, которая установит is_painting в False
    def on_close():
        is_painting.value = False
        dialog.destroy()

    # Привязываем on_close к событию закрытия окна
    dialog.protocol("WM_DELETE_WINDOW", on_close)

    dialog.mainloop()