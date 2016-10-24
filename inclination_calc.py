#KSP Inclination Maneuver Calculator
#Edited 10/13/2016
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

import math 
from decimal import * #TODO: replace all instances of floats with the Decimal type once basic functionality is established
getcontext().prec = 10

#Semi Major Axis calculation:
def SMA_From_Orb_Vel (currentHeight, OrbVel, LocalGrav):
	return -1 / (OrbVel ** 2 / LocalGrav - 2 / currentHeight)

#Eccentricity calculation
def Ecc_From_Ap_Pe(Apoapsis, Periapsis):
    return (Apoapsis - Periapsis) / (Apoapsis + Periapsis)

#set up a class for orbits
class ORBIT = (object):
    #TODO: make all orbital params not inputted by user properties or methods of Orbit class
    def __init__(self, AP, PE, INC, PBD, APE, LAN, TAN):
        #all __init__ definitions values used to define orbit taken from user inputs
        self.AP = AP    #Periapsis
        self.PE = PE    #Apoapsis
        self.INC = INC  #Inclination
        self.PBB = PBD  #Planetary body
        self.APE = APE  #Argument of periapsis
        self.LAN = LAN  #Longitude of ascending node
        self.TAN = TAN  #True anomaly
        
        self.SMA = ((AP + PE) / 2)
        self.ECC = Ecc_From_Ap_Pe(AP, PE)
        
        self.period = (2 * math.pi) * math.sqrt((self.SMA ** 3) / gravConstant) #orbital period
        self.meanMotion = 360 / self.period                                     #mean motion
    
        #orbital velocity method
    def Orb_Vel(currentHeight, SemiMajorAxis, LocalGrav):
	    return math.sqrt(LocalGrav * (2 / currentHeight - 1 / semiMajorAxis))
    
    #calculate DV required for changing the orbit's plane by a given amount
    def Plane_Change_Delta_V(AngleChange):	
	    numerator = 2 * math.sin(AngleChange / 2) * math.sqrt(1 - self.ECC ** 2) * math.degrees(math.cos(self.APE + self.TAN)) * self.meanMotion * self.SMA 
	    return numerator / (1 + self.ECC * math.degrees(math.cos(self.TAN))) 
        #^that equation was horrendous. if you have a question, ask wikipedia. its under orbital inclination change or something.
    
    def Optimize_Plane_Change(AngleChange, InitAp):
        maneuverList = []
        for values in range(InitAp, maxSafeAp + 1, 100):
            maneuverList.append(Plane_Change_Delta_V(incDifference))
        
        return maneuverList

#creates new instance of Orbit class via user inputs    
def New_Orbit_From_Input():
    
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

    #get orbital parameters from inputs
    apHeight = float(input("Apoapsis height(Km)? ") * 1000)				
    peHeight = float(input("Periapsis height(Km)? ") * 1000)

    #TODO: either find a way to do simpler inputs (unlikely) or read params directly from a .sfs
    initInc = int(input("Current inclination? "))
    global finalInc = int(input("Desired inclination? "))
    peArg = float(input("Argument of Periapsis? "))
    anLong = float(input("longitude of ascending node? "))
    maxApPref = str(input("Avoid possible intercepts with moons? (y/n) (defaults to n if invalid or null) ")).lower

    #change maxSafeAp lookup if the user specifies yes for maxApPref
    if maxApPref == "y":
        bodyValues['kerbin'][2] = int(9570440)
        bodyValues['eve'][2] = int(14048876)
        bodyValues['duna'][2] = int(12999278)
        bodyValues['jool'][2] = int(2.4559852 * 10 ** 9)
    
    #assign gravConstant, localRadius and maxSafeAp from dictionary lookup based on input 
    localSystem = str("0")
    while localSystem == "0":	
        localSystem = str(input("Local planetary body? ")).lower
    
        #first check if the user's input was valid
        if localSystem not in bodyValues:
            print("Error: Not a valid body in KSP")
            localSystem = str("0")	
        #actually assign the values (only runs if intput body is valid)
        else:
            gravConstant = bodyValues[localSystem][0]
            localRadius = bodyValues[localSystem][1]
            global maxSafeAp = bodyValues[localSystem][2]
    
    #create variables needed for defining orbit
    initApHeightAdj = apHeight + localRadius
    initPeHeightAdj = peHeight + localRadius
    
    #assign orbital parameters that are simpler to caclulate for circular orbuts
    if apHeight == peHeight:
        print("Input accepted. Calculating...")
        nodeHeight = initApHeightAdj
        initTNA = 360 - peArg
    else:
        nodeHeight = float(input("Altitude at ascending node(Km)? ")) + localRadius
        print("Input accepted. Calculating...")

        #decide wether to use An or Dn for manuvers by which one > semi minor axis 
        initTAN = math.degrees(math.acos((initSMA - (initSMA * initECC ** 2) - nodeHeight) / (nodeHeight * initECC)))
        if nodeHeight < (initSMA * math.sqrt(1 - initECC ** 2):
            initTAN = math.fabs(initTNA - 180)
    
    newOrbit = ORBIT(
        initApHeightAdj,    #Apoapsis
        initPeHeightAdj,    #Periapsis
        initInc,            #Inclination
        localSystem,        #Local planetary body
        peArg,              #Argument of periapsis
        anLong,             #Longitude of ascending node 
        0                   #True anomaly; can be set to 0 since it's based off of an arbitrary ref angle
    )

    return newOrbit

initOrbit = New_Orbit_From_Input():

#TODO: calculate best bi-eliptic plane change DV once sketchy math is figured out:
maneuverList = initOrbit.Optimize_Plane_Change(abs(finalInc - initOrbit.INC), initOrbit.AP)

print ("Maneuver DV is " + initialOrbit.Plane_Change_Delta_V(math.fabs(finalInc - initInc)) + " m/s.")
