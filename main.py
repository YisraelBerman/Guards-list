import random # for shuffle
import pandas as pd # for working with database
from shutil import copy # create backup
from datetime import datetime, timedelta # for handling the date in the check
shifts = ["10:00-13:00", "13:00-16:00", "16:00-19:00", "19:00-22:00", "22:00-1:00", "1:00-4:00", "4:00-7:00", "7:00-10:00"]
ROWS = len(shifts)
COLUMNS = 6 # number of positions * 2
NONIMPORTENTPOSITION = 6
LESSIMPORTENTSHIFT = [0, 7, 1, 5, 4, 3]
NEXTCOLMUN = 9


def create(day):
    database = {"date": [f"{day}" for a in range(ROWS)], "shift": shifts, "Gate 1": [0 for a in range(ROWS)], "Gate 2": [0 for a in range(ROWS)], "East 1": [0 for a in range(ROWS)], "East 2": [0 for a in range(ROWS)], "West 1": [0 for a in range(ROWS)], "West 2": [0 for a in range(ROWS)]} #, 'LookOut 1': [0 for a in range(ROWS)], 'LookOut 2': [0 for a in range(ROWS)]
    mylist = pd.DataFrame(database)
    mylist.to_csv(f"{day}.csv", index=False)


#check how many shifts can you have and mark the extras a empty "ריק"
def num_shifts(df, guardlist):
    total_shifts = ROWS * COLUMNS
    #checks how many positions have been taken already by volunteers
    full_counter = 0
    for i in range(ROWS):
        for j in range(COLUMNS):
            try:
                kuku = int(df.iat[i, j+2])
            except:
                full_counter += 1
    print(total_shifts, full_counter, len(guardlist)*2)

    extra = total_shifts - full_counter - (len(guardlist) * 2)
    #if 0 or less it means we have enough for all positions. if more then 0 we need empty positions
    if extra <= 0:
        print("enjoy the air!")
        return df
    else:
        extra = extra // 2 + 2
        #mark empty by importance order
        for i in range(extra):
            df.iat[LESSIMPORTENTSHIFT[i], NONIMPORTENTPOSITION + 2] = "ריק"
            df.iat[LESSIMPORTENTSHIFT[i], NONIMPORTENTPOSITION + 3] = "ריק"
        return df


#adds names by order to table
def add_names(df, counter, guard_list):
    for i in range(ROWS):
        for j in range(COLUMNS):
                #an empty cell can be casted to int
            try:
                kuku = int(df.iat[i, j + 2])
                df.iat[i, j + 2] = guard_list[counter % len(guard_list)]
                counter += 1
            except:
                pass
    print("first of tomorrow: ", guard_list[counter % len(guard_list)])
    return df, counter % len(guard_list)


def night_shift(df,day):
    df = pd.read_csv(f"{day}.csv")
    myguardslist = pd.read_csv('guards.csv')
    row_list = df.loc[5, :].values.flatten().tolist()
    counter = 0
    for x in range(COLUMNS):
        name = myguardslist.at[x, "1-4 two night ago"]
        if name in row_list and name != "סייר - נתנאל" and name != "ריק":
            print(name, 'was two nights ago\n')
            counter += 1
        name = myguardslist.at[x, "1-4 last night"]
        if name in row_list and name != "סייר - נתנאל" and name != "ריק":
            print(name, 'was last night\n')
            counter += 1

    if counter != 0:
        #list who can be a replacment
        allguards = myguardslist["guards"].values.tolist()
        guards_night_count = myguardslist["1-4 all"].values.tolist()
        # Using zip to pair elements from column1 and column2
        pairs = zip(allguards, guards_night_count)
        
        # Creating a dictionary from the pairs
        night_count_dict = dict(pairs)
        
        print("---------\nPossible switchs:\n22:00 shift: ")
        row_list = df.loc[4, :].values.flatten().tolist()
        last_night_shift = myguardslist["1-4 last night"].values.tolist()
        two_nights_ago_shift = myguardslist["1-4 two night ago"].values.tolist()
        for x in row_list:
            if x not in last_night_shift and x not in two_nights_ago_shift:
                try:
                    print(x, "  ", night_count_dict[x])
                except:
                    print(x)
        print("4:00 shift:")
        row_list = df.loc[6, :].values.flatten().tolist()
        #last_night_shift = myguardslist["1-4 last night"].values.tolist()
        #two_nights_ago_shift = myguardslist["1-4 two night ago"].values.tolist()
        for x in row_list:
            if x not in last_night_shift and x not in two_nights_ago_shift:
                try:
                    print(x,"  ", night_count_dict[x])
                except:
                    print(x)
        #TODO fix automaticly
    else:
        print("Night shift is OK")

    return df


def shuffle(df):
    for i in range(ROWS):
        row_list = df.loc[i, :].values.flatten().tolist()
        row_list = row_list[2:]
        if row_list[COLUMNS-1] == "ריק":
            row_list = row_list[:COLUMNS-2]

        fixed = [(pos, item) for (pos, item) in enumerate(row_list) if str(item).startswith(("א ", "מ ", "ריק", "--"))]

        #fixed = [(pos, item) for (pos, item) in enumerate(row_list) if (str(item).startswith("א ") or str(item).startswith("מ ")  or str(item).startswith("ריק") or str(item).startswith("--"))]
        # shuffle list
        random.shuffle(row_list)
        # swap fixed elements back to their original position
        for pos, item in fixed:
            index = row_list.index(item)
            row_list[pos], row_list[index] = row_list[index], row_list[pos]

        for n in range(len(row_list)):
            df.iat[i,n+2] = row_list[n]
        #TODO check if previos shift was in same position
    return df


def update(day):
    df = pd.read_csv(f"{day}.csv")
    myguardslist = pd.read_csv('guards.csv')
    guards_list = myguardslist["guardsToday"].values.tolist()
    guards_list = [name for name in guards_list if name != 'q']
    #TODO make checking first automatic
    next = int(input("Who is first for tomorrow? "))
    myguardslist.iat[1, NEXTCOLMUN] = guards_list[next]
    i = myguardslist.set_index('guards').index.get_loc(guards_list[next])
    myguardslist.iat[0, NEXTCOLMUN] = i

    row_list = df.loc[5, :].values.flatten().tolist()
    row_list = row_list[2:]
    for x in range(COLUMNS):
        myguardslist.at[x, "1-4 two night ago"] = myguardslist.at[x, "1-4 last night"]
        myguardslist.at[x, "1-4 last night"] = row_list[x]

    # add to 1-4 shift counter
    for x in range(COLUMNS):
        try:
            i = myguardslist.set_index('guards').index.get_loc(row_list[x])
            myguardslist.at[i, '1-4 all'] = int(myguardslist.at[i, '1-4 all']) + 1
        except:
            pass

    myguardslist.to_csv('guards.csv', index=False)   


def checkOK(day):
    print("checking")
    df = pd.read_csv(f"{day}.csv")
    good = True

    f = '%d_%m'
    res = (datetime.strptime(day, f) - timedelta(days=1)).strftime(f)
    df2 = pd.read_csv(f"{res}.csv")
    df2 = df2[-3:]
    df = pd.concat([df2, df.loc[:]]).reset_index(drop=True)
    #df.to_csv("big.csv", index=False)

    good = True
    rows = []
    for i in range(ROWS + 3):
        row_list = df.loc[i, :].values.flatten().tolist()
        row_list = row_list[2:]
        rows.append([name for name in row_list if name != 'ריק'])

    end = len(rows) - 1
    counter = 0
    for i in rows:
        for j in i:
            if counter < end and j in rows[counter + 1]:
                print("way too close - no break ", j)
                good = False
            if counter < end - 1 and j in rows[counter + 2]:
                good = False
                print("too close, only 3 hour break: ", j)
            if counter < end -2 and j in rows[counter + 3]:
                print("only 6 hour break: ",j)
                good = False

        counter += 1
    if good:
      print("Breaks between shifts are all good")
    night_shift(df, day)


def generate(day):
    copy(f"{day}.csv", "backup.csv")
    mylist = pd.read_csv(f"{day}.csv")
    myguardslist = pd.read_csv('guards.csv')
    guards_list = myguardslist["guardsToday"].values.tolist()
    next = int(float(myguardslist.iat[0, NEXTCOLMUN])) #starting point in guard list
    guards_list = [name for name in guards_list if name != 'q']
    #mylist = num_shifts(mylist, guards_list) #check if enough guards for all shifts

    mylist, next = add_names(mylist, next, guards_list) # fill up table
    #mylist.to_csv("beforeshuffle.csv", index=False)
    mylist = shuffle(mylist)

    mylist.to_csv(f"{day}.csv", index=False)

    print(next, guards_list[next])
    myguardslist.to_csv('guards.csv', index=False)
    checkOK(day)


if __name__ == '__main__':

    day = input("enter the date: ")
    x = 5

    while x not in [0,1,2,3]:
        menu = ("Choose what to do:\n"
                "   0) Create new table\n"
                "   1) Generate\n"
                "   2) Check\n"
                "   3) update files - not ready yet\n      ")
        x = int(input(menu))
    func_list = [create, generate, checkOK, update]
    func_list[x](day)


    #create guards file
    #data = {"today guards": [], "guards": " ", "1-4 all": " ", "1-4 latt night": " ", "1-4 two night ago": " "}
    #daf = pd.DataFrame(data)
    #daf.to_csv("guards.csv")



