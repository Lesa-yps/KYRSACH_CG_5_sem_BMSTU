import math

def draw_triangle(bitmap, zBuffer, yBuffer, pointA, pointB, pointC, color, contour):
    """
    Рисует треугольник на bitmap, используя буферы глубины (zBuffer) и высоты (yBuffer).

    Аргументы:
        bitmap: изображение, на которое будет нанесён треугольник.
        zBuffer: буфер глубины.
        yBuffer: буфер высоты.
        pointA, pointB, pointC: вершины треугольника (объекты Point3D с координатами X, Y, Z).
        color: цвет для закраски треугольника.
        contour: флаг, указывающий, рисовать ли контур треугольника.
    """

    # Сортируем точки по координате Y, чтобы pointA был вверху, pointC внизу
    if pointA.Y > pointB.Y:
        pointA, pointB = pointB, pointA
    if pointA.Y > pointC.Y:
        pointA, pointC = pointC, pointA
    if pointB.Y > pointC.Y:
        pointB, pointC = pointC, pointB

    # Вычисляем приращения (dx, dz) вдоль сторон треугольника
    def compute_deltas(p1, p2):
        dy = p2.Y - p1.Y
        if abs(dy) > 1e-4:  # eps для предотвращения деления на 0
            dx = (p2.X - p1.X) / abs(dy)
            dz = (p2.Z - p1.Z) / abs(dy)
            return dx, dz
        return 0, 0  # Если dy почти 0, приращений нет

    dx_AC, dz_AC = compute_deltas(pointA, pointC)
    dx_AB, dz_AB = compute_deltas(pointA, pointB)
    dx_BC, dz_BC = compute_deltas(pointB, pointC)

    fl_AB = abs(pointB.Y - pointA.Y) <= 1e-4  # Проверяем, горизонтальна ли сторона AB
    start_BC = False  # Флаг, что началась обработка стороны BC

    # Начальные точки для сканирующей строки
    point1 = Point3D(pointA.X, pointA.Y, pointA.Z)
    point2 = Point3D(pointB.X, pointB.Y, pointB.Z) if fl_AB else Point3D(pointA.X, pointA.Y, pointA.Z)

    # Проводим заполнение треугольника построчно
    while point1.Y < pointC.Y:
        # Если включён контур, рисуем границы треугольника
        if contour:
            draw_point(bitmap, zBuffer, yBuffer, point1, "black")
            draw_point(bitmap, zBuffer, yBuffer, point2, "black")

        # Рисуем текущую сканирующую строку между point1 и point2
        draw_line(bitmap, zBuffer, yBuffer, point1, point2, color)

        # Обновляем координаты point2
        if point2.Y < pointB.Y:
            point2.X += dx_AB
            point2.Z += dz_AB
        else:
            if not start_BC:
                # Если переходим к стороне BC
                start_BC = True
                point2 = Point3D(pointB.X, pointB.Y, pointB.Z)
            else:
                point2.X += dx_BC
                point2.Z += dz_BC

        # Обновляем координаты point1
        point1.X += dx_AC
        point1.Y += 1
        point1.Z += dz_AC
