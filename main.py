print("running this script requires BeautifulSoap and matplotlib")
from datetime import datetime
from bs4 import BeautifulSoup
import matplotlib as plt
import csv

outputShows = False

def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

# ------------------------------------------------------------------------------------------ MAKING LISTS ----------------------------------------------------------------------------------------
inputfile = input("Enter animelist file:   ")
file = open("animelist_1625113687_-_9255282.xml", mode='r')
soup = BeautifulSoup(file, 'xml')

name = [str(el.text) for el in soup.find_all("series_title")]
epcount = [int(el.text) for el in soup.find_all("my_watched_episodes")]
seriestype = [str(el.text) for el in soup.find_all("series_type")]
status = [str(el.text) for el in soup.find_all("my_status")]

startdate = [str(el.text) for el in soup.find_all("my_start_date")]
finishdate = [str(el.text) for el in soup.find_all("my_finish_date")]


#Remove unfinished anime
toBeRemoved = []
for m in range(len(epcount)):
    if outputShows:
        print(str(m) + ' - ' +str(name[m])+'   '+str(epcount[m])+' '+str(seriestype[m])+' '+str(status[m])+' '+str(startdate[m])+' '+str(finishdate[m]))
    
    if status[m] == "Plan to Watch" or status[m] == "Watching" or status[m] == "On-Hold" or status[m] == "Dropped":
        if outputShows:
            print("         Status of " + str(name[m]) + " is "+str(status[m])+", removeing from list")
        toBeRemoved.append(m)
        #del epcount[m], seriestype[m], status[m], startdate[m], finishdate[m], name[m]
for ele in sorted(toBeRemoved, reverse = True):
	del epcount[ele], seriestype[ele], status[ele], startdate[ele], finishdate[ele], name[ele]

	
#change start day to datetime format
startdatetime = []
for i in range(len(startdate)):
    
    #if day of month is unspecified (00), change it to 1
    if startdate[i][8] + startdate[i][9] == '00':
        x = list(startdate[i])
        x[9] = '1'
        startdate[i] = "".join(x)
        
    startdatetime.append(datetime.strptime(startdate[i],'%Y-%m-%d'))



#change finish day to datetime format
finishdatetime = []
for i in range(len(finishdate)):
    
    #if day of month is unspecified (00), change it to 28
    if finishdate[i][8] + finishdate[i][9] == '00':
        x = list(finishdate[i])
        x[8] = '2'
        x[9] = '8'
        finishdate[i] = "".join(x)
        
    finishdatetime.append(datetime.strptime(finishdate[i],'%Y-%m-%d'))


for m in range(len(epcount)):
    if outputShows:
        print(str(m) + ' - ' +str(name[m])+'   '+str(epcount[m])+' '+str(seriestype[m])+' '+str(status[m])+' '+str(startdate[m])+' '+str(finishdate[m]))

# ------------------------------------------------------------------------------------------ USING LISTS ----------------------------------------------------------------------------------------
#min and max year
year = []
month={}
    
# Create list of years to find the minimum
for i in range(len(startdatetime)):
    year.append(finishdatetime[i].year)

#Create output table month and year
for currentyear in range(min(year),max(year)+1):
    for i in range(1,13):
        month[str(currentyear)+"-"+str(i)]=0
        
monthLengths={
    1:31,
    2:28,
    3:31,
    4:30,
    5:31,
    6:30,
    7:31,
    8:31,
    9:30,
    10:31,
    11:30,
    12:31}


# For every show, find percent of time in month and add percent of time * number of episodes to month
for i in range(len(startdatetime)):
    class show:
        start = startdatetime[i]
        end = finishdatetime[i]
        length = epcount[i]
    show.startmonth = str(show.start.year)+"-"+str(show.start.month)
    show.completiontime = show.end - show.start
    show.completiontime = int(show.completiontime.days)
    
    if diff_month(show.end,show.start) == 0: # 1 month shows
        month[str(show.startmonth)] = month[str(show.startmonth)] + show.length
        
    elif diff_month(show.end,show.start) == 1: # 2 month shows
        show.endmonth = str(show.end.year)+"-"+str(show.end.month)

        show.timeinstartmonth = datetime(show.start.year, show.start.month, monthLengths[int(show.start.month)],0,0)-show.start
        show.timeinendmonth = show.end - datetime(show.end.year, show.end.month, 1,0,0)

        show.timeinstartmonth = int(show.timeinstartmonth.days)
        show.timeinendmonth = int(show.timeinendmonth.days)

        if outputShows:
            print("\n 2 month show:")
            print("name:"+str(name[i])+"   startdate:"+str(show.start)+"   enddate:"+str(show.end)+"   length:"+str(show.length)+"   time in start month:"+str(show.timeinstartmonth)+"   time in end month:"+str(show.timeinendmonth))
            print((show.timeinstartmonth / show.completiontime)*show.length)
            print((show.timeinendmonth / show.completiontime)*show.length)
            print("\n")
        
        month[str(show.startmonth)] = month[str(show.startmonth)] + ((show.timeinstartmonth / show.completiontime)*show.length)
        month[str(show.endmonth)] = month[str(show.endmonth)] + ((show.timeinendmonth / show.completiontime)*show.length)

    else: # 3+ month shows
        #print("seasonal")
        show.endmonth = str(show.end.year)+"-"+str(show.end.month)

        show.timeinstartmonth = datetime(show.start.year, show.start.month, monthLengths[int(show.start.month)],0,0)-show.start
        show.timeinendmonth = show.end - datetime(show.end.year, show.end.month, 1,0,0)

        show.timeinstartmonth = int(show.timeinstartmonth.days)
        show.timeinendmonth = int(show.timeinendmonth.days)
        
        month[str(show.startmonth)] = month[str(show.startmonth)] + ((show.timeinstartmonth / show.completiontime)*show.length)
        month[str(show.endmonth)] = month[str(show.endmonth)] + ((show.timeinendmonth / show.completiontime)*show.length)

        show.middlemonth = []
        #add name of month to array show.middlemonth
        for x in range(diff_month(show.end,show.start)-1):
            potentialMonth = int(show.start.month)+1+x
            if potentialMonth <= 12:
                show.middlemonth.append(str(show.start.year)+"-"+str(potentialMonth))
            else:
                show.middlemonth.append(str(int(show.start.year)+1)+"-"+str(potentialMonth-12))
        # add time to middle month
        for x in show.middlemonth:
            month[str(x)] = month[str(x)] + ((30 / show.completiontime)*show.length)

#export as csv
with open('output.csv', 'w') as f:
    for key in month.keys():
        f.write("%s,%s\n"%(key,month[key]))
