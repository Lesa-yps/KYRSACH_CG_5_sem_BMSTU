# функция затемняет цвет в формате "#хххххх" на переданный коэффициент
def darken_color(hex_color, factor=0.5):
    # проверка что цвет начинается с '#' и длина равна 7 символам
    if hex_color.startswith("#") and len(hex_color) == 7:
        # разбор цвета на компоненты R, G, B
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        # затемнение каждой компоненты
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        # форматируется и возвращается затемненный цвет
        return "#{:02x}{:02x}{:02x}".format(r, g, b)
    else:
        print("Неверный формат цвета. Используйте формат #RRGGBB.")
        return hex_color
    
# функция осветляет цвет в формате "#хххххх" на переданный коэффициент
def lighten_color(hex_color, factor=0.5):
    # проверка что цвет начинается с '#' и длина равна 7 символам
    if hex_color.startswith("#") and len(hex_color) == 7:
        # разбор цвета на компоненты R, G, B
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        # интерполируется каждый компонент к белому, увеличиваясь по коэффициенту
        r = int(r + (255 - r) * factor)
        g = int(g + (255 - g) * factor)
        b = int(b + (255 - b) * factor)
        # форматируется и возвращается осветлённый цвет
        return "#{:02x}{:02x}{:02x}".format(r, g, b)
    else:
        print("Неверный формат цвета. Используйте формат #RRGGBB.")
        return hex_color