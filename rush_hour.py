import sys
import z3

if __name__ == '__main__':
    # read the file provided as command line argument
    file = list(map(str.strip, open("inp.txt", "r").readlines()))
    n, k = map(int, file[0].split(','))
    red_car = list(map(int, file[1].split(',')))
    cars = []
    mines = []
    initial_car_pos = {}
    for lines in file[2:]:
        if lines.split(',')[0] != '2':
            cars.append(list(map(int, lines.split(','))))
        else:
            mines.append(list(map(int, lines.split(',')))[1:])
    print("check1")
    # k -0 vertical k-1 horizontal k-2 red
    vars = [[[[[],[],[]] for j in range(n)]for _ in range(n)] for l in range(0, k+1)]
    s = z3.Solver()
    initial_car_pos['*'] = [red_car[0],red_car[1]]
    for time in range(0, k+1):
        all_pos = []
        this_car_pos = []
        for i in range(n):
            for j in range(n):
                vars[time][i][j][2]=z3.Bool(f"*_2_{i}_{j}_{time}")   
                this_car_pos.append((vars[time][i][j][2],1))
        for i in range(n):
            for j in range(n):
                if time==0 and i!=red_car[0] and j!=red_car[1]:
                    s.add(z3.Not(vars[time][i][j][2]))
                if j < n-1:
                    # all_pos.append((z3.And(vars[f"*_2_{i}_{j}_{time}"], vars[f"*_2_{i}_{j+1}_{time}"]),1))
                    all_pos.append((z3.And(vars[time][i][j][2],vars[time][i][j+1][2]), 1))
        if time==0:
            s.add(vars[time][red_car[0]][red_car[1]][2])
        s.add(z3.PbEq(tuple(all_pos), 1))
        s.add(z3.PbEq(tuple(this_car_pos), 2))
    print("check2")
    
    # k -0 vertical k-1 horizontal k-2 red

    for id, car in enumerate(cars):
        initial_car_pos[id] = [car[1],car[2]]
        for time in range(0, k+1):
            all_pos = []
            my_pos=0
            this_car_pos = []
            for i in range(n):
                for j in range(n):
                    my_pos = len(vars[time][i][j][car[0]])
                    vars[time][i][j][car[0]].append(z3.Bool(f"{id}_{car[0]}_{i}_{j}_{time}"))
                    this_car_pos.append((vars[time][i][j][car[0]][my_pos],1))
            if time==0:
                s.add(vars[time][car[1]][car[2]][car[0]][my_pos])
            for i in range(n):
                for j in range(n):
                    if time==0 and i!=car[1] and j!=car[2]:
                        s.add(z3.Not(vars[time][i][j][car[0]][my_pos]))
                    if car[0] == 0:
                        if i < n-1:
                            # print(vars[time][i][j][car[0]])
                            # print(vars[time][i+1][j][car[0]])
                            all_pos.append((z3.And(vars[time][i][j][car[0]][my_pos], vars[time][i+1][j][car[0]][my_pos]), 1))
                    else:
                        if j < n-1:
                            all_pos.append((z3.And(vars[time][i][j][car[0]][my_pos], vars[time][i][j+1][car[0]][my_pos]),1))
            # 2 adjacent positions true for for each car at all instants # adjacent ensured
            s.add(z3.PbEq(tuple(all_pos), 1))
            s.add(z3.PbEq(tuple(this_car_pos), 2))
    print("check3")
    
    goal = []
    for time in range(0, k+1):
        goal.append(z3.And(vars[time][red_car[0]][n-1][2],vars[time][red_car[0]][n-2][2]))
    s.add(z3.Or(goal))

    # no car at mines ever
    for mine in mines:
        for time in range(0, k+1):
            i = mine[0]
            j = mine[1]
            s.add(z3.Not(vars[time][i][j][2]))
            for type in range(2):
                for k_ in vars[time][i][j][type]:
                    s.add(z3.Not(k_))

    # two cars never at same position at any instant
    for time in range(0, k+1):
        for i in range(n):
            for j in range(n):
                clauses = [vars[time][i][j][2]]
                for type in range(2):
                    for k_ in vars[time][i][j][type]:
                        clauses.append(k_)
                s.add(z3.AtMost(*clauses, 1))
    print("check4")
    
    # ensure exactly 1 car moves by 1 unit at each instant (given red has not reached n-1)
    for time in range(1, k+1):
        clauses = []
        change_instant=[]
        for i in range(n):
            for j in range(n):
                change_instant.append((z3.Xor(vars[time-1][i][j][2], vars[time][i][j][2]),1))
                if 0<j<n-1:
                    red_move = z3.And(vars[time-1][i][j-1][2],vars[time-1][i][j][2], vars[time][i][j][2],vars[time][i][j+1][2])
                    red_move_back = z3.And(vars[time-1][i][j][2],vars[time-1][i][j+1][2], vars[time][i][j][2],vars[time][i][j-1][2])
                    clauses.append((red_move,1))
                    clauses.append((red_move_back,1))
                for type in range(2):
                    for k_ in range(len(vars[time][i][j][type])):
                        change_instant.append((z3.Xor(vars[time-1][i][j][type][k_], vars[time][i][j][type][k_]),1))
                        if type==0: # vertical
                            if i<n-1:
                                vert_move = z3.And(vars[time-1][i-1][j][type][k_],vars[time-1][i][j][type][k_], vars[time][i][j][type][k_] ,vars[time][i+1][j][type][k_])
                                vert_move_back = z3.And(vars[time-1][i][j][type][k_],vars[time-1][i+1][j][type][k_], vars[time][i][j][type][k_] ,vars[time][i-1][j][type][k_])
                                clauses.append((vert_move,1))
                                clauses.append((vert_move_back,1))
                        else:
                            if j<n-1:
                                hor_move = z3.And(vars[time-1][i][j-1][type][k_],vars[time-1][i][j][type][k_],vars[time][i][j][type][k_] ,vars[time][i][j+1][type][k_])
                                hor_move_back = z3.And(vars[time-1][i][j][type][k_],vars[time-1][i][j+1][type][k_],vars[time][i][j][type][k_] ,vars[time][i][j-1][type][k_])
                                clauses.append((hor_move,1))
                                clauses.append((hor_move_back,1))
        # s.add(z3.PbLe(tuple(clauses), 1))
        s.add(z3.PbEq(clauses, 1))
        s.add(z3.PbEq(change_instant, 2))
    print("check5")
        # print(clauses)
    

    # vars= [[[[z3.Bool(f"{i}_{j}_{type}_{time}") for i in range(n)] for j in range(n)] for type in range(3)] for time in range(k)]

    # var_red = [[[z3.Bool(f"{cols}_{rows}_{time}") for cols in range(n)] for rows in range(n)] for time in range(k)]
    # var_others = []


