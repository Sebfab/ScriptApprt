# -*- coding: utf-8 -*-
from threading import Thread
import json
import parikstra as nav
import datetime
import csv
import unicodedata
import numpy as np
import os
import sys
import string
import random

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def getDuration(lItineraries, method=0):
#method=0 --> fair
#method=1 --> first
#method=2 --> min
    if method == 0:
        if len(lItineraries) == 1:
            td = lItineraries[0].duration
            return td.seconds//60
        elif len(lItineraries) > 1:
            for i in range(len(lItineraries)):
                if lItineraries[i].type == u'Trajet arriv\xe9e au plus t\xf4t':
                    td = lItineraries[i].duration
                    return td.seconds//60

            tdmin=99999999.
            for i in range(len(lItineraries)):
                tdmin = min(tdmin, lItineraries[i].duration.seconds//60)

            return tdmin
        return None
    elif method == 1:
        if len(lItineraries) > 0:
            td = lItineraries[0].duration
            return td.seconds//60
        return None
    elif method == 2:
        if len(lItineraries) > 0:
            tdmin=99999999.
            for i in range(len(lItineraries)):
                tdmin = min(tdmin, lItineraries[i].duration.seconds//60)
            return tdmin
        return None

def calcDurationWithAlea(theGoDuration, theReDuration, coeff=1.0):
    return coeff*(theGoDuration+theReDuration)/2.0

def calcCodeAil(refDurationWithAlea, newDurationWithAlea):
    diffDuration = abs(refDurationWithAlea-newDurationWithAlea)
    if diffDuration <= 0.0:
        return 0
    elif diffDuration < 10.0:
        return 1
    elif diffDuration < 15.0:
        return 2
    elif diffDuration < 20.0:
        return 3
    elif diffDuration < 25.0:
        return 4
    elif diffDuration < 30.0:
        return 5
    elif diffDuration < 35.0:
        return 6
    elif diffDuration < 40.0:
        return 7
    elif diffDuration < 45.0:
        return 8
    else:
        return 9

# def getColorFromCodeAil(theCodeAil):
#     if theCodeAil == 4:
#         return 'green'
#     elif theCodeAil == 3:
#         return 'yellow'
#     elif theCodeAil == 2:
#         return '#ffc000'
#     elif theCodeAil == 1:
#         return 'red'
#     elif theCodeAil == 0:
#         return 'black'

class myAdress:
    def __init__(self, data):
        if 'column_4' in data['fields']:
            self.setFields(data['fields'])
            self.setCoords(data['geometry'])
        # else:
        #     self.is75=False

    def setFields(self, data):
        # self.is75=True
        self.number=data['column_2']
        self.adress=data['column_2'] + u' ' + data['column_3']
        self.cpostale=data['column_4']
        self.city=data['column_5']
        self.id=data['column_1']

    def setCoords(self, data):
        self.coords=data['coordinates']

    def setDurationWithAlea(self, theDuration):
        self.duration=theDuration

    def setCodeAil(self, code):
        self.code=code

    # def inParis(self):
    #     return self.is75

    def getNum(self):
        return self.number

    def getAdress(self):
        return self.adress

    def getCity(self):
        return self.city

    def getAdressWithoutNum(self):
        return self.adress[len(self.number):].strip()

    def getCodePostale(self):
        return self.cpostale

    def getCoords(self):
        return self.coords

    def getId(self):
        return self.id

class exploreCity(Thread):
    def __init__(self, num_thread, adresses, end_info, id_start, id_end):
        Thread.__init__(self)
        self.num_thread = num_thread
        self.work_name = end_info[0]
        self.adresses = adresses
        self.end = end_info[1]
        self.id_start = id_start
        self.id_end = id_end

    def run(self):
    #method=0 --> fair
    #method=1 --> first
    #method=2 --> min

        random_string=id_generator()

        csvfile0 = open('Results/carte_ail_fair_%s_%s.csv92' %(self.work_name, random_string), 'a')
        csvfile1 = open('Results/carte_ail_first_%s_%s.csv92' %(self.work_name, random_string), 'a')
        csvfile2 = open('Results/carte_ail_min_%s_%s.csv92' %(self.work_name, random_string), 'a')

        fieldnames = ['Id', 'Code_postale', 'Ville', 'Adresse', 'Num', 'Temps_'+self.work_name, 'Code', 'Longitude', 'Latitude']

        lwriter=[]
        lwriter.append(csv.DictWriter(csvfile0, fieldnames=fieldnames))
        lwriter.append(csv.DictWriter(csvfile1, fieldnames=fieldnames))
        lwriter.append(csv.DictWriter(csvfile2, fieldnames=fieldnames))

        print u"Start thread %d " %(self.num_thread)
        for id_adress in range(self.id_start, self.id_end):
            if not(id_adress%10):
                print 'Thread ', self.num_thread,' : ', id_adress,'/',self.id_end
            adress = self.adresses[id_adress]
            start  = adress.getAdress()+u', '+adress.getCity()
            newDurationWithAlea = 0.0
            if not('/' in start):
                newGoItinerary = nav.Itinerary(start, end=self.end, date=date_arrival  , sens=-1)
                newReItinerary = nav.Itinerary(self.end, end=start, date=date_departure, sens= 1)
                for i in range(len(lwriter)):
                    newGoDuration = getDuration(newGoItinerary, method=i)
                    newReDuration = getDuration(newReItinerary, method=i)
                    if newGoDuration != None and newReDuration != None:
                        newDurationWithAlea = calcDurationWithAlea(newGoDuration, newReDuration)
                        adress.setDurationWithAlea(newDurationWithAlea)
                        theCodeAil = calcCodeAil(0.0, newDurationWithAlea)
                        adress.setCodeAil(theCodeAil)
                        coords=adress.getCoords()
                        # print id_adress,'/',len(self.adresses), ' : ', start, newDurationWithAlea, theCodeAil
                        # print 'Thread ', self.num_thread,' : ', id_adress,'/',self.id_end
                        lwriter[i].writerow({'Id':adress.getId(),
                                             'Code_postale':adress.getCodePostale(),
                                             'Ville':adress.getCity(),
                                             'Adresse':unicodedata.normalize('NFKD',adress.getAdressWithoutNum()).encode('ascii','ignore'),
                                             'Num':adress.getNum(),
                                             'Temps_'+self.work_name:newDurationWithAlea,
                                             'Code':theCodeAil,
                                             'Longitude':coords[0],
                                             'Latitude':coords[1]})
                    else:
                        coords=adress.getCoords()
                        # print id_adress,'/',len(self.adresses), ' : ', start, 'Not Done'
                        lwriter[i].writerow({'Id':adress.getId(),
                                             'Code_postale':adress.getCodePostale(),
                                             'Ville':adress.getCity(),
                                             'Adresse':unicodedata.normalize('NFKD',adress.getAdressWithoutNum()).encode('ascii','ignore'),
                                             'Num':adress.getNum(),
                                             'Temps_'+self.work_name:newDurationWithAlea,
                                             'Code':"-1",
                                             'Longitude':coords[0],
                                             'Latitude':coords[1]})
            else:
                coords=adress.getCoords()
                # print id_adress,'/',len(self.adresses), ' : ', start, 'Not Done'
                for i in range(len(lwriter)):
                    lwriter[i].writerow({'Id':adress.getId(),
                                         'Code_postale':adress.getCodePostale(),
                                         'Ville':adress.getCity(),
                                         'Adresse':unicodedata.normalize('NFKD',adress.getAdressWithoutNum()).encode('ascii','ignore'),
                                         'Num':adress.getNum(),
                                         'Temps_'+self.work_name:newDurationWithAlea,
                                         'Code':"-2",
                                         'Longitude':coords[0],
                                         'Latitude':coords[1]})

        csvfile0.close()
        csvfile1.close()
        csvfile2.close()

def getalladresses(l_cpostal=[], l_id=[]):
    print u"Read json file"
    file = open('base-dadresses-nationale-ouverte-bano-hauts-de-seine.json')
    all_adresses = json.load(file)
    file.close()

    adresses=[]
    nb_all_adresses=len(all_adresses)
    adresses_tested=[]

    if len(l_id) == 0:
        if l_cpostal != None:
            for id_adress in range(nb_all_adresses):
                adress=myAdress(all_adresses[id_adress])
                if adress.getCodePostale() in l_cpostal:
                    adresses.append(adress)
        else:
            for id_adress in range(nb_all_adresses):
                adress=myAdress(all_adresses[id_adress])
                adresses.append(adress)
    elif len(l_id) > 0:
        if len(l_cpostal) > 0:
            for id_adress in range(nb_all_adresses):
                adress=myAdress(all_adresses[id_adress])
                if adress.getCodePostale() in l_cpostal:
                    if not (adress.getId() in l_id):
                        adresses.append(adress)
                    else:
                        adresses_tested.append(adress)
        else:
            for id_adress in range(nb_all_adresses):
                adress=myAdress(all_adresses[id_adress])
                if not (adress.getId() in l_id):
                    adresses.append(adress)
                else:
                    adresses_tested.append(adress)

    print u"Nombre d'adresses d\xe9ja test\xe9e :", len(adresses_tested)
    return adresses


def listfileindirectories(path, str, crit='min'):
    l_files=[]

    for root, dirs, files in os.walk(path):
        for i in files:
            fileName, fileExtension=os.path.splitext(i)
            if fileExtension == '.csv' and crit in fileName:
                if str in fileName:
                    l_files.append(os.path.join(root, i))
    return l_files

def getadressesfromcvsfile(l_file):
    l_adresses=[]
    for file in l_file:
        with open(file, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                l_adresses.append(row[4]+" "+row[3]+", "+row[2])
    return l_adresses

def getadressesidfromcvsfile(l_file):
    l_adresses_id=[]
    for file in l_file:
        with open(file, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[4] != None and row[3] != None and float(row[5]) > 0.0 and len(row) == 9:
                    l_adresses_id.append(int(row[0]))
    return l_adresses_id

if __name__ == '__main__':

    path=os.getcwd()
    test = False
    eval = True
    annee = 2017
    mois  = 02
    jour  = 03

    #Calcul du temps de trajet de référence
    EDF1 = "97 avenue Pierre Brossolette, Montrouge"
    EDF2 = "14 rue Paul Bert, Montrouge"
    AREVA = "1 place Jean Millet, Courbevoie"
    SFL = "10 Rue Raymond David, Malakoff"
    str = "AREVA"

    # d_work_adresses={"AREVA":AREVA,"EDF1":EDF1,"EDF2":EDF2}
    if str=="AREVA":
        d_work_adresses={"AREVA":AREVA}
    elif str=="EDF1":
        d_work_adresses={"EDF1":EDF1}
    elif str=="EDF2":
        d_work_adresses={"EDF2":EDF2}
    elif str=="SFL":
        d_work_adresses={"SFL":SFL}

    date_arrival  =datetime.datetime(annee,mois,jour, 9,00)
    date_departure=datetime.datetime(annee,mois,jour,17,30)

    l_cpostal=[92800]
    if test:
        l_cpostal=[92800]

    l_files=listfileindirectories(path, str)

    adresses_tested_id=[]

    if len(l_files) > 0:
        adresses_tested_id = getadressesidfromcvsfile(l_files)

    adresses=getalladresses(l_cpostal=l_cpostal, l_id=adresses_tested_id)
    nb_adresses=len(adresses)

    print "Nombre d'adresses a traiter :", nb_adresses

    if eval:

        plage_adresses=range(0,nb_adresses,200)
        plage_adresses.append(nb_adresses)

        if test:
            plage_adresses=range(10)

        for work_name in d_work_adresses.keys():
            l_threads=[]

            for i in range(len(plage_adresses)-1):
                l_threads.append(exploreCity(i, adresses, [work_name, d_work_adresses[work_name]], plage_adresses[i], plage_adresses[i+1]))

            for i in range(len(plage_adresses)-1):
                l_threads[i].start()

            for i in range(len(plage_adresses)-1):
                l_threads[i].join()
