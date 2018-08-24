# Written by Jared Selby for Texas State University Project EverGreen, 2017

import os.path

def DefCon(variance):
                            # check if the file exists
    if os.path.isfile("defcon_status.txt"):
                            # if it does, open it for writing
        f = open("defcon_status.txt", "r+")
    else:
                            # if it does not, create the file and write 2 at the beginning
        f = open("defcon_status.txt", "w+")
        f.seek(0)
        f.write("2")        # write a starting value of 2 seconds

    f.seek(0)               # find the first line of the file
    hold = f.readline()     # read and assign to hold
    hold = hold.strip()     # strip any white space that might be there
    if hold == "":
        hold = 2
    else:
        hold = int(hold)        # convert to int (P2.7 defaults write to str, can't maths a str)
    vari = variance         # assign the passed variance value to vari

    if vari == 1:           # if variance is low increase hold time
        hold = hold * 2
    elif vari == 2:         # if variance is high decrease hold time
        hold = hold / 2
    elif vari == 3:         # reset condition for the Pi
        hold = 2
                            # max sample frequency is once every 2 minutes
    if hold > 120:          # if hold exceeds 2 minutes, drop it to 2 minutes
        hold = 120
    elif hold < 2:          # if hold drops below 2 seconds, reset to 2 seconds
        hold = 2        

                            # delete the file and re-create so it is empty
                            # this is a stupid workaround for python 2.7 overwrite issues
    f = open("defcon_status.txt", "w+")
    f.seek(0)               # go to first line
    f.write(str(hold))      # write string version of hold there
    f.close()               # close the file so it saves
    
    return hold             # return hold to parent for wait time
