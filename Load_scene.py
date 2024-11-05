from tkinter import messagebox

from Add_interface import submit, insert_delete_spinbox



# Загружает сцену из файла
def load_scene_file(Facade, table, scene_width_spinbox, scene_height_spinbox, file_path):
    rc = True  # Флаг успешности загрузки
    
    try:
        with open(file_path, 'r') as file:
            # Обработка первой строки с описанием сцены
            first_line = file.readline().strip().split()
            if len(first_line) != 4 or first_line[0] != "сцена":
                raise RuntimeError("Некорректное форматирование первой строки")

            # Присваиваем цвет, ширину и длину сцены
            scene_color = first_line[1]
            try:
                scene_width = int(first_line[2])
                scene_height = int(first_line[3])
                Facade.create_floor(scene_width, scene_height, scene_color)

                # Устанавливаем размеры в Spinbox, если они корректны
                insert_delete_spinbox(scene_width_spinbox, str(scene_width))
                insert_delete_spinbox(scene_height_spinbox, str(scene_height))
                
            except ValueError:
                raise RuntimeError("Некорректные данные ширины или высоты сцены")

            # Обрабатываем остальные строки файла
            for line in file:
                if not rc:
                    break

                parts = line.strip().split()
                obj_type = parts[0]

                # Проверка корректности формата строки и типов данных
                if obj_type == "стена" and len(parts) == 7:
                    try:
                        color, width, height, length, offset_x, offset_y = parts[1], int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5]), int(parts[6])
                    except ValueError:
                        raise RuntimeError(f"Ошибка данных для объекта '{obj_type}'")
                    entry_arr = [width, height, length, offset_x, offset_y]
                
                elif obj_type == "дверь" and len(parts) == 10:
                    try:
                        color, width, height, length, offset_x, offset_y, width_hole, height_hole, side_hole = parts[1], int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5]), int(parts[6]), int(parts[7]), int(parts[8]), int(parts[9])
                    except ValueError:
                        raise RuntimeError(f"Ошибка данных для объекта '{obj_type}'")
                    entry_arr = [width, height, length, offset_x, offset_y, width_hole, height_hole, side_hole]
                
                elif obj_type == "окно" and len(parts) == 11:
                    try:
                        color, width, height, length, offset_x, offset_y, width_hole, height_hole, side_hole, up_hole = parts[1], int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5]), int(parts[6]), int(parts[7]), int(parts[8]), int(parts[9]), int(parts[10])
                    except ValueError:
                        raise RuntimeError(f"Ошибка данных для объекта '{obj_type}'")
                    entry_arr = [width, height, length, offset_x, offset_y, width_hole, height_hole, side_hole, up_hole]
                
                else:
                    raise RuntimeError("Некорректные параметры объекта")

                # Добавляем объект в сцену, если не возникло ошибок
                rc = submit(Facade, table, obj_type, color, entry_arr)
        Facade.redraw_scene()
        messagebox.showinfo("Успех", f"Сцена успешно загружена из файла {file_path}!") 

    except FileNotFoundError:
        messagebox.showerror("Ошибка", "Файл не найден. Проверьте путь к файлу.")
        rc = False
    except IOError:
        messagebox.showerror("Ошибка", "Не удалось открыть файл. Ошибка ввода-вывода.")
        rc = False
    except RuntimeError as e:
        # Ловим пользовательские исключения
        messagebox.showerror("Ошибка", f"Ошибка загрузки сцены: {str(e)}")
        rc = False
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить сцену из файла. Ошибка: {str(e)}")
        rc = False

    return rc
