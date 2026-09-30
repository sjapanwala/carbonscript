import sys, os
from pathlib import Path

def library(lib):
    library = input("> ")
    if Path(library).exists():
        print("f")
    else:
        print("nf")

library(1)
