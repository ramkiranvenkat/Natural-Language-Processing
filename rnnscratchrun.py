# -*- coding: utf-8 -*-
"""RNNScratchRun.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1qxuuNOWr5GtzPU_BDmr2uxrGGVMjitq3
"""

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import urllib
import sys
import os
import zipfile

from google.colab import drive
drive.mount('/content/drive')
zip_ref = zipfile.ZipFile("/content/drive/My Drive/ReadDataFolderWheel.zip", 'r')
zip_ref.extractall("/home")
zip_ref.close()

!ls /home/ReadDataFolderWheel

zip_ref = zipfile.ZipFile("/content/drive/My Drive/ReadDataFolderWheelGyroFailure.zip", 'r')
zip_ref.extractall("/home")
zip_ref.close()

!ls /home/ReadDataFolderWheelGyroFailure

import pandas as pd
path = "/home/ReadDataFolderWheel/"

def rearrangeData(dp):
  a = []
  for i in range(9):
    a.append([dp[i,2:],dp[i+1,2:]])
  return np.array(a)

data =  pd.read_csv(path + 'dp.0',sep=' ',header=None)
dataPoints = rearrangeData(data.to_numpy())
print(dataPoints.shape)
for filename in os.listdir(path):
  if (filename is not 'dp.0'):
    data =  pd.read_csv(path + filename,sep=' ',header=None)
  dataPoints = np.vstack((dataPoints,rearrangeData(data.to_numpy())))
print(dataPoints.shape)

path = "/home/ReadDataFolderWheel/"
data =  pd.read_csv(path + 'dp.0',sep=' ',header=None)
RNNDataPoint = np.array([data.to_numpy()[:-1,2:]])
print(RNNDataPoint.shape)
for filename in os.listdir(path):
  if (filename != 'dp.0'):
    data =  pd.read_csv(path + filename,sep=' ',header=None)
  RNNDataPoint = np.vstack((RNNDataPoint,np.array([data.to_numpy()[:,2:]])))
print(RNNDataPoint.shape)

path = "/home/ReadDataFolderWheelGyroFailure/"
data =  pd.read_csv(path + 'dp.0_W3',sep=' ',header=None) # first file in directory
RNNDataPointTest = np.array([data.to_numpy()[:,2:13]])
RNNMarking = []
for filename in os.listdir(path):
  if (filename is not 'dp.0_W3'):
    data =  pd.read_csv(path + filename,sep=' ',header=None)
    m = 1
    if filename[-1] == '0':
      m = 0
  RNNMarking.append(m)
  RNNDataPointTest = np.vstack((RNNDataPointTest,np.array([data.to_numpy()[:,2:13]])))
RNNMarking = np.array(RNNMarking)
print(RNNDataPointTest.shape,RNNMarking.shape)

path = "/home/ReadDataFolderWheelGyroFailure/"

def rearrangeData(dp,m,marking):
  a = []
  for i in range(9):
    a.append([dp[i,2:13],dp[i+1,2:13]])
    marking.append(m)
  return np.array(a)

marking = []
data =  pd.read_csv(path + 'dp.0_W3',sep=' ',header=None) # first file in directory
dataPointsTest = rearrangeData(data.to_numpy(),1,marking)
print(dataPointsTest.shape)
for filename in os.listdir(path):
  if (filename is not 'dp.0_W3'):
    data =  pd.read_csv(path + filename,sep=' ',header=None)
  m = 1
  if filename[-1] == '0':
    m = 0
  dataPointsTest = np.vstack((dataPointsTest,rearrangeData(data.to_numpy(),m,marking)))
marking = np.array(marking)  
print(dataPointsTest.shape)
print(marking.shape)

# Data Normalization
print(dataPoints[:,0,:].shape)
maxvals = np.amax(dataPoints,axis=0)
minvals = np.amin(dataPoints,axis=0)
maxvals = np.amax(maxvals,axis=0)
minvals = np.amin(minvals,axis=0)

print(maxvals)
maxvalsT = np.amax(dataPointsTest,axis=0)
minvalsT = np.amin(dataPointsTest,axis=0)
maxvalsT = np.amax(maxvalsT,axis=0)
minvalsT = np.amin(minvalsT,axis=0)
print(maxvalsT)
maxvals = np.maximum(maxvals,maxvalsT)
minvals = np.minimum(minvals,minvalsT)
print(maxvals)
difvals = maxvals-minvals

dataPointsNormalised = dataPoints.copy()
dataPointsTestNormalised = dataPointsTest.copy()

for i in range(dataPoints.shape[0]):
  dataPointsNormalised[i,0,:] = np.divide(dataPoints[i,0,:] - minvals, difvals)
  dataPointsNormalised[i,1,:] = np.divide(dataPoints[i,1,:] - minvals, difvals)
for i in range(dataPointsTest.shape[0]):
  dataPointsTestNormalised[i,0,:] = np.divide(dataPointsTest[i,0,:] - minvals, difvals)
  dataPointsTestNormalised[i,1,:] = np.divide(dataPointsTest[i,1,:] - minvals, difvals)
"""
maxvals = np.amax(dataPointsNormalised,axis=0)
minvals = np.amin(dataPointsNormalised,axis=0)
maxvals = np.amax(maxvals,axis=0)
minvals = np.amin(minvals,axis=0)
print(maxvals,minvals)
"""

#RNN Data Normalization
RNNDataPointNormalised = RNNDataPoint.copy()
for i in range(RNNDataPoint.shape[0]):
  for j in range(RNNDataPoint.shape[1]):
    RNNDataPointNormalised[i,j,:] = np.divide(RNNDataPoint[i,j,:] - minvals, difvals)
print(RNNDataPointNormalised.shape)
print(np.max(RNNDataPointNormalised))

#RNN Data Normalization
RNNDataPointTestNormalised = RNNDataPointTest.copy()
for i in range(RNNDataPointTest.shape[0]):
  for j in range(RNNDataPointTest.shape[1]):
    RNNDataPointTestNormalised[i,j,:] = np.divide(RNNDataPointTest[i,j,:] - minvals, difvals)
print(RNNDataPointTestNormalised.shape)
print(np.max(RNNDataPointTestNormalised))

train_limit = int(0.8*dataPointsNormalised.shape[0])
X_train = dataPointsNormalised[:train_limit]
X_test = dataPointsNormalised[train_limit:]

print(X_train.shape)
print(X_test.shape)

train_limit = int(0.8*RNNDataPointNormalised.shape[0])
X_train_RNN = RNNDataPointNormalised[:train_limit]
X_test_RNN = RNNDataPointNormalised[train_limit:]

print(X_train_RNN.shape)
print(X_test_RNN.shape)

import torch.nn as nn
import torch.nn.functional as F
import torch

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class MeasStateToState(nn.Module):
  def __init__(self, input_size, output_size):
    super(MeasStateToState, self).__init__()
    self.dense1 = nn.Linear(input_size, 512)
    self.dense2 = nn.Linear(512, 256)
    self.dense3 = nn.Linear(256, 128)
    self.dense4 = nn.Linear(128, output_size)
  
  def forward(self,input):
    x = F.relu(self.dense1(input))
    x = F.relu(self.dense2(x))
    x = F.relu(self.dense3(x))
    x = F.sigmoid(self.dense4(x))
    return x

class StateToMeas(nn.Module):
  def __init__(self, input_size, output_size):
    super(StateToMeas, self).__init__()
    self.dense1 = nn.Linear(input_size, 64)
    self.dense2 = nn.Linear(64, 32)
    self.dense3 = nn.Linear(32, output_size)
  
  def forward(self,input):
    x = F.relu(self.dense1(input))
    x = F.relu(self.dense2(x))
    x = F.sigmoid(self.dense3(x))
    return x

class InitNetwork(nn.Module):
  def __init__(self, input_size, output_size):
    super(InitNetwork, self).__init__()
    self.dense1 = nn.Linear(input_size, 256)
    self.dense2 = nn.Linear(256, 128)
    self.dense3 = nn.Linear(128, output_size)
  
  def forward(self,input):
    x = F.relu(self.dense1(input))
    x = F.relu(self.dense2(x))
    x = F.sigmoid(self.dense3(x))
    return x

class dynamics(nn.Module):
  def __init__(self, input_size, hidden_size):
    super(dynamics, self).__init__()
    self.hidden_size = hidden_size
    self.ms2s = MeasStateToState(input_size + hidden_size,hidden_size)
    output_size = input_size
    self.s2m = StateToMeas(hidden_size,output_size)
    self.INet = InitNetwork(11,n_hidden)

  def forward(self, input, hidden):
    prev_state = self.INet(input)
    combined = torch.cat((input, hidden), 1)
    state = self.ms2s(combined)
    measurement = self.s2m(state)
    return measurement, state, prev_state

  def initHidden(self,input):
    #return torch.zeros(1, self.hidden_size)
    return self.INet(input)

n_hidden = 64
dyn = dynamics(11, n_hidden)
dyn.load_state_dict(torch.load('dyn12.pt'))
criterionL1 = nn.L1Loss()
criterionMSE = nn.MSELoss()

learning_rate = 0.005 # If you set this too high, it might explode. If too low, it might not learn
optimizer = torch.optim.Adam(dyn.parameters(), lr=learning_rate)
def trainOne(datapointL):
    state = dyn.initHidden()
    loss = 0.0
    meas = datapointL[0]
    for i in range(datapointL.shape[0]-1):
        meas, state, prev_state = dyn(meas, state)
        loss += criterionMSE(meas, datapointL[i+1])
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    return meas, loss.item()

optimizer = torch.optim.Adam(dyn.parameters())
gamma = 0.2
def TrainBatchInitNetwork(dataL):
  batch_size = dataL.shape[0]
  loss = 0.0
  for _ in range(batch_size):
    datap = dataL[_]
    meas = datap[0]
    state = dyn.initHidden(meas)
    for j in range(datap.shape[0]-1):
      pstate = state
      meas, state, prev_state = dyn(meas, state)
      loss += criterionMSE(meas, datap[j+1]) + gamma*criterionMSE(prev_state, pstate)
  optimizer.zero_grad()
  loss.backward()
  optimizer.step()
  return loss.item()

X_train = torch.from_numpy(X_train_RNN)
print(X_train.shape)
X_train = X_train.reshape(X_train.shape[0],X_train.shape[1],1,X_train.shape[2]).float()
print(X_train.shape)

X_test = torch.from_numpy(X_test_RNN)
print(X_test.shape)
X_test = X_test.reshape(X_test.shape[0],X_test.shape[1],1,X_test.shape[2]).float()
print(X_test.shape)

import tqdm
batch_size =2048
avg_loss = []
epochs = 100
val_loss = []
for epoch in range(epochs):
  loss = 0
  n = 0
  for i in range(0,X_train.shape[0], batch_size):
    ll = i
    hl = min(i+batch_size,X_train.shape[0])
    batch_data = X_train[ll:hl]
    loss+=TrainBatchInitNetwork(batch_data)
    n+=1
  avg_loss.append(loss/n)
  print("Epoch: ",epoch,"Loss: ",loss/n)
  # validation
  loss = 0
  n = 0
  for i in range(0,X_test.shape[0], batch_size):
    ll = i
    hl = min(i+batch_size,X_train.shape[0])
    batch_data = X_train[ll:hl]
    for _ in range(batch_data.shape[0]):
      datap = batch_data[_]
      meas = datap[0]
      state = dyn.initHidden(meas)
      lloss = 0
      for j in range(datap.shape[0]-1):
        pstate = state
        meas, state, prev_state = dyn(meas, state)
        lloss += criterionMSE(meas, datap[j+1])
      loss+=lloss.item()
    val_loss.append(loss)
    n+=1
  print("Epoch: ",epoch,"Val Loss: ",loss/n)

plt.plot(np.array(avg_loss))
plt.plot(np.array(val_loss))

torch.save(dyn.state_dict(), 'dyn13.pt')

X_no_fail = torch.from_numpy(RNNDataPointNormalised)
X_no_fail = X_no_fail.reshape(X_no_fail.shape[0],X_no_fail.shape[1],1,X_no_fail.shape[2])
lossArray = []
for _ in range(X_no_fail.shape[0]):
  datap = X_no_fail[_].float()
  meas = datap[0]
  state = dyn.initHidden(meas)
  loss = 0
  for j in range(datap.shape[0]-1):
    pstate = state
    meas, state, prev_state = dyn(meas, state)
    loss += criterionMSE(meas, datap[j+1])
  lossArray.append(loss)

datap = X_no_fail[0].float()
meas = datap[0]
state = dyn.initHidden(meas)
print(datap[0],meas)
statestore = [datap[0].numpy(), meas.numpy()]
for j in range(datap.shape[0]-1):
  pstate = state
  with torch.no_grad():
    meas, state, prev_state = dyn(meas, state)
  statestore.append([datap[j+1].numpy(),meas.numpy()])

plt.plot(np.array(lossArray))

X_fail = torch.from_numpy(RNNDataPointTestNormalised)
X_fail = X_fail.reshape(X_fail.shape[0],X_fail.shape[1],1,X_fail.shape[2])
lossArray = []
for _ in range(X_fail.shape[0]):
  datap = X_fail[_].float()
  meas = datap[0]
  state = dyn.initHidden(meas)
  loss = 0
  for j in range(datap.shape[0]-1):
    pstate = state
    meas, state, prev_state = dyn(meas, state)
    loss += criterionMSE(meas, datap[j+1])
  lossArray.append(abs(float(loss)))

plt.plot(np.array(lossArray))
print(lossArray)

mark = list(RNNMarking)
c=['r*','bo']
print(len(lossArray[:-1]),len(mark))
plt.plot(mark,lossArray[1:],'b*')
print(np.sum(mark))
limitVal = 0.05
mismatch_Array = []
mark1loss = []
mark0loss = []
j1, j2, j3, j4 = 0, 0, 0, 0
for i in range(len(mark)):
  if lossArray[i] < limitVal:
    if mark[i] == 0:
      mark0loss.append(lossArray[i])
      mismatch_Array.append([0,0])
      j1+=1
    else:
      mark1loss.append(lossArray[i])
      mismatch_Array.append([1,1])
      j2+=1
  else:
    if mark[i] == 0:
      mark0loss.append(lossArray[i])
      mismatch_Array.append([1,-1])
      j3+=1
    else:
      mark1loss.append(lossArray[i])
      mismatch_Array.append([0,0])
      j4+=1

mismatch_Array = np.array(mismatch_Array)
mark1loss = np.array(mark1loss)
mark0loss = np.array(mark0loss)

print(np.sum(mismatch_Array[:,0]))
print(j1,j2,j3,j4)

x = mark1loss
print(x.shape)
plt.hist(x, bins = 100)
plt.show()

x = mark0loss
print(x.shape)
plt.hist(x, bins = 100)
plt.show()