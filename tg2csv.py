#Script to convert TextGrid data to .csv format, which can be opened in any spreadsheet program.
#C.A. 2021
#Last updated 7/20/21
#   Use:
#       Put the script in the folder where your TextGrids are, navigate to that folder, and run:
#         python tg2csv.py
#
#   Note: this script is designed only for songs in 4/4

import sys
import re
import os
import codecs

def main(filename): #Called from "__main__" at the very bottom.
    try: #Most of the .TextGrides files are encoded in ASCII, but a few of them are in Unicode. If they are in Unicode, we have to convert them first.
        f = codecs.open(filename, 'r', 'utf-16')
        lines = [line.rstrip() for line in f]
    except UnicodeError: #If the file is in ASCII and we try to read it as Unicode, it won't work, so we catch this error.
        f = open(filename, 'r')   
        lines = [line.rstrip() for line in f]
    f.close()

    #Define a new data type, "interval"                                                             int     float   float   string
    class interval: #a variable of this type can be created like this: [variable name] = interval([number], [xmin], [xmax], [text])
        def __init__(self, number, xmin, xmax, text): #Any one of a variable's parameters can be returned from that variable like this: [variable name].[parameter name]
            self.number = number
            self.xmin = xmin
            self.xmax = xmax
            self.length = xmax-xmin
            self.text = text
        
    ### Routine for turning TextGrid file information into lists of interval objects ###
    tiers = [] #List of lists, one for each tier.
    curTier = [] #List of intervals that the loop below will be adding to. When a tier is finished being added, this list will be added to the "tiers" list.
    curNumber = 0 #These "cur" variables are for keeping track of the parameters of the current interval in the tier the script is looping through.
    curXmin = 0.0
    curXmax = 0.0
    curText = ""
    i = 0 #This (and the checkIfLast string) will be used to check whether or not the loop has reached the end of the TextGrid file.
    checkIfLast = ""
    for line in lines:
        if re.search("item ", line): #In the TextGrid file, each tier starts with "item[x]:". So if we see that string, we know we hit a new tier.
            tiers.append(curTier) #Before resetting the "cur" paramaters, add the current tier to the "tiers" list. Because there are two instances of "item" in the header of every TextGrid, tiers[0] and tiers[1] will be empty. So tier 1 is actually tiers[2], tier 9 is tiers[10].
            curTier = [] #At the beginning of each tier, set the list to be empty.
            curNumber = 0 #Set the interval number back to 0.
        if re.search("intervals ", line): #Each interval is written "intervals [x]:", so we add 1 to curNumber every time to keep track of which interval we are on.
            curNumber += 1
        if re.search("xmin", line):
            curXmin = float("".join(re.findall(r'[0123456789.]', line))) #This just means "take only the numeral characters and . from the current line and set curXmin to that".
        if re.search("xmax", line):
            curXmax = float("".join(re.findall(r'[0123456789.]', line))) #Same as curXmin above
        if re.search("text =", line):
            curText = "".join(re.findall(r'"(.*?)"', line)) #curText is set to whatever in the current line is between quotes.
            curTier.append(interval(curNumber,curXmin,curXmax,curText)) #Add the current interval to "curTier" list.

        try: #The program tries to set checkIfLast to whatever the _next_ item in the TextGrid file is. If there is no next item, skip this and go to the "except IndexError:" section.
            checkIfLast = lines[i+1] #checkIfLast is just a dummy variable, its only purpose is for this check.
        except IndexError: #If we have reached the end of the TextGrid file:
            tiers.append(curTier) #Add the last tier to the "tiers" list

        i += 1
        


    ### Routine for outputting the TextGrid data to csv format ###
    createNew = open(filename+".csv", "a") #Create a [filename].csv file, just in case it doesn't exist already.
    createNew.close()
    with open(filename+".csv", 'r+') as f2: 
        f2.truncate()
        f2.write("Syllable,Metric Absolute,Micro Absolute,Metric Measure,Beat Strength,Accent,Zone")
        i = 0
        metricCounter = 0
        measureCounter = 0
        curZone = ""
        zoneCounter = 0
        for inter in tiers[7]: #Loop through each interval in Tier 6 (e.g. tiers[7]).
            microText = "," 
            beatStrength = "4," #Default value
            if(inter.text != ""): #Each interval should be a syllable. If there's no text in it, we can just skip it.
                f2.write('\n')
                
                #Syllable: The syllable text
                f2.write(inter.text+",")
                
                #Metric Absolute: How many beats into the song the syllable is
                for absolute in tiers[6]: #Tier 5 (e.g. tiers[6]) is the one with the unmodified metric data. We need to use that to get a count of which (absolute) beat we're on.
                    if inter.xmin == absolute.xmin: #We look through every interval in Tier 5 until we find one that has the same xmin as our current syllable.
                        metricCounter = absolute.number-1 #Set metricCounter to the interval number of the Tier 5 interval that corresponds to our current syllable. metricCounter is the number that will be printed to the "Metric Absolute" column in our spreadsheet.
                        for measure in tiers[4]: #While we're at it, we should also calculate which measure we're on. This will be used for the "Metric Measure" column of the spreadsheet.
                            if absolute.xmin < measure.xmax: #Same as above, but this time comparing Tier 5 to Tier 3, to find which measure our current syllable is in.
                                measureCounter = measure.number-1 #Because of the xxx at the start of the TextGrid, the "first" measure actually shows up as measure 2, the second shows up as 3, etc. So we need to subtract one so it makes sense.
                                break #Once we find what we're looking for, we can stop the loop.
                        break
                f2.write(str(metricCounter)+",") 
                
                x = 0
                #Micro Absolute: The starting time for the syllable's microtiming interval
                while(x < len(tiers[8])): #Look through the whole microtiming tier to find the microtiming interval that matches the metric interval.
                    if(inter.xmin >= tiers[8][x].xmin and inter.xmin <= tiers[8][x].xmax and inter.text == tiers[8][x].text): #If metric interval's xmin falls BETWEEN any microtiming interval's xmin and xmax, AND the text for both intervals matches, use that microtiming interval.
                        microText = str(tiers[8][x].xmin)+","
                    elif(inter.xmax >= tiers[8][x].xmin and inter.xmax <= tiers[8][x].xmax and inter.text == tiers[8][x].text): #If none of the intervals match the above criteria, try it with the metric interval's xmax instead of its xmin.
                        microText = str(tiers[8][x].xmin)+","
                    elif(inter.xmin <= tiers[8][x].xmin and inter.xmax >= tiers[8][x].xmax and inter.text == tiers[8][x].text): #If that doesn't work, check microtiming intervals that start AFTER the metric interval.
                        microText = str(tiers[8][x].xmin)+","
                    elif(inter.xmin >= tiers[8][x-1].xmax and inter.text == tiers[8][x-1].text): #If all of the above fail, check the previous interval.
                        microText = str(tiers[8][x-1].xmin)+","
                    x += 1
                f2.write(microText)
                
                #Metric Measure: Formatted as X.Y, where X is which measure of the song the syllable is in, Y is which beat of that measure the syllable is on
                if(metricCounter%4 == 0): #We % (modulo) the current syllable's metric number by 4, to figure out which of the four beats it lands on. 1, 2, and 3 will show up correctly, but 4 shows up as 0, so we need to create a special exception for that.
                    f2.write(str(measureCounter)+"."+str(4)+",") #Change any 0s to 4s.
                else:
                    f2.write(str(measureCounter)+"."+str(metricCounter%4)+",")
                
                #Beat Strength: Out of tiers 1, 2, 3, and 4, which is the lowest number tier that the current metric interval lines up with?
                for beat in tiers[4]: #Check tier 3
                    if(beat.xmin == inter.xmin):
                        beatStrength = "3,"
                for beat in tiers[3]: #Check tier 2
                    if(beat.xmin == inter.xmin):
                        beatStrength = "2,"
                for beat in tiers[2]: #Check tier 1
                    if(beat.xmin == inter.xmin):
                        beatStrength = "1,"
                f2.write(beatStrength)
                
                #Accent: Does the syllable have a strong accent (X), a weak accent (x), or no accent (not marked)?
                f2.write(tiers[9][i].text+",") 
                
                #Zone: Which zone the syllable is in
                for zone in tiers[10]: #Loop through Tier 9 intervals
                    if inter.xmin < zone.xmax: #Check if the xmin of the current syllable is less than the xmax of a Zone in Tier 9
                        curZone = zone.text #If the xmin of the current syllable falls within a zone, make curZone that zone's text, then end the loop.
                        break
                f2.write(curZone)
                
            i += 1
    f2.close()


if __name__ == "__main__":
    for root, dirs, files in os.walk(".", topdown=True): #Run the script on each file in the directory
        for file in files:
            if(file.endswith(".TextGrid")): #Only run the script on files that end in .TextGrid
                main(file)
