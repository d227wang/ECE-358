#!/usr/bin/env python3
import sys
import numpy as np
import queue as queue
from heapq import heappop, heappush, heapify
from GenerateRV import generateRV

###############################################################################
# Simulate a MM1K queue
#
# NOTE: Largely based on MM1 queue simulator, comments will only cover portions 
# not in MM1 queue simulator. Please see that file for additional comments
#
# Largest difference between the two simulators was that a min heap had to be 
# used for this MM1K simulator as it allows departure events to be added and 
# sorted much faster than for an array. Also a queue object is used instead of
# keeping track of the simulated queue by the difference in packets arrived counter
# and packets departed counter. This was done to improve code readability.
###############################################################################

bufferSize = 10
L = 2000
C = 1e6

class Event:
	ARRIVAL = 1
	DEPARTURE = 2
	OBSERVATION = 3

	#Contructor
	def __init__(self, time, type):
		self.time = time
		self.type = type

	#Definition of less than comparitor needed to use Event objects in a min heap
	def __lt__(self, other):
		return self.time < other.time

def getDifference(current, previous):
	if current == previous:
		return 1
	try:
		return (abs(current - previous) / previous)
	except ZeroDivisionError:
		return 0

def generateEventTimes(eventsHeap, lam, simTime, type):
	eventTimes = np.zeros(int(simTime*(2*lam)))
	runningTime = 0
	while runningTime < simTime:
		time = generateRV(lam)
		runningTime += time
		event = Event(runningTime, type)
		heappush(eventsHeap, event)

def processEvents(eventsHeap):
	N_a = 0
	N_d = 0
	N_o = 0
	avgQueue = 0
	idleCounter = 0
	droppedCounter = 0
	endOfQueue = 0
	waitTime = 0

	q = queue.Queue(bufferSize)

	while True: 
		try:
			event = heappop(eventsHeap)
		#Exception catcher, will run when heap is empty to break while loop
		except: 
			break

		if event.type == Event.ARRIVAL:
			N_a += 1
			if q.full():
				droppedCounter += 1
			else:
				q.put(event)
				currentTime = event.time

				# Case that there are packets in the queue and the newly arrived packet will have to wait
				if endOfQueue > currentTime:
					waitTime = endOfQueue - currentTime
				# No packets are currently in the queue 
				else:
					waitTime = 0
				packetLength = generateRV(1/L)
				serviceTime = packetLength / C
				departureTime = currentTime + waitTime + serviceTime
				heappush(eventsHeap, Event(departureTime, Event.DEPARTURE))
				endOfQueue = departureTime

		elif event.type == Event.DEPARTURE:
			N_d += 1
			#Dequeue the departure event
			q.get()
		elif event.type == Event.OBSERVATION:
			N_o += 1
			if q.empty():
				idleCounter += 1
			# Same formula from MM1 simulator for Cumulative moving average: https://en.wikipedia.org/wiki/Moving_average
			avgQueue = (avgQueue * (N_o - 1) + q.qsize()) / N_o

	P_idle = idleCounter / N_o
	# Probability of a packet being droped is the number of packets dropped per total packets processed (N_a)
	P_drop = droppedCounter / N_a
	return {'avgQueue': avgQueue, 'P_idle': P_idle, 'P_drop': P_drop}

def setupEvents(eventsHeap, simTime, rho):

	lam = C*rho/L
	alpha = lam*5
	generateEventTimes(eventsHeap, lam, simTime, Event.ARRIVAL)
	generateEventTimes(eventsHeap, alpha, simTime, Event.OBSERVATION)

# Run simualtor for buffer size of 10, 25, 50 packets and for 0.5<=rho<=1.5.
# Simlulator starts with a simulation time of 1000 s and doubles that if there is a difference of over 5%
# in a metric of interest between two runs.
def main():
	print("============================BEGIN SIMULATION============================")
	print("Sim. T, Rho, Buffer size, Average in queue, Drop probability, differnce w/ last run: ")
	for bs in (25, 50):
		np.set_printoptions(threshold=sys.maxsize)	
		simTime = 1000
		error = 1
		errors = np.zeros(11)
		prevousResult = [{'avgQueue': 0 , 'P_drop': 0} for n in range(11)]
		firstRun = True
		bufferSize = bs
		while error > 0.05:
			for i in range(11):
				rho = round(0.5 + 0.1*i, 2)

				eventsHeap = []
				setupEvents(eventsHeap, simTime, rho)

				result = processEvents(eventsHeap)

				if prevousResult[i]['avgQueue'] != 0  and prevousResult[i]['P_drop'] != 0:
					errors[i] = max(getDifference(result['avgQueue'], prevousResult[i]['avgQueue']), 
						getDifference(result['P_drop'], prevousResult[i]['P_drop']))

				print(simTime,", ", rho,", ", bufferSize,", ", round(result['avgQueue'], 8), ", ", round(result['P_drop'], 8), ", ", round(errors[i],8))
				prevousResult[i]['avgQueue'] = result['avgQueue']
				prevousResult[i]['P_drop'] = result['P_drop']

			if not firstRun:
				error = np.max(errors)
			simTime = simTime*2
			firstRun = False
	print("============================SIMULATION COMPLETE============================")

if __name__ == '__main__':
	main()