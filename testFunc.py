import time as t
import matplotlib.pyplot as plt
from Point import Point
from Scene import Scene

DEF_COLOR = "#333333"
MAX_COUNT_PLANES = 200

# фейковый canvas, чтобы инициализировать Scene
class FakeCanvas:
    pass


# рисует графики по собранным данным
def draw_graphs(num_planes_list, seq_times, par_times):
    # вычисляем ускорение параллельной обработки по сравнению с последовательной
    speedups = [seq / par if par > 0 else None for seq, par in zip(seq_times, par_times)]

    # построение графиков
    plt.figure(figsize=(12, 6))

    # график сравнения времени выполнения
    plt.subplot(1, 2, 1)
    plt.plot(num_planes_list, seq_times, 'o-', label='Последовательно', color='blue')
    plt.plot(num_planes_list, par_times, 's-', label='Параллельно', color='green')
    plt.xlabel('Количество плоскостей')
    plt.ylabel('Время выполнения (сек)')
    plt.title('Сравнение времени выполнения')
    plt.legend()
    plt.grid(True)

    # график ускорения
    plt.subplot(1, 2, 2)
    plt.plot(num_planes_list, speedups, 'd-', color='red', label='Ускорение')
    plt.axhline(1, color='gray', linestyle='--', label='Без ускорения')
    plt.xlabel('Количество плоскостей')
    plt.ylabel('Ускорение')
    plt.title('Ускорение при параллельной обработке')
    plt.legend()
    plt.grid(True)

    # сохранение и отображение и графиков
    plt.tight_layout()
    plt.savefig('test_calc_pixel_matrix_performance.png')
    plt.show()


# функция тестирует calc_pixel_matrix параллельно или последовательно по числу плоскостей = размеру сцены (т.к. плоскости 1х1 по диагонали)
def test_calc_pixel_matrix(scene, num_planes, is_parallel):
    # генерация тестовых плоскостей
    list_planes = []
    for i in range(num_planes):
        plane = (Point(i, i, 0), Point(i + 1, i, 0), Point(i + 1, i + 1, 0), Point(i, i + 1, 0), DEF_COLOR)
        list_planes.append(plane)

    # параметры Z-буфера
    params_Z_buffer = (list_planes, (0, 0), (800, 600), Point(num_planes / 2, num_planes / 2, 0), 1, 30, 1000)

    # измерение времени выполнения
    start_time = t.time()
    scene.calc_pixel_matrix(params_Z_buffer, is_parallel)
    res_time = t.time() - start_time

    print(f"{'Параллельно' if is_parallel else 'Последовательно'}: {res_time:.4f} сек")
    return res_time


if __name__ == "__main__":
    # инициализация сцены
    canvas = FakeCanvas()
    scene = Scene(canvas)

    # размеры сцены для тестов
    i = 0
    num_planes_list = list()
    diff = 1
    while i < MAX_COUNT_PLANES:
        num_planes_list.append(i)
        i += diff
        diff += 1

    # собираем данные по всему количеству плоскостей
    seq_times_list, par_times_list = list(), list()
    for num_planes in num_planes_list:
        print(f"\nРазмер сцены: {num_planes}")
        seq_time = test_calc_pixel_matrix(scene, num_planes, is_parallel=False)
        par_time = test_calc_pixel_matrix(scene, num_planes, is_parallel=True)
        print(f"Ускорение при параллельной обработке: {seq_time / par_time if par_time > 0 else 'N/A'}")
        seq_times_list.append(seq_time)
        par_times_list.append(par_time)

    # рисует графики по собранным данным
    draw_graphs(num_planes_list, seq_times_list, par_times_list)