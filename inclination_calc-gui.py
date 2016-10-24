#KSP Inclination Maneuver Calculator- graphical output version
#Edited 10/11/2016
#The MIT License (MIT)

#Copyright (c) 2015-2016 Ethan Wilton 

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

#==================================================================================================================================

#A WORD ABOUT THIS BRANCH:

#One night, my sleep-deprived, ADHD ass decided it would be a really cool and fun idea to make a GUI for this program. Later I realized that was actually a really shitty idea, considering the program wouldn't execute to completion due to errors at that point in development. 

#As such, development of this branch is hereby suspended until the base program does what it's supposed to without crashing. This will probably take quite a while (read: I probably wont get back to developing this branch for at least a year or so). 

#If you really want a GUI version of this that badly, I suppose you could fork the dev or master branch and develop it yourself, but I wont be providing any help.

#==================================================================================================================================

from tkinter import *
import math
from decimal import *
getcontext().prec = 10

#orbital velocity calculation:
def Orb_Vel(NodeHeight, SemiMajorAxis, LocalGrav):
	return math.sqrt(LocalGrav * (2 / nodeHeight - 1 / semiMajorAxis))

#Semi Major Axis calculation:
def Semi_Major_Axis (NodeHeight, OrbVel, LocalGrav):
	return -1 / (OrbVel ** 2 / LocalGrav - 2 / NodeHeight)

#caculate DV of a plane change maneuver:	
def Inclination_Change_Delta_V (AngleChange, Eccentricity, PeriapsisArgument, TrueAnomaly, MeanMotion, SMajorAxis):	
	numerator = 2 * math.sin(AngleChange / 2) * math.sqrt(1 - Eccentricity ** 2) * math.cos(PeriapsisArgument + TrueAnomaly) * MeanMotion * SMajorAxis 
	return numerator / (1 + Eccentricity * math.cos(TrueAnomaly)) 
    #that equation was horrendous. if you have a question, ask wikipedia. its under orbital inclination change or something.
	
root = Tk()

#get orbital parameters from inputs
#TODO: simplify so the user doesnt need to look at the save files to input vars (if possible)
apHeight = Decimal(input("Apoapsis height(Km)? "))				
peHeight = Decimal(input("Periapsis height(Km)? "))

#only ask for nodeHeight if it is needed
if apHeight == peHeight:
	nodeHeight = apHeight
else:
	nodeHeight = Decimal(input("Altitude at ascending node(Km)? "))

currentInc = int(input("Current inclination? "))
finalInc = int(input("Desired inclination? "))
maxApPref = str(input("Prevent intercepts with moons? (y/n) (defaults to n if invalid or null) "))
maxApPref = maxApPref.lower

#dictionary for values associated with the planetary bodies:
bodyValues = {
    #list items: index 0 is gravConstant, 1 is localRadius, 2 is maxSafeAp
    'kerbin': [int(3.5316000 * 10 ** 12), int(600000), int(84159286)],
    'mun': [int(6.5138398 * 10 ** 10), int(200000), int(2429559)],
    'minmus': [int(1.7658000 * 10 ** 9), int(60000), int(2247428)],
    'moho': [int(1.6860938 * 10 ** 11), int(250000), int(9646663)], 
    'eve': [int(8.1717302 * 10 ** 12), int(700000), int(85109365)], 
    'gilly': [int(8289449.8), int(13000), int(126123)],
    'duna': [int(3.0136321 * 10 ** 11), int(320000), int(47921949)],
    'ike': [int(1.8568369 * 10 ** 10), int(130000), int(1049598)],
    'dres': [int(2.1484489 * 10 ** 10), int(138000), int(32832840)],
    'jool': [int(2.8252800 * 10 ** 14), int(6000000), int(2.4559852 * 10 ** 9)],
    'laythe': [int(1.9620000 * 10 ** 12), int(500000), int(3723645)],
    'vall': [int(2.0748150 * 10 ** 11), int(300000), int(2406401)],
    'tylo': [int(2.8252800 * 10 ** 12), int(600000), int(10856518)],
    'bop': [int(2.4868349 * 10 ** 9), int(65000), int(1221060)],
    'pol': [int(7.2170208 * 10 ** 8), int(44000), int(1042138)],
    'eeloo': [int(7.4410815 * 10 ** 10), int(210000), int(1.1908294 * 10 ** 8 )], 
    'kerbol': [int(1.1723328 * 10 ** 18), int(261600000), int(10 ** 12)],
    'sun': [int(1.1723328 * 10 ** 18), int(261600000), int(10 ** 12)]
}

#^ I dedicate this dictionary in the name of the elif block of agony and despair, which it replaced

if maxApPref == "y":
    bodyValues['kerbin'][2] = int(9570440)
    bodyValues['eve'][2] = int(14048876)
    bodyValues['duna'][2] = int(12999278)
    bodyValues['jool'][2] = int(2.4559852 * 10 ** 9)

#assign gravConstant, localRadius and maxSafeAp from dictionary lookup based on input 
localSystem = str("0")
while localSystem == "0":	
	localSystem = str(input("Local planetary body? "))
	localSystem = localSystem.lower()

	#first check if the user's input was valid
	if localSystem not in bodyValues:
		print("Error: Not a valid body in KSP")
		localSystem = str("0")
	
	#actually assign the values (only runs if intput body is valid)
	else:
		gravConstant = bodyValues[localSystem][0]
		localRadius = bodyValues[localSystem][1]
		maxSafeAp = bodyValues[localSystem][2]

print("Input accepted. Calculating...")	

#initialize some important variables:

#change ap/pe height to actual radius from center for accurate mathing. also converting from km to m is probably important
apHeightTotal = (apHeight * 1000) + localRadius		
peHeightTotal = (peHeight * 1000) + localRadius

#various prbital params
eccentricity = Decimal((apHeightTotal - peHeightTotal) / (apHeightTotal + peHeightTotal))
incDifference  = math.fabs(finalInc - currentInc)
semiMajorAxis = ((2 * localRadius) + peHeightTotal + apHeightTotal) / 2			
nodeHeightTotal = localRadius + nodeHeight
peAngle = 0
anAngle = math.acos((nodeHeightTotal + semiMajorAxis - (semiMajorAxis * eccentricity ** 2)) / peHeight * eccentricity)	
#clarification: anAngle is angle of ascending node
dnAngle = math.fabs(anAngle - math.pi)
argumentOfPeriapsis = math.fabs(peAngle - anAngle)
orbitalPeriod = 2 * math.pi * math.sqrt(semiMajorAxis ** 3 / gravConstant)
meanMotion = (2 * math.pi) / orbitalPeriod

#prevents anAngle from throwing /0 errors
if eccentricity != 0: 
    anAngle = math.acos((nodeHeightTotal + semiMajorAxis - (semiMajorAxis * eccentricity ** 2)) / peHeight * eccentricity)
else: 
    anAngle = 0

#convert to radians because math
currentInc = math.radians(currentInc)						
finalInc = math.radians(finalInc)
incDifference = math.radians(incDifference)

#calculate more orbital params using functions defined earlier
orbVelInitial = Orb_Vel(nodeHeightTotal, semiMajorAxis, gravConstant)		
directChangeDeltaV = Inclination_Change_Delta_V(incDifference, eccentricity, argumentOfPeriapsis, anAngle, meanMotion, semiMajorAxis)



#Finish this part once sketchy math is figured out:
#while (apHeightTotal < maxSafeAp):				#aforementioned while loop from hell. Finds the cheapest possible bi-eliptic plane change maneuver.
#	orbVelBiEliptic = orbVelBiEliptic + 50
#	biElipticChangeSMA = Semi_Major_Axis(nodeHeightTotal, orbVelBiEliptic, gravConstant)
#	apHeightTotal = 
#	
#	
#if directChangeDeltaV < biElipticDeltaV:			#outputs appropriate maneuver + delta V readout
#	print("Use a bi-elliptic plane change maneuver.")
#	print("The maneuver will take ", biElipticDeltaV, "m/s")
#
#else:
#	print("Use a basic plane change maneuver.")
#	print("The maneuver will take ", directChangeDeltaV, "m/s")

print ("Maneuver DV is ", directChangeDeltaV, " m/s.")
