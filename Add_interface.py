import tkinter as tk
from tkinter import messagebox, colorchooser

# цвет объекта по-умолчанию синий
plane_color = "#0000ff"


# Задаёт новое значение spinbox
def insert_delete_spinbox(spinbox, x):
    spinbox.delete(0, "end")
    spinbox.insert(0, x)


# Функция, проверяющая корректность размеров и расположения дырки
def check_sizes(entry_arr, obj_type):
    rc = False   # Флаг успешности проверки
    for x in entry_arr[:3] + entry_arr[5:]:
        if x <= 0:
            messagebox.showerror("Ошибка", "Неположительные размеры! Проверьте границы объекта.")
            rc = True
            return rc

    width, height = entry_arr[0], entry_arr[1]

    if obj_type == "стена":
        pass

    elif obj_type == "дверь" or obj_type == "окно":
        width_hole, height_hole = entry_arr[5], entry_arr[6]
        # Проверка, чтобы отверстие не было шире или выше объекта
        if width_hole >= width or height_hole >= height:
            rc = True

        elif obj_type == "окно":
            up_hole = entry_arr[7]
            # Проверка, чтобы окно не вылезло за верх объекта
            if up_hole >= height or (up_hole + height_hole) >= height:
                rc = True

    if rc:
        messagebox.showerror("Ошибка", "Неверные размеры! Проверьте границы объекта.")

    return rc


# Определяем функцию для и добавления объекта
def submit(Facade, table, obj_type, color, entry_arr, dialog = None):
    # if dialog is not None:
        # color = plane_color
    # Флаг успешности проверок
    rc = True
    # Проверка пересечений и размеров
    if not Facade.check_intersection(entry_arr[:5]) and not check_sizes(entry_arr, obj_type):
        # Добавляем объект
        Facade.add_object(obj_type, tuple([color] + entry_arr))

        # Добавляем строку в таблицу
        new_data = (obj_type, entry_arr[3], entry_arr[4], entry_arr[0], entry_arr[1], entry_arr[2])
        # Добавление строки в конец таблицы
        table.insert("", "end", values=new_data)

        # Реакция диалогового окна если оно есть
        if (dialog):
            messagebox.showinfo("Успех", f"Объект '{obj_type}' успешно добавлен!")
            dialog.destroy()  # Закрываем окно после добавления

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

        SIZE_Y += 100
        entry_arr += [width_hole_spin, height_hole_spin]

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

    # Кнопка для подтверждения
    tk.Button(dialog, text="Добавить объект", command=lambda: submit(Facade, table, obj_type, plane_color, [int(i.get()) for i in entry_arr], dialog), width=20, height=1, bd=7, font=("Calibry", 12), activebackground="salmon", bg="khaki", cursor="hand1").pack()

    # Устанавливаем фиксированный размер окна
    dialog.geometry(f"{SIZE_X}x{SIZE_Y}")
    dialog.resizable(False, False)  # Запрещаем изменение размера окна

    dialog.mainloop()