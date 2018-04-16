# -*- coding: utf-8 -*-
import json
import csv
import unicodedata
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import string
import random


def listfileindirectories(path, str, crit='min'):
    l_files=[]

    for root, dirs, files in os.walk(path):
        for i in files:
            fileName, fileExtension=os.path.splitext(i)
            if fileExtension == '.csv92' and crit in fileName:
                if str in fileName:
                    l_files.append(os.path.join(root, i))
    return l_files

if __name__ == '__main__':

    path=os.getcwd()
    l_files_AREVA=listfileindirectories(path, "AREVA")
    l_files_EDF1 =listfileindirectories(path, "EDF1")
    l_files_EDF2 =listfileindirectories(path, "EDF2")
    l_files_SFL =listfileindirectories(path, "SFL")

    #method=0 --> fair
    #method=1 --> first
    #method=2 --> min

    #   0          1            2         3        4                5               6         7           8
    # ['Id', 'Code_postale', 'Ville', 'Adresse', 'Num', 'Temps_'+self.work_name, 'Code', 'Longitude', 'Latitude']
    #    0         1            2         3        4           5            6             7             8            9            10           11          12           13          14           15           16
    # ['Id', 'Code_postale', 'Ville', 'Adresse', 'Num', 'Temps_AREVA', 'Temps_EDF1', 'Temps_EDF2', 'Temps_SFL', 'Temps_max', 'Code_AREVA', 'Code_EDF1', 'Code_EDF2', 'Code_SFL', 'Code_max', 'Longitude', 'Latitude']

    # method=2
    fig0, ax0 = plt.subplots()

    data=[]
    l_id=[]

    for file in l_files_AREVA:
        with open(file, 'rb') as f_AREVA:
            reader_AREVA = csv.reader(f_AREVA)
            for row in reader_AREVA:
                if len(row) == 9:
                    if float(row[5]) > 0.0:
                        data.append([row[0],row[1],row[2],row[3],row[4],row[5],"0.0","0.0","0.0",row[5],row[6],"0","0","0",row[6],row[7],row[8]])
                        l_id.append(row[0])

    for file in l_files_EDF1:
        with open(file, 'rb') as f_EDF1:
            reader_EDF1  = csv.reader(f_EDF1)
            for row in reader_EDF1:
                if len(row) == 9:
                    if float(row[5]) > 0.0:
                        if row[0] in l_id:
                            id = l_id.index(row[0])
                            data[id][6] = row[5]
                            data[id][9] = max(data[id][9], row[5])
                            data[id][11] = row[6]
                            data[id][14] = max(data[id][14], row[6])
                    else:
                        data.append([row[0],row[1],row[2],row[3],row[4],"0.0",row[5],"0.0","0.0",row[5],"0",row[6],"0","0",row[6],row[7],row[8]])
                        l_id.append(row[0])

    for file in l_files_EDF2:
        with open(file, 'rb') as f_EDF2:
            reader_EDF2  = csv.reader(f_EDF2)
            for row in reader_EDF2:
                if len(row) == 9:
                    if float(row[5]) > 0.0:
                        if row[0] in l_id:
                            id = l_id.index(row[0])
                            data[id][7] = row[5]
                            data[id][9] = max(data[id][9], row[5])
                            data[id][12] = row[6]
                            data[id][14] = max(data[id][14], row[6])
                    else:
                        data.append([row[0],row[1],row[2],row[3],row[4],"0.0","0.0",row[5],"0.0",row[5],"0","0",row[6],"0",row[6],row[7],row[8]])
                        l_id.append(row[0])

    for file in l_files_SFL:
        with open(file, 'rb') as f_SFL:
            reader_SFL  = csv.reader(f_SFL)
            for row in reader_SFL:
                if len(row) == 9:
                    if float(row[5]) > 0.0:
                        if row[0] in l_id:
                            id = l_id.index(row[0])
                            data[id][8] = row[5]
                            data[id][9] = max(data[id][9], row[5])
                            data[id][13] = row[6]
                            data[id][14] = max(data[id][14], row[6])
                    else:
                        data.append([row[0],row[1],row[2],row[3],row[4],"0.0","0.0","0.0",row[5],row[5],"0","0","0",row[6],row[6],row[7],row[8]])
                        l_id.append(row[0])

    csvfile0 = open('Results/carte_ail_min.csv92', 'w')
    fieldnames = ['Id', 'Code_Postale', 'Ville', 'Adresse', 'Num', 'Temps_AREVA', 'Temps_EDF1', 'Temps_EDF2', 'Temps_SFL', 'Temps_max', 'Code_AREVA', 'Code_EDF1', 'Code_EDF2', 'Code_SFL', 'Code_max', 'Longitude', 'Latitude']
    writer = csv.DictWriter(csvfile0, fieldnames=fieldnames)
    for i in range(len(data)):
        writer.writerow({'Id':data[i][0],
                         'Code_Postale':data[i][1],
                         'Ville':data[i][2],
                         'Adresse':data[i][3],
                         'Num':data[i][4],
                         'Temps_AREVA':data[i][5],
                         'Temps_EDF1':data[i][6],
                         'Temps_EDF2':data[i][7],
                         'Temps_SFL':data[i][8],
                         'Temps_max':data[i][9],
                         'Code_AREVA':data[i][10],
                         'Code_EDF1':data[i][11],
                         'Code_EDF2':data[i][12],
                         'Code_SFL':data[i][13],
                         'Code_max':data[i][14],
                         'Longitude':data[i][15],
                         'Latitude':data[i][16]})
    csvfile0.close()
    #     plt.scatter(data[:-1,0], data[:-1,1], c=data[:-1,2])
    #
    # plt.colorbar()
    # plt.show()
