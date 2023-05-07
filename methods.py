import pandas as pd

"""
This method is what I used to split the long strings representing the individual hours into a list of one hour blocks

Parameters
----------
hours : string
    represent the long string of hours that the individual is available that day
    
Returns
----------
ans : list 
    a list of 1 hour blocks that the individual is available that day
"""
def listSplit(hours):
    ans = []
    for timeBlock in hours:
        timeBlock = timeBlock.replace(" ", "")
        if(timeBlock[:2] == "11" or timeBlock[:2] == "12" or timeBlock[:2] == "10"):
            timeBlock = timeBlock[:2]
        else:
            timeBlock = timeBlock[:1]
        ans.append(timeBlock)
    return ans

"""
This method is used to get rid of all the extra characters in the strings so that only the start hour is listed

Parameters
----------
mentees : pandas dataframe
    This represents the mentee dataset which contains all the listed hours they are available for the week
    
days : list
    The days that the office is running IMP meetings during that quarter
    
Return
----------
mentees : pandas dataframe 
    This will be the updated dataset which will shave off all the extra characters. EX:(9:00am - 10:00am) -> 9
"""
def hourCleanUp(mentees, days):
    counter = 0
    #might not be nec. anymore -> was using this to get around the numpy float var type that was messing up conversions
    mentees = mentees.fillna("fix THIS")
    for individual in mentees['Name']:
        for day in days:
            elem = mentees.at[mentees.index[counter], day]
            if(elem == "fix THIS"):
                mentees.at[mentees.index[counter], day] = []
                continue
            elem = elem.split(",")
            mentees[day][counter] = listSplit(elem)
        counter += 1
    return mentees

"""
This method is used to properly setup our schedule for the next wave of students. Each slot in schedule has three different values it can
take. The first is just an empty cell which means that there was no availability provided that day by our mentors. The second can be a pair
which we can tell by if there is a comma in the string. This means that that time slot is already accounted for so we should'nt try to
schedule another meeting during that (time, room). The last possible scenario is that there is just a mentor listed. This means that the room is still open so we can try to look for a mentee for that hour.

Parameters
----------
schedule : pandas dataframe
    The current iteration of the schedule which will contain all mentor slots as well as any pairs that have already been made in previous runs.
    
Return
----------
schedule : pandas dataframe
    A updated schedule which will be prepared to take in the next wave of students
"""
def scheduleSetUp(schedule):
    #grabs all the days and rooms open this quarter
    roomAvail = schedule.columns.tolist()
    roomAvail.pop(0)
    timeBlocks = schedule['Time'].tolist()
    
    schedule = schedule.fillna('')
    
    for room in roomAvail:
        counter = 0
        for hour in timeBlocks:
            tmp = schedule[room][counter]
            tmp = tmp.replace("[", "")
            tmp = tmp.replace("]", "")
            tmp = tmp.replace("'", "")
            tmp = tmp.strip()
            #catches when the hour block is empty
            if(schedule[room][counter] == ''):
                schedule[room][counter] = []
                counter += 1
            #catches when there is already a pair at this hour block
            elif (tmp.find(",") != -1):
                schedule[room][counter] = tmp
                counter += 1
            #catches when there is just a mentor listed
            else:
                tmpList = [tmp]
                schedule[room][counter] = tmpList
                counter += 1
    return schedule

"""
This method will sort the dataframe such that the users with the least amount of availability are at the top of the list

Parameters
----------
mentees : pandas dataframe
    The current wave of mentees that we are working with.
days : list
    The days that the office is running imp meetings that day
    
Return
----------
    mentees - A updated version of the mentees dataset which will have the mentees ordered in ascending order in terms of their availability.
"""
def sortFrame(mentees, days):
    for day in days:
        dayLength = []
        for elem in mentees[day]:
            dayLength.append(len(elem))
        mentees[day + " length"] = dayLength

    #Now that we have that we sum over all the days and sort by that
    dayLengths = []
    for day in days:
        tmpString = day + " length"
        dayLengths.append(tmpString)
    
    
    totals = []
    for index, row in mentees.iterrows():
        tmp = 0
        for lengths in dayLengths:
            tmp = tmp + row[lengths]
        totals.append(tmp)
    mentees["totals"] = totals


    #Sort by totals
    mentees = mentees.sort_values(by = "totals")

    #Now we can drop all the extra columns we created
    mentees = mentees.iloc[:,:-(len(days) + 1)]
    
    mentees = mentees.reset_index()
    mentees = mentees.drop(['index'], axis=1)
    return mentees

"""
This is the main algo that will do the matching for the students looking for the first availbility in our schedule from the begining to the end of the week.
Currerntly working on making it to where we dont search from begining to end of week for every student. Instead each student will be indexed and all odd will go from the begining and even from the end. This is being done to avoid booking all the earlier day slots for the earlier waves since this can be problematic for the later waves.
Parameters 
----------
mentees : pandas dataframe
    A dataframe that contains all of the mentees/students that we will be assigning in this wave. It contains their avail.
    
days : list
    The days that we are running IMP meetings for that quarter
    
daysSched : list
    The rooms we will have open for the days that we are open that quarter
    
schedule : pandas dataframe
    The current iteration of our schedule -> a dataframe that contains all of the current pairs and openings.
    
mentorCapacity : dictionary(mentorName, # of students they have)
    A dictionary that contains all of the mentors and the amount of students they have been assigned
    
TheMagicNumver : int
    The max amount of mentees that we want a mentor to have after taking this current wave into account
    
Return 
----------
schedule : pandas dataframe
    The updated schedule with all of the pairs that we matched for that wave of students
    
extras : pandas dataframe
    A new dataframe that contains all of the students that we weren't able to accomadate for that wave.
    
mentorCapacity : dictionary 
    The updated dictionary that now reflects all of the new pairs that we made for this current wave of students.
"""
def mainAlgo(mentees, days, daysSched, schedule, mentorCapacity, TheMagicNumber):
    room_schedule = {room: [item for item in schedule if room in item] for room in set(item.split("(")[1].strip(")").strip() for item in                          schedule)}
    
    newDaysSched = [item for room in sorted(room_schedule.keys()) for item in room_schedule[room]]

    revDaysSched = [newDaysSched[i:i+5] for i in range(0, len(newDaysSched), 5)]
    revDaysSched = [elem for set_ in reversed(revDaysSched) for elem in set_]
    revDaysSched = revDaysSched[::-1]
    extras = pd.DataFrame()
    menteeCounter = 0
    menteeDict = {name: 0 for name in mentees['Name']}
    
    #Start looking at each mentee and when they're available
    index = 0
    for mentee in mentees['Name']:
        matchFound = False
        for day in days:
            #grabs the hours they are avail on "day" and catches when they have no avail for "day"
            menteeHours = mentees.at[mentees.index[menteeCounter], day]
            if(menteeHours == []):
                continue
            
            #Now need to check schedule on those days and times to see if avail
            #dayStub -> Monday -> Mon
            dayStub = day[:3]
            #daysSched has all rooms for all days saved -> Mon(room 1), Mon(room 2), Mon(room 3), ...

            #tries to even out the distribution of scheduling so that monday not so packed
            if index % 2 == 0:
                tmpDaysSched = daysSched
            else:
                tmpDaysSched = revDaysSched
            
            for daySch in tmpDaysSched:
                if dayStub in daySch:
                    for hour in menteeHours:
                        
                        tmp = schedule.at[int(hour), daySch]
                        if(len(tmp) == 0 or type(tmp) != list or tmp[0] == ''):#len(tmp) == 0
                            continue
                        #catches when there's a opening and our mentor isn't overbooked so we break out of schedule loop
                        if(len(tmp) == 1 and mentorCapacity[tmp[0]] < TheMagicNumber and menteeDict[mentee] < 1):
                            tmp.append(mentee)
                            matchFound = True
                            mentorCapacity[tmp[0]] += 1
                            menteeDict[mentee] += 1
                            break
                #if(matchFound == True):
                    #break
            index += 1
        if(menteeDict[mentee] == 0):
            tmpRow = mentees.loc[mentees['Name'] == mentee]
            extras = extras.append(tmpRow, ignore_index = True)
        menteeCounter += 1
    return (schedule, extras, mentorCapacity)

"""
This method is used to double check that we don't book a student during their scheduled seminar section time. This is because students will sometimes list their seminar time in their availbility for IMP.

Parameters
----------
mentees : pandas dataframe
    The current wave of mentees that we are working with.
    
days : list
    The days that we are holding meetings that week
    
Return
----------
mentees : pandas dataframe
    The updated mentees dataframe that will have cleaned any mistakes where students indicated they were free during their seminar section
"""    
def seminarClean(mentees, days):
    counter = 0
    for semStatus in mentees["Seminar Status"]:
        #grabs the hour time that the student is booked
        semHour = semStatus[8:10]
        semHour = semHour.replace(":", "")
        
        if(semStatus == "I completed Seminar in a previous term."):
            counter += 1
            continue
        
        #searches for our day substring in the students seminar status
        for day in days:
            if day in semStatus:
                semDay = day
        
        elem = mentees.at[mentees.index[counter], semDay]
        if semHour in elem:
            elem.remove(semHour)
            mentees.at[mentees.index[counter], semDay] = elem
        counter += 1
    return mentees

"""
Sets up our dictionary that tracks the mentors and the assigned students that each mentor has already been assigned.

Parameters 
----------
mentors : pandas dataframe
    A list containing all of the mentors names
    
Return 
----------
mentorCapacity - dictionary
    A dictionary that contains all of the mentors names as keys and 0 as values since they haven't been assigned any students
"""
def mentorCapacitySetUp(mentors, daysSched, hours, schedule):
    mentorCapacity = {}
    for name in mentors:
        name = name.strip()
        mentorCapacity[name] = 0
    
    #searches for any pairs we already made
    for day in daysSched:
        for hour in hours:
            tmp = schedule[day][hour]
            #Catches when there is nothing there
            if(type(tmp) == list):
                continue
            tmpList = tmp.split(",")
            mentorName = tmpList[0]
            mentorName = mentorName.strip()
            mentorCapacity[mentorName] += 1

    return mentorCapacity

"""
Gathers all of the remaining time slots in the schedule that still have a mentor available.
Parameters 
----------
daysSched : list
    All of the rooms that are available for the days that we are running IMP meetings that quarter
    
timeBlocks : list
    All of the hours that we will be running meetings for the quarter
    
schedule : pandas dataframe
    The current schedule that maps out all of the mentor avail we have for that quarter

Return
----------
remainingSlots : list
    A list that contains all of the open slots in our current iteration of the schedule
"""
def gatherRemainingSlots(daysSched, timeBlocks, schedule):
    remainingSlots = []
    for day in daysSched:
        for hour in timeBlocks:
            tmp = schedule.loc[hour][day]
            if(type(tmp) == list and tmp[0] != ''):
                tmpTuple = tmp[0], hour, day
                remainingSlots.append(tmpTuple)
    return(remainingSlots)

"""
Checks to see if any of the open slots are adjacent to each other. For example mentor 1 is available in Room1 on Tuesdays and mentor 2 is also available in Room2 on Tuesdays then they will be paired together in a tuple to be schedueled later on.

Parameters 
----------
remainingSlots : list
    A list of all the open slots in the current iteration of the schedule
    
mentorCapacity : dictionary
    A dictionary that contains all of the mentors and the amount of the students they've already been assigned.
    
Return 
----------
pairs : list
    A list of tuples that contains all of the examples in the schedule where two mentors with listed availability at the same time can be grouped together
"""
def initialPairUp(remainingSlots, mentorCapacity):
    pairs = []
    for mentorAvail in remainingSlots:
        mentorName = mentorAvail[0]
        time = mentorAvail[1]
        dayRoom = mentorAvail[2][:3]
        for innerMentorAvail in remainingSlots:
            innerMentorName = innerMentorAvail[0]
            innerTime = innerMentorAvail[1]
            innerDayRoom = innerMentorAvail[2][:3]
            #makes sure that we dont match a mentor with themselves
            if(mentorName == innerMentorName):
                continue
            if(time == innerTime and dayRoom == innerDayRoom 
               and mentorCapacity.get(mentorName) < 1 and mentorCapacity.get(innerMentorName) < 1):
                #This means that this can be a pair
                pairs.append((mentorAvail, innerMentorAvail))
                mentorCapacity[mentorName] += 1
                mentorCapacity[innerMentorName] += 1
                break
    return(pairs)

"""
Updates the schedule to where all of the pairs in our pairs list is implemented into the schedule

Parameters 
----------
pairs : list
    A list of tuples that contains all of the examples in the schedule where two mentors with listed availability at the same time can be grouped together
    
schedule : pandas dataframe
    The current iteration of the schedule 
    
mentorCapacity : dictionary
    The dictionary that represents how many students each mentor has 
    
Return 
----------
schedule : pandas dataframe
    The updated iteration of the schedule that contains all of the pairs we had collected before hand
"""
def initialPairScheduleUpdate(pairs, schedule, mentorCapacity):
    #This grabs the priority room and makes sure to delete the mentor from the other room before pairing them            
    for elem in pairs:
        roomA = int(elem[0][2][-2:-1])
        roomB = int(elem[1][2][-2:-1])
        if(roomA < roomB):
            finalRoom = elem[0][2]
            deleteRoom = elem[1][2]
        else:
            finalRoom = elem[1][2]
            deleteRoom = elem[0][2]
        schedule.at[elem[0][1], finalRoom] = elem[0][0] + ", " + elem[1][0]
        schedule.at[elem[0][1], deleteRoom] = []
    return(schedule, mentorCapacity)

"""
The main mentor algorithm that does all of the extra matching based off of the avail that the mentors provided in the mentee enrollment form and the slots that are still open in the current iteration of the schedule.

Parameters
----------
mentors : list
    A list of all the mentors that are taking on students that quarter
    
schedule : pandas dataframe
    The current iteration of the schedule
    
daysSched : list
    The rooms that are avail for the days that we are running IMP that quarter
    
mentees : pandas dataframe
    A dataframe containing the mentees info from names to avail
    
mentorCapacity : dictionary
    The dictionary that represents how many students each mentor has
    
TheMagicNumber : int
    The max amount of students we want an individual mentor to have after factoring in this wave

Return
----------
schedule : pandas dataframe
    The updated iteration of the schedule

mentorCapacity : dictionary
    The dictionary that represents how many students each mentor has
"""
def mainMentorAlgo(mentors, schedule, daysSched, mentees, mentorCapacity, TheMagicNumber):
    #setup
    timeBlocks = list(schedule.index.values)
    
    #gathers all the slots in the schedule that arent paired yet
    remainingSlots = gatherRemainingSlots(daysSched, timeBlocks, schedule)  
    
    #out of all the remaining slots we search to see if any of them can be paired up           
    pairs = initialPairUp(remainingSlots, mentorCapacity)       
    

    #This grabs the priority room and makes sure to delete the mentor from the other room before pairing them            
    schCap = initialPairScheduleUpdate(pairs, schedule, mentorCapacity)
    schedule = schCap[0]
    mentorCapacity = schCap[1]
        
    for elem in remainingSlots:
        hour = elem[1]
        day = elem[2][:3]
        
        counter = 0
        for mentee in mentees['Name']:
            for days in mentees.columns:
                if(day == days[:3]):
                    dayAvail = days
            menteeAvail = mentees.at[counter, dayAvail]
            name = mentee
            if(str(hour) in menteeAvail and mentorCapacity[name] < 1 and mentorCapacity[elem[0]]  < 1 and name != elem[0]):
                mentorCapacity[name] = mentorCapacity.get(name) + 1
                mentorCapacity[elem[0]] = mentorCapacity.get(elem[0]) + 1
                schedule.at[hour, elem[2]] = elem[0] + ", " + mentee
            counter += 1
    return(schedule, mentorCapacity)

def everything(TheMagicNumber):
    #sets up all the data sets we will be working with
    mentees = pd.read_csv('mentee.csv')
    schedule = pd.read_csv('schedule.csv')
    mentors = pd.read_csv('mentor.csv')
    mentors = mentors['Name'].tolist()
    extras = pd.DataFrame()
    hours = schedule['Time'].tolist()
    
    #cleans mentee dataframe
    days = mentees.columns.tolist()
    days.pop(0)
    days.pop(0)
    mentees = hourCleanUp(mentees, days)
    mentees = seminarClean(mentees, days)
    
    #Prepares schedule and sets up daysSched which represents the rooms we have avail for each day
    daysSched = schedule.columns.tolist()
    daysSched.pop(0)

    schedule = scheduleSetUp(schedule)
    schedule.set_index('Time', inplace=True)
    
    #sets up and fills mentorCapacity
    mentorCapacity = mentorCapacitySetUp(mentors, daysSched, hours, schedule)
    
    #Sorts the mentees dataframe in ascending order
    mentees = sortFrame(mentees, days)
    
    if mentees["Name"][0] in mentors:   
        tmp = mainMentorAlgo(mentors, schedule, daysSched, mentees, mentorCapacity, TheMagicNumber)
        schedule = tmp[0]
        mentorCapacity = tmp[1]
    else:
        tmp = mainAlgo(mentees, days, daysSched, schedule, mentorCapacity,TheMagicNumber)
        schedule = tmp[0]
        extras = tmp[1]
        mentorCapacity = tmp[2]
        
    schedule.reset_index(inplace=True)
    schedule.to_csv('FinalSchedule.csv', index=False)
    extras.to_csv('extras.csv', index=False)
    return (schedule, extras, mentorCapacity)
