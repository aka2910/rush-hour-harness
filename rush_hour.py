import sys
import z3

if __name__ == '__main__':
    # read the file provided as command line argument
    file = map(str.strip,open(sys.argv[1], "r").readlines())
    n, k = map(int, file[0].split(','))
    red_car = list(map(int, file[1].split(',')))
    cars = []
    mines = []
    for lines in file[2:]:
        if lines.split(',')[0]!='2':
            cars.append(list(map(int, lines.split(','))))
        else:
            mines.append(list(map(int, lines.split(','))))
    

      
