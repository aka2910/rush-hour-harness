import sys
import z3

s = z3.Solver()
# read the file provided as command line argument
file = list(map(str.strip, open(sys.argv[1], "r").readlines()))
n, timeout = map(int, file[0].split(','))
red_car = list(map(int, file[1].split(',')))
cars = []
mines = []
car_vars = []


class Car:
    def __init__(self, typ, ini_x, ini_y, id_):
        global s, n, timeout
        # typ =0 vertical
        # typ =1 or 2 horizontal
        self.typ = typ
        self.row = ini_x
        self.col = ini_y
        self.var = [z3.Int(f'{t}_{typ}_{id_}_{ini_x}_{ini_y}') for t in range(timeout + 1)]
        # for var b/w 0 to n-1
        # print(self.var)
        # print(k, n)
        for i in range(timeout + 1):
            s.add(self.var[i] >= 0, self.var[i] <= n - 2)
        for i in range(timeout):
            s.add(self.var[i + 1] - self.var[i] <= 1)
            s.add(self.var[i] - self.var[i + 1] <= 1)

        # goal
        if typ == 2:
            s.add(z3.Or([self.var[i] == n - 2 for i in range(timeout + 1)]))

        if typ == 0:
            s.add(self.var[0] == ini_x)
        else:
            s.add(self.var[0] == ini_y)


for lines in file[2:]:
    if lines.split(',')[0] != '2':
        k = len(cars)
        cars.append(list(map(int, lines.split(','))))
        car_vars.append(Car(cars[k][0], cars[k][1], cars[k][2], k))
    else:
        mines.append(list(map(int, lines.split(',')))[1:])

car_vars.append(Car(2, red_car[0], red_car[1], '*'))

for mine in mines:
    for car in car_vars:
        if car.typ == 0 and car.col == mine[1]:
            [s.add(z3.Not(z3.Or(car.var[i] == mine[0], car.var[i] + 1 == mine[0]))) for i in range(timeout + 1)]
        elif (car.typ == 1 or car.typ == 2) and car.row == mine[0]:
            [s.add(z3.Not(z3.Or(car.var[i] == mine[1], car.var[i] + 1 == mine[1]))) for i in range(timeout + 1)]

# avoid collision between horizontal and vertical
for i in range(len(car_vars)):
    for j in range(i + 1, len(car_vars)):
        car1 = car_vars[i]
        car2 = car_vars[j]
        if car1 == car2:
            continue
        # both hor
        if car1.typ != 0 and car2.typ != 0:
            if car1.row == car2.row:
                for t in range(timeout + 1):
                    if car1.col < car2.col:
                        s.add(car2.var[t] - car1.var[t] > 1)
                    else:
                        s.add(car2.var[t] - car1.var[t] < -1)
        if car1.typ == 0 and car2.typ == 0:
            if car1.col == car2.col:
                for t in range(timeout + 1):
                    if car1.row < car2.row:
                        s.add(car2.var[t] - car1.var[t] > 1)
                    else:
                        s.add(car2.var[t] - car1.var[t] < -1)

        if car1.typ != 0 and car2.typ == 0:
            for t in range(timeout + 1):
                i1 = car1.row
                i2 = car1.var[t]

                j1 = car2.var[t]
                j2 = car2.col
                s.add(z3.Not(z3.Or(
                    z3.And(i1 - j1 == 0,
                           j2 - i2 == 0),
                    z3.And(i1 - j1 == 0,
                           j2 - i2 == 1),
                    z3.And(i1 - j1 == 1,
                           j2 - i2 == 0),
                    z3.And(i1 - j1 == 1,
                           j2 - i2 == 1)
                )))
        if car1.typ == 0 and car2.typ != 0:
            for t in range(timeout + 1):
                i1 = car1.var[t]
                i2 = car1.col
                j1 = car2.row
                j2 = car2.var[t]
                s.add(z3.Not(z3.Or(
                    z3.And(i1 - j1 == 0,
                           j2 - i2 == 0),
                    z3.And(i1 - j1 == 0,
                           j2 - i2 == -1),
                    z3.And(i1 - j1 == -1,
                           j2 - i2 == 0),
                    z3.And(i1 - j1 == -1,
                           j2 - i2 == -1)
                )))

# horizontal collides with vertical

# movement
for time in range(1, timeout + 1):
    clauses = []
    for car in car_vars:
        clauses.append((car.var[time] - car.var[time - 1] == 1, 1))
        clauses.append((car.var[time - 1] - car.var[time] == 1, 1))
    s.add(z3.PbEq(clauses, 1))

if s.check() == z3.unsat:
    print("unsat")
    exit()

# print(s.model())
times = [[] for t in range(timeout + 1)]
endtime = 0
for i in s.model():
    k = int(str(i).split('_')[0])
    times[k].append(f"{'_'.join(str(i).split('_')[1:])}_{s.model()[i]}")

for i in range(len(times)):
    for kk in times[i]:
        if str(kk).startswith('2') and str(kk).endswith(str(n - 2)):
            endtime = i
            break
    if endtime != 0:
        break

# print(*times, sep='\n')
for t in range(endtime):
    a, b = 0, 0
    for i in times[t]:
        if i not in times[t + 1]:
            if i.split('_')[0] != '0':
                a = int(i.split('_')[2])
                b = int(i.split('_')[4])
            else:
                a = int(i.split('_')[4])
                b = int(i.split('_')[3])
    for i in times[t + 1]:
        if i not in times[t]:
            if i.split('_')[0] != '0':
                b = max(b, int(i.split('_')[4]))
            else:
                a = max(a, int(i.split('_')[4]))
    print(a, b, sep=',')
