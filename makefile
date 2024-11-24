run: main.py
#	sudo nice -n -20 python3 main.py
	taskset -c 0-14 python3 main.py
#	numactl --interleave=all python3 main.py
#python3 main.py