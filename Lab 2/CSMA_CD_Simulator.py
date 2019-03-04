#!/usr/bin/env python3

import sys
import random
import numpy as np
import queue as queue
from enum import Enum
from GenerateRV import generateRV
from GenerateRV import generateRVArray

R = 10**6
L = 1500
D = 10
S = (2/3)*(3*10**8)
trans_delay = L/R
prop_delay = D/S
Tp = 512/R
numEvents = 0

def generateEventTimes(A, simTime):
	global numEvents
	eventTimes = queue.Queue(int(simTime*(2*A)))
	runningTime = 0
	while runningTime < simTime:
		time = generateRV(A)
		runningTime += time
		eventTimes.put(runningTime)
		numEvents += 1
	return eventTimes

def processEvents(nodes):
	packetsTransmitted = 0
	packetsSuccessful = 0
	time = 0

	while (packetsSuccessful < numEvents):
		nextPackets = np.full(len(nodes), np.inf)
		collisionCounters = np.zeros(len(nodes))
		for i in range(len(nodes)):
			if nodes[i].empty() == False:
				nextPackets[i] = nodes[i].queue[0]
		senderIndex = np.argmin(nextPackets)
		# print (nextPackets)
		# print(senderIndex)
		time = nodes[senderIndex].queue[0]

		collisionDetected = False
		for i in range(len(nodes)):
			if i != senderIndex and nodes[i].empty() == False:
				distance = abs(i - senderIndex)
				firstBitArrivalTime = time + distance*prop_delay
				lastBitArrivalTime = firstBitArrivalTime + trans_delay

				# Collision
				if nodes[i].queue[0] < firstBitArrivalTime: 
					# print("collision")
					packetsTransmitted += 1
					collisionCounters[i] += 1
					collisionDetected = True

					if collisionCounters[i] > 10:
						print("dropped")
						nodes[i].get()
						collisionCounters[i] = 0
					else: 
						wait = random.uniform(0, 2**collisionCounters[i] + 1)*Tp
						nodes[i].queue[0] = time + wait

				# Adjust packet times
				elif nodes[i].queue[0] >= firstBitArrivalTime and nodes[i].queue[0] < lastBitArrivalTime:
					# print("Adjust")
					nodes[i].queue[0] = lastBitArrivalTime
			
		if (collisionDetected == False):
			# print("sucess")
			nodes[senderIndex].get()
			packetsTransmitted += 1
			packetsSuccessful += 1
			collisionCounters[i] = 0
		else: 
			wait = random.uniform(0, 2**collisionCounters[senderIndex] + 1)*Tp
			nodes[senderIndex].queue[0] = time + wait

	print(packetsTransmitted)
	print(packetsSuccessful)



def main():
	np.set_printoptions(threshold=sys.maxsize)	
	global numEvents

	numEvents = 0
	N = 40
	A = 12
	simTime = 1000
	
	nodes = [0] * N
	for i in range(0, N):
		nodes[i] = generateEventTimes(A, simTime)
	processEvents(nodes)
	# print(nodes[19].queue[0])

if __name__ == '__main__':
	main()