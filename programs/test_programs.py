import subprocess

print("\033[92m Testing Calculator\033[0m\n")
subprocess.run([".././cscript.py", "./calculator.car"])

print("\033[92m Testing Fibonacci\033[0m\n")
subprocess.run([".././cscript.py", "./fibonacci.car"])

print("\033[92m Testing Guessing Game\033[0m\n")
subprocess.run([".././cscript.py", "./guessing_game.car"])

print("\033[92m Testing Multiples\033[0m\n")
subprocess.run([".././cscript.py", "./multiples.car"])

print("\033[92m Testing Syntax\033[0m\n")
subprocess.run([".././cscript.py", "./syntax.car"])

print("\033[92m Testing Even Fibonacci\033[0m\n")
subprocess.run([".././cscript.py", "./evenfib.car"])

print("\033[92m Testing FizzBuzz\033[0m\n")
subprocess.run([".././cscript.py", "./fizzbuzz.car"])

print("\033[92m Testing Main\033[0m\n")
subprocess.run([".././cscript.py", "./main.car"])

print("\033[92m Testing Reversed Array\033[0m\n")
subprocess.run([".././cscript.py", "./reversed_array.car"])

print("\033[92m Testing Soprted Array\033[0m\n")
subprocess.run([".././cscript.py", "./sort.car"])
