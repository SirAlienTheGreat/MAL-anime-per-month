from datetime import datetime
from bs4 import BeautifulSoup
import csv
from AnilistPython import Anilist
import time
from colorama import Fore

outputShows = False


def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

anilist = Anilist()

def check_for_seasonal(show, name):
    time.sleep(1)
    if name == "Houkago Teibou Nisshi":
        return True
    #Uses the anilist library to fetch data about the anime
    try:
        anime = anilist.get_anime(name)
    except:
        print(Fore.RED + " ERROR: Couldn't find show \"" + Fore.WHITE + name + Fore.RED + "\"on anilist")
        return True

    ending_date = datetime.strptime(anime["ending_time"],"%m/%d/%Y")
    endDelta = (show.end - ending_date).days

    starting_date = datetime.strptime(anime["starting_time"],"%m/%d/%Y")
    startDelta = (show.start - starting_date).days

    # If the show was finished within 4 days of the last ep and 29 days of the first ep
    if (endDelta >= -4) & (startDelta <= 29):
        return True
    else:
        return False



# ------------------------------------------------------------------------------------------ MAKING LISTS ----------------------------------------------------------------------------------------
try:
    from tkinter import filedialog as fd

    inputfile = fd.askopenfilename()
except:
    print("The GUI file chooser dialog didn't work. Please input it via CLI")
    inputfile = input("Enter animelist file:   ")

file = open(inputfile, mode='r')
soup = BeautifulSoup(file, 'xml')

name = [str(el.text) for el in soup.find_all("series_title")]
epcount = [int(el.text) for el in soup.find_all("my_watched_episodes")]
seriestype = [str(el.text) for el in soup.find_all("series_type")]
status = [str(el.text) for el in soup.find_all("my_status")]
rating = [int(el.text) for el in soup.find_all("my_score")]

startdate = [str(el.text) for el in soup.find_all("my_start_date")]
finishdate = [str(el.text) for el in soup.find_all("my_finish_date")]

# Remove unfinished anime
toBeRemoved = []
for m in range(len(epcount)):
    if outputShows:
        print(str(m) + ' - ' + str(name[m]) + '   ' + str(epcount[m]) + ' ' + str(seriestype[m]) + ' ' + str(
            status[m]) + ' ' + str(startdate[m]) + ' ' + str(finishdate[m]))

    if status[m] == "Plan to Watch" or status[m] == "Watching" or status[m] == "On-Hold" or status[m] == "Dropped":
        if outputShows:
            print("         Status of " + str(name[m]) + " is " + str(status[m]) + ", removeing from list")
        toBeRemoved.append(m)
        # del epcount[m], seriestype[m], status[m], startdate[m], finishdate[m], name[m]
for ele in sorted(toBeRemoved, reverse=True):
    del epcount[ele], seriestype[ele], status[ele], startdate[ele], finishdate[ele], name[ele], rating[ele]

# change start day to datetime format
startdatetime = []
for i in range(len(startdate)):

    # if day of month is unspecified (00), change it to 1
    if startdate[i][8] + startdate[i][9] == '00':
        x = list(startdate[i])
        x[9] = '1'
        startdate[i] = "".join(x)

    startdatetime.append(datetime.strptime(startdate[i], '%Y-%m-%d'))

# change finish day to datetime format
finishdatetime = []
for i in range(len(finishdate)):

    # if day of month is unspecified (00), change it to 28
    if finishdate[i][8] + finishdate[i][9] == '00':
        x = list(finishdate[i])
        x[8] = '2'
        x[9] = '8'
        finishdate[i] = "".join(x)

    finishdatetime.append(datetime.strptime(finishdate[i], '%Y-%m-%d'))

for m in range(len(epcount)):
    if outputShows:
        print(str(m) + ' - ' + str(name[m]) + '   ' + str(epcount[m]) + ' ' + str(seriestype[m]) + ' ' + str(
            status[m]) + ' ' + str(startdate[m]) + ' ' + str(finishdate[m]))

# ------------------------------------------------------------------------------------------ USING LISTS ----------------------------------------------------------------------------------------
# min and max year
year = []
month = {}

# Approximates seasonals by using 3+ month shows with close to the correct amount of time
monthSeasonal = {}

# average consists of a sum and divisor
monthsum = {}  # For calculating length-weighted averages
monthscored = {}  # month dict from above, but excludes unscored items

monthunweightedsum = {}  # where every show is weighted the same, regardless of length
monthdivisor = {}

# Create list of years to find the minimum
for i in range(len(startdatetime)):
    year.append(finishdatetime[i].year)

# Create output table month and year
for currentyear in range(min(year), max(year) + 1):
    for i in range(1, 13):
        month[str(currentyear) + "-" + str(i)] = 0
        monthSeasonal[str(currentyear) + "-" + str(i)] = 0
        monthscored[str(currentyear) + "-" + str(i)] = 0
        monthsum[str(currentyear) + "-" + str(i)] = 0
        monthunweightedsum[str(currentyear) + "-" + str(i)] = 0
        monthdivisor[str(currentyear) + "-" + str(i)] = 0

monthLengths = {
    1: 31,
    2: 28,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31}

seasonals = []
# For every show, find percent of time in month and add percent of time * number of episodes to month
for i in range(len(startdatetime)):
    class show:
        start = startdatetime[i]
        end = finishdatetime[i]
        length = epcount[i]
        score = rating[i]


    show.startmonth = str(show.start.year) + "-" + str(show.start.month)
    show.completiontime = show.end - show.start
    show.completiontime = int(show.completiontime.days)

    if diff_month(show.end, show.start) == 0:  # 1 month shows
        month[str(show.startmonth)] = month[str(show.startmonth)] + show.length

        if show.score != 0:  # Show score 0 means unrated, so these should be excluded
            monthsum[str(show.startmonth)] = monthsum[str(show.startmonth)] + (show.score * show.length)
            monthscored[str(show.startmonth)] = monthscored[str(show.startmonth)] + show.length

            monthunweightedsum[str(show.startmonth)] += (show.score)
            monthdivisor[str(show.startmonth)] += 1

            if outputShows:
                print(Fore.BLUE+ "\n 1 month show:")
                print("name:" + str(name[i]) + "\n  Score:" + str(
                    show.score) + "\n  Amount to add to weighted sum:" + str(
                    show.score * show.length) + "\n  Amount to add to unweighted sum:" + str(
                    show.score) + "\n  Month:" + str(show.startmonth) + Fore.RESET)


    elif diff_month(show.end, show.start) == 1:  # 2 month shows
        show.endmonth = str(show.end.year) + "-" + str(show.end.month)

        show.timeinstartmonth = datetime(show.start.year, show.start.month, monthLengths[int(show.start.month)], 0,
                                         0) - show.start
        show.timeinendmonth = show.end - datetime(show.end.year, show.end.month, 1, 0, 0)

        show.timeinstartmonth = int(show.timeinstartmonth.days)
        show.timeinendmonth = int(show.timeinendmonth.days)

        month[str(show.startmonth)] = month[str(show.startmonth)] + (
                    (show.timeinstartmonth / show.completiontime) * show.length)
        month[str(show.endmonth)] = month[str(show.endmonth)] + (
                    (show.timeinendmonth / show.completiontime) * show.length)

        if show.score != 0:
            monthsum[str(show.startmonth)] = monthsum[str(show.startmonth)] + (
                        (show.timeinstartmonth / show.completiontime) * (show.score * show.length))
            monthsum[str(show.endmonth)] = monthsum[str(show.endmonth)] + (
                        (show.timeinendmonth / show.completiontime) * (show.score * show.length))

            monthscored[str(show.startmonth)] = monthscored[str(show.startmonth)] + (
                        (show.timeinstartmonth / show.completiontime) * show.length)
            monthscored[str(show.endmonth)] = monthscored[str(show.endmonth)] + (
                        (show.timeinendmonth / show.completiontime) * show.length)

            monthunweightedsum[str(show.startmonth)] = monthunweightedsum[str(show.startmonth)] + (
                        (show.timeinstartmonth / show.completiontime) * (show.score))
            monthunweightedsum[str(show.endmonth)] = monthunweightedsum[str(show.endmonth)] + (
                        (show.timeinendmonth / show.completiontime) * (show.score))

            monthdivisor[str(show.startmonth)] = monthdivisor[str(show.startmonth)] + (
            (show.timeinstartmonth / show.completiontime))
            monthdivisor[str(show.endmonth)] = monthdivisor[str(show.endmonth)] + (
            (show.timeinendmonth / show.completiontime))
        if outputShows:
            print(Fore.BLUE+"\n 2 month show:")
            print("Name:" + str(name[i]) + "\n  Score:" + str(show.score) + "\n  Time in start month:" + str(
                show.timeinstartmonth) + "\n  Time in end month:" + str(show.timeinendmonth))
            print("Score to add to weighted start sum first month " + str(
                ((show.timeinstartmonth / show.completiontime) * (show.score * show.length))))
            print("Score to add to weighted start sum second month " + str(
                (show.timeinendmonth / show.completiontime) * (show.score * show.length)))
            print("Score to add to unweighted start sum first month " + str(
                (show.timeinstartmonth / show.completiontime) * (show.score)))
            print("Score to add to unweighted start sum second month " + str(
                (show.timeinendmonth / show.completiontime) * (show.score)))
            print("Time to add to unweighted first month divisor" + str((show.timeinstartmonth / show.completiontime)))
            print("Time to add to unweighted second month divisor" + str((show.timeinendmonth / show.completiontime))+Fore.RESET)


    else:  # 3+ month shows
        isSeasonal = False
        if check_for_seasonal(show, str(name[i])):
            isSeasonal = True
            seasonals.append(str(name[i]))
            print(Fore.GREEN+str(name[i]) + " Is a seasonal show" + Fore.RESET)
        else:
            print(Fore.RED +str(name[i]) + " Is NOT a seasonal show" + Fore.RESET)

        show.endmonth = str(show.end.year) + "-" + str(show.end.month)

        show.timeinstartmonth = datetime(show.start.year, show.start.month, monthLengths[int(show.start.month)], 0,
                                         0) - show.start
        show.timeinendmonth = show.end - datetime(show.end.year, show.end.month, 1, 0, 0)

        show.timeinstartmonth = int(show.timeinstartmonth.days)
        show.timeinendmonth = int(show.timeinendmonth.days)

        month[str(show.startmonth)] = month[str(show.startmonth)] + (
                    (show.timeinstartmonth / show.completiontime) * show.length)
        month[str(show.endmonth)] = month[str(show.endmonth)] + (
                    (show.timeinendmonth / show.completiontime) * show.length)

        if isSeasonal:
            if show.timeinstartmonth > 7:
                print(show.timeinstartmonth)
                monthSeasonal[str(show.startmonth)] += ((show.timeinstartmonth / show.completiontime) * show.length)
                # This was a flawed algorithm. I intended to not count eps watched before starting (i.e. if you start a show on ep 3, skip ep 1 and 2)
                #monthSeasonal[str(show.startmonth)] = monthSeasonal[str(show.startmonth)] + (show.timeinstartmonth/7)
                #print(Fore.BLUE + "For show " +Fore.WHITE+str(name[i]) + ", " + str(show.timeinstartmonth/7) + "eps were spend in start month")
            if show.timeinendmonth > 7:
                monthSeasonal[str(show.endmonth)] += ((show.timeinendmonth / show.completiontime) * show.length)
                #monthSeasonal[str(show.endmonth)] = monthSeasonal[str(show.endmonth)] + (show.timeinendmonth / 7)
                #print(Fore.BLUE + "For show " +Fore.WHITE+str(name[i]) + ", " + str(show.timeinendmonth/7) + "eps were spend in end month")
                


        if show.score != 0:
            monthsum[str(show.startmonth)] += (
                        (show.timeinstartmonth / show.completiontime) * (show.score * show.length))
            monthsum[str(show.endmonth)] += ((show.timeinendmonth / show.completiontime) * (show.score * show.length))

            monthscored[str(show.startmonth)] += ((show.timeinstartmonth / show.completiontime) * show.length)
            monthscored[str(show.endmonth)] += ((show.timeinendmonth / show.completiontime) * show.length)

            monthunweightedsum[str(show.startmonth)] += ((show.timeinstartmonth / show.completiontime) * (show.score))
            monthunweightedsum[str(show.endmonth)] += ((show.timeinendmonth / show.completiontime) * (show.score))

            monthdivisor[str(show.startmonth)] += ((show.timeinstartmonth / show.completiontime))
            monthdivisor[str(show.endmonth)] += ((show.timeinendmonth / show.completiontime))

        show.middlemonth = []
        # add name of month to array show.middlemonth
        for x in range(diff_month(show.end, show.start) - 1):
            potentialMonth = int(show.start.month) + 1 + x
            if potentialMonth <= 12:
                show.middlemonth.append(str(show.start.year) + "-" + str(potentialMonth))
            else:
                show.middlemonth.append(str(int(show.start.year) + 1) + "-" + str(potentialMonth - 12))
        # add time to middle month
        for x in show.middlemonth:
            month[str(x)] = month[str(x)] + ((30 / show.completiontime) * show.length)
            if isSeasonal:
                monthSeasonal[str(x)] += ((30 / show.completiontime) * show.length)
                # Also flawed algorithm - The rest of the program works with the (somewhat flawed) assumption
                # that shows are distributed smoothly. This matches the inaccuracy with the rest.
                #monthSeasonal[str(x)] = monthSeasonal[str(x)] + 4
            if show.score != 0:
                monthsum[str(x)] += ((30 / show.completiontime) * (show.score * show.length))
                monthscored[str(x)] += ((30 / show.completiontime) * show.length)

                monthunweightedsum[str(x)] += ((30 / show.completiontime) * (show.score))
                monthdivisor[str(x)] += ((30 / show.completiontime))

        if outputShows:
            print(Fore.BLUE+"\n 3+ month show:")
            print("days spent watching: " + str((show.end - show.start).days))
            print("name:" + str(name[i]) + "   startdate:" + str(show.start) + "   enddate:" + str(
                show.end) + "   middle months are:" + str(show.middlemonth) + "   length:" + str(
                show.length) + "   time in start month:" + str(show.timeinstartmonth) + "   time in end month:" + str(
                show.timeinendmonth))
            print((show.timeinstartmonth / show.completiontime) * show.length)
            print((show.timeinendmonth / show.completiontime) * show.length)
            print("\n"+Fore.RESET)

# export as csv
with open('output.csv', 'w') as f:
    writerfile = csv.writer(f)
    writerfile.writerow(["Month", "Episodes watched", "Of which were seasonal", "Length-weighted average score", "Unweighted average score"])
    for key in month.keys():
        if float(monthdivisor[key]) == 0:
            writerfile.writerow([key, month[key], monthSeasonal[key], 0, 0])
        else:
            writerfile.writerow([key, month[key], monthSeasonal[key], str(monthsum[key] / monthscored[key]),
                                 str(monthunweightedsum[key] / monthdivisor[key])])
