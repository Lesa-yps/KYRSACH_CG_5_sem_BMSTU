#import tkinter.messagebox as mb

DEF_MAX_Z = 10000

class Point:

    x = y = z = 0

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def print_coords(self):
        print("x = ", self.x)  # 1
        print("y = ", self.y)  # 2
        print("z = ", self.z)  # 3

    # Простейшая ортографическая проекция для отображения 3D-координат на 2D-плоскость
    def project(self, MAX_Z = DEF_MAX_Z):
        # if (self.z <= -MAX_Z):
        #     mb.showinfo("Внимнаие!", f"Координата по z <= -{MAX_Z}! Ортографическая проекция сломалась бы, поэтому z стал = -{MAX_Z - 1}.")
        #     self.z = -MAX_Z + 1
        scale = (MAX_Z + self.z) / MAX_Z
        self.x *= scale
        self.y *= scale
        return self
    
    # Простейшая ортографическая проекция для отображения 3D-координат на 2D-плоскость (обратная)
    def anti_project(self, MAX_Z = DEF_MAX_Z):
        scale = (MAX_Z + self.z) / MAX_Z
        self.x /= scale
        self.y /= scale
        return self
    
    def coords(self):
        return (self.x, self.y, self.z)
    
    def copy(self):
        return Point(* self.coords())
    
    def multy(self, num):
        self.x *= num
        self.y *= num
        self.z *= num
        return self
    
    def add(self, dx, dy, dz):
        self.x += dx
        self.y += dy
        self.z += dz
        return self
    
    def is_same(self, point1, eps=1e-6):
        return (
            abs(self.x - point1.x) < eps and
            abs(self.y - point1.y) < eps and
            abs(self.z - point1.z) < eps
        )
    
    # Нормализация вектора
    def normalize(self):
        magnitude = (self.x**2 + self.y**2 + self.z**2)**0.5
        if magnitude > 1e-6:
            self.x /= magnitude
            self.y /= magnitude
            self.z /= magnitude
        return self

    # Векторное произведение с другим вектором (Point)
    def cross(self, point):
        cx = self.y * point.z - self.z * point.y
        cy = self.z * point.x - self.x * point.z
        cz = self.x * point.y - self.y * point.x
        return Point(cx, cy, cz)
    
    # Скалярное произведение с другим вектором (Point)
    def dot(self, point):
        return self.x * point.x + self.y * point.y + self.z * point.z


# Пример использования класса Point
if __name__ == "__main__":
    point1 = Point(1, 2, 3)
    point2 = Point(4, 5, 6)

    # Нормализация
    normalized = point1.copy().normalize()
    print("Normalized point1:", normalized.coords())

    # Векторное произведение
    cross_product = point1.cross(point2)
    print("Cross product of point1 and point2:", cross_product.coords())