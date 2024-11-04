import tkinter.messagebox as mb

DEF_MAX_Z = 1000

class Point:

    x = y = z = 0

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def print_coords(self):
        print("x = ", point.x)  # 1
        print("y = ", point.y)  # 2
        print("z = ", point.z)  # 3

    # Простейшая ортографическая проекция для отображения 3D-координат на 2D-плоскость
    def project(self, MAX_Z = DEF_MAX_Z):
        if (self.z <= -MAX_Z):
            mb.showinfo("Внимнаие!", f"Координата по z <= -{MAX_Z}! Ортографическая проекция сломалась бы, поэтому z стал = -{MAX_Z - 1}.")
            self.z = MAX_Z + 1
        scale = MAX_Z / (MAX_Z + self.z)
        self.x *= scale
        self.y *= scale
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
    
    def is_same(self, point1):
        return self.x == point1.x and self.y == point1.y and self.z == point1.z


# Пример использования класса Point
if __name__ == "__main__":
    point = Point(1, 2, 3)
    point.x = 0
    point.print_coords()
    
