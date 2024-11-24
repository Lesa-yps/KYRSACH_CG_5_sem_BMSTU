Компьютерная графика: курсовая работа


Выполнила студентка группы ИУ7-55Б Талышева Олеся Николаевна


Задание курсовой:

Проектирование цифровых моделей помещений различной планировки.


*как запустить тестирование модульное через виртуальное окружение? (на линуксе)

python3 -m venv venv
source venv/bin/activate
pip install coverage pytest numpy
make -f iu7cglabs_kostritsky report-unittesting-latest.txt
deactivate
