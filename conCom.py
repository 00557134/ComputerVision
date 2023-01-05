# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 02:45:27 2021

@author: User
"""

import os
import numpy as np
import math
from PIL import Image
from matplotlib import pyplot as plt
import random

def openImg(fileName):
    img = Image.open(fileName)
    
    return img

def RGBtoGray(img):
    img = np.array(img)
    H, W, C = img.shape
    grayImg = np.zeros((H, W))
    
    for i in range(H):
        for j in range(W):
            grayImg[i][j] = int((img[i][j][0] + img[i][j][1]* 2 + img[i][j][2]) >> 2)
            
    grayImg = Image.fromarray(grayImg)
    
    return grayImg

# For ISODATA
def computeMu(T, colorProb):
    pa = sum(colorProb[i] for i in range(T))
    pb = sum(colorProb[i] for i in range(T, 256))
    
    x1 = sum(i * colorProb[i] for i in range(T))
    x2 = sum(i * colorProb[i] for i in range(T, 256))
    
    mu1 = x1/pa
    mu2 = x2/pb
    
    return mu1, mu2

def ISOdata(grayImg):
    colorHist = np.zeros((256))
    grayImg = np.array(grayImg)
    H, W = grayImg.shape
    
    # Computing color histogram
    for i in range(H):
        for j in range(W):
            #print(type(grayImg[i][j]))
            colorHist[int(grayImg[i][j])] += 1 / (H*W)
        
    #print(colorHist)
    
        
    TH = 128
    # Computing mu1, mu2
    mu1, mu2 = computeMu(TH, colorHist)
    
    while(int((mu1+mu2)/2) != TH):
        #print(TH, " ", int((mu1+mu2)/2))
        TH = int((mu1+mu2)/2)
        mu1, mu2 = computeMu(TH, colorHist)
        
    return TH


def findParent(relationMap, x):
    val = relationMap[x]
    
    while val != 0:
        tmp = int(val)
        #print(tmp)
        val = relationMap[tmp]

    return tmp

def reDraw(componentIndex, relationMap):
    H, W = componentIndex.shape
    
    for i in range(1, H):
        for j in range(1, W):
            if relationMap[componentIndex[i][j]] != 0:
                par = findParent(relationMap, componentIndex[i][j])
                componentIndex[i][j] = par
                
    return componentIndex
    

# 判斷有無物件，並建立相鄰關係
def directionTF(grayImg, x, y, componentIndex, cnt, relationDict):
    grayImg = np.array(grayImg)
    #print(x, " ", y)
    
    if grayImg[x][y]:
        if componentIndex[x-1][y] == 0 and componentIndex[x][y-1] == 0:
            componentIndex[x][y] = cnt
            cnt += 1
            #print(cnt)
        elif componentIndex[x-1][y] != 0 and componentIndex[x][y-1] == 0:
            componentIndex[x][y] = componentIndex[x-1][y]
            #relationDict[cnt] = componentIndex[x-1][y]
        elif componentIndex[x-1][y] == 0 and componentIndex[x][y-1] != 0:
            componentIndex[x][y] = componentIndex[x][y-1]
            #relationDict[cnt] = componentIndex[x][y-1]
        elif componentIndex[x-1][y] != 0 and componentIndex[x][y-1] != 0 and componentIndex[x-1][y] != componentIndex[x][y-1]:
            componentIndex[x][y] = min(componentIndex[x][y-1], componentIndex[x-1][y])
            relationDict[max(componentIndex[x][y-1], componentIndex[x-1][y])] = min(componentIndex[x][y-1], componentIndex[x-1][y])
        elif componentIndex[x-1][y] != 0 and componentIndex[x][y-1] != 0 and componentIndex[x-1][y] == componentIndex[x][y-1]:
            componentIndex[x][y] = componentIndex[x][y-1]
        
        
    return cnt, relationDict
    
    

def connectedCom(grayImg):
    grayImg = np.array(grayImg)
    H, W = grayImg.shape
    print("Shape: ", H, W)
    componentIndex = np.zeros((H,W), dtype=np.int)
    cnt = 1
    relationDict = dict()
    
    if grayImg[0][0]:
        componentIndex[0][0] = cnt
        cnt += 1
    
    for i in range(1, W):
        if grayImg[0][i]: 
            if componentIndex[0][i-1] != 0:
                componentIndex[0][i] = componentIndex[0][i-1]
                #relationDict[cnt] = componentIndex[0][i-1]
            else:
                componentIndex[0][i] = cnt
                cnt += 1
                
    for i in range(1, H):
        if grayImg[i][0]: 
            if componentIndex[i-1][0] != 0:
                componentIndex[i][0] = componentIndex[i-1][0]
                #relationDict[cnt] = componentIndex[i-1][0]
            else:   
                componentIndex[i][0] = cnt
                cnt += 1
            
    #print(grayImg)
    print(cnt)
    for i in range(1, H):
        for j in range(1, W):
            cnt, relationDict = directionTF(grayImg, i, j, componentIndex, cnt, relationDict)
            #print(cnt)
    
    print(relationDict)
    relationMap = np.zeros(cnt)
    
    for key, value in relationDict.items():
        relationMap[key] = value
        
    #print(relationMap)
    componentIndex = reDraw(componentIndex, relationMap)
    #print(componentIndex)
    #print(componentIndex)
    print("Number of class: ", cnt)
    np.savetxt("Component.txt", componentIndex, fmt="%d")
    return componentIndex, cnt
                


# 依照物件編號隨機塗上顏色
def drawColor(connectImg, classNum):
    H, W = connectImg.shape
    rgbImg = np.zeros((H, W, 3))
    
    colorMap = np.zeros((classNum+1, 3))
    
    for i in range(1, classNum):
        for j in range(3):
            color = random.randint(0, 256)
            colorMap[i][j] = color
            
    print(colorMap)
    
    for i in range(H):
        for j in range(W):
            if connectImg[i][j] != 0:
                rgbImg[i][j][0] = colorMap[connectImg[i][j]][0]
                rgbImg[i][j][1] = colorMap[connectImg[i][j]][1]
                rgbImg[i][j][2] = colorMap[connectImg[i][j]][2]
                
                
    #print(rgbImg)            
    rgbImg = Image.fromarray(np.uint8(rgbImg))
    return rgbImg


def findNum(componentIndex):
    H, W = componentIndex.shape
    maxNum = np.max(componentIndex)
    calComNum = np.zeros(maxNum+1)
    
    for i in range(H):
        for j in range(W):
            if componentIndex[i][j] != 0:
                calComNum[componentIndex[i][j]] += 1
                
    return len(calComNum[calComNum>8000])
    

img = openImg('example3.png')

grayImg = RGBtoGray(img)
thresh = ISOdata(grayImg)
print(thresh)

grayImg = np.array(grayImg)
grayImg = grayImg <= thresh
grayImg = Image.fromarray(grayImg)


conComponent, classNum = connectedCom(grayImg)
comNums = findNum(conComponent)
rgbImg = drawColor(conComponent, classNum)

print("數字個數: ", comNums)

plt.figure()
f, axarr = plt.subplots(2,1) 
#plt.imshow(img)
axarr[0].imshow(grayImg)
axarr[1].imshow(rgbImg)
grayImg.save('grayImg.png')
rgbImg.save('rgbImg.png')

plt.show()






