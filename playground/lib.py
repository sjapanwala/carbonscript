import sys
def main(x):
    return int(x)**2

if len(sys.argv) > 1:
    print(main(sys.argv[1]))


