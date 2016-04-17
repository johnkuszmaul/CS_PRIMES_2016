# CS_PRIMES_2016
PRIMES Project for 2016-17, involving implementation of Proof of Space

This project is implemented in Python 2.7.11.

# File Descriptions

`sc.py` genererates superconcentrator graphs (currently implementing butterfly graph scheme)

`ptc.py` generates a PTC hard-to-pebble graph using the superconcentrators from sc.py, per the sceme of Paul, Tarjan, and Celoni

`pebble.py` is a class that encapsulates the pebbling, i.e. the current configuration of pebbles on the graph

`pebbling_algos.py` contains several different pebbling algorithms of varying efficiency

`utils.py` stores a motley crew of miscellaneous functions
