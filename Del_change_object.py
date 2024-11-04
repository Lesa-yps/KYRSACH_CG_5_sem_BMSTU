from tkinter import messagebox

from Add_interface import add_object_dialog

# Достаёт из таблицы данные выбранной строки
def take_del_select_table_data(tree):
    res = None
    selected_items = tree.selection()  # Получаем список ID выбранных строк
    # Проверка, что строка таблицы выбрана, и извлечение данных
    if selected_items:
        # Получаем первую выбранную строку
        item_id = selected_items[0]
        # Извлекаем данные из строки
        item_data = tree.item(item_id, "values")
        print("Данные выбранной строки:", item_data)
        res = [item_data[0]] + [int(i) for i in item_data[1:]]
        # Удаляем выбранную строку из таблицы
        tree.delete(item_id)
    else:
        messagebox.showerror("Ошибка", "Ни одна строка в таблице не выбрана.")
    return res

# Удаляет объект, выбранный в таблице
def delete_object_tree(Facade, tree):
    new_item_data = take_del_select_table_data(tree)
    if new_item_data:
        Facade.delele_object(new_item_data)


# Изменяет объект, выбранный в таблице
def change_object_tree(Facade, tree):
    new_item_data = take_del_select_table_data(tree)
    if new_item_data:
        # Получаем все данные объекта
        object_data_all = Facade.take_data_object(new_item_data)
        # Удаляем объект
        Facade.delele_object(new_item_data)
        # Добавляем новый объект, по-умолчанию задавая старые значения
        add_object_dialog(Facade, tree, object_data_all["type"], object_data_all["color"], object_data_all["sizes"])
