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
S = (2/3)*(3*(10**8))
trans_delay = L/R
prop_delay = D/S
Tp = 512/R
numEvents = 0
def getDifference(current, previous):
	if current == previous:
		return 1
	try:
		return (abs(current - previous) / previous)
	except ZeroDivisionError:
		return 0
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

def processEvents(nodes, simTime, persistant):
	packetsTransmitted = 0
	packetsSuccessful = 0
	packetsDropped = 0
	collisionCounters = np.zeros(len(nodes))
	collisionSensingCounters = np.zeros(len(nodes))
	time = 0
	counter = 0

	while (time < simTime):
		nextPackets = np.full(len(nodes), np.inf)
		for i in range(len(nodes)):
			if nodes[i].empty() == False:
				nextPackets[i] = nodes[i].queue[0]
		senderIndex = np.argmin(nextPackets)
		time = nodes[senderIndex].queue[0]

		collisionDetected = False
		for i in range(len(nodes)):
			if i != senderIndex and nodes[i].empty() == False:
				distance = abs(i - senderIndex)
				firstBitArrivalTime = time + distance*prop_delay
				lastBitArrivalTime = firstBitArrivalTime + trans_delay

				# Collision
				if nodes[i].queue[0] < firstBitArrivalTime: 
					packetsTransmitted += 1
					collisionCounters[i] += 1
					collisionDetected = True

					if collisionCounters[i] > 10:
						nodes[i].get()
						packetsDropped += 1
						collisionCounters[i] = 0
					else: 
						wait = random.uniform(0, (2**collisionCounters[i]) - 1)*Tp
						nodes[i].queue[0] = time + wait

				# Adjust packet times
				elif nodes[i].queue[0] >= firstBitArrivalTime and nodes[i].queue[0] < lastBitArrivalTime:
					packetsTransmitted += 1
					if persistant == True:
						nodes[i].queue[0] = lastBitArrivalTime
					else: 
						collisionSensingCounters[i] += 1
						if collisionSensingCounters[i] > 10:
							nodes[i].get()
							packetsDropped += 1
							collisionSensingCounters[i] = 0
						else: 
							wait = random.uniform(0, (2**collisionSensingCounters[i]) - 1)*Tp
							nodes[i].queue[0] = time + wait
			
		if (collisionDetected == False):
			nodes[senderIndex].get()
			packetsTransmitted += 1
			packetsSuccessful += 1
			collisionCounters[i] = 0
			collisionSensingCounters[i] = 0
		else: 
			packetsTransmitted += 1
			collisionCounters[senderIndex] += 1
			wait = random.uniform(0, 2**collisionCounters[senderIndex] - 1)*Tp
			nodes[senderIndex].queue[0] = time + wait
			collisionSensingCounters[i] = 0

	efficiency = packetsSuccessful/packetsTransmitted
	throughput = (packetsSuccessful * L)/simTime
	return {"efficiency": efficiency, "throughput": throughput}



def main():
	np.set_printoptions(threshold=sys.maxsize)	
	global numEvents

	numEvents = 0
	N = [20, 40, 60, 80, 100]
	A = 12
	persistant = True
	simTime = 1000
	error = 1
	errors = np.zeros(len(N))
	firstRun = True
	prevousResult = [{'efficiency': 0 , 'throughput': 0} for n in range(len(N))]
	while error > 0.05:
		print("=====Begin simulation for T: " + str(simTime))
		print("A, N, Efficiency, Throughput, errors")
		for n in range(len(N)):
			nodes = [0] * N[n]
			for i in range(0, N[n]):
				nodes[i] = generateEventTimes(A, simTime)
			e = processEvents(nodes, simTime, persistant)
			

			errors[n] = max(getDifference(e['efficiency'], prevousResult[n]['efficiency']), getDifference(e['throughput'], prevousResult[n]['throughput']))
			prevousResult[n]['efficiency'] = e['efficiency']
			prevousResult[n]['throughput'] = e['throughput']
			
			print( str(A)+ ", " + str(N[n]) + ", " + str(e['efficiency']) + ", " + str(e['throughput'])+ ", " + str(errors[n]))
			

		if not firstRun:
			error = max(errors)
		simTime = simTime*2
		firstRun = False

if __name__ == '__main__':
	main()