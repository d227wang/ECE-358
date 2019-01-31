#!/usr/bin/env python3
import sys
import numpy as np
from enum import Enum
from GenerateRV import generateRV
from GenerateRV import generateRVArray


###############################################################################
# Simulate a MM1 queue
#
# Functions: 
# getDifference(current, previous) - Helper function to calculate the difference
#                    			     between two values, used in finding proper 
#                    			     simulation time 
# calculateDepartureTimes(sortedDES) - Calculates the departure times of each
#                             		   packet. Requires a sorted DES table as 
#									   input
# generateEventTimes(lam, simTime) - Generates a list of events with rate param-
#                             		 eter lam and end time simTime. Used to gen-
#									 erate Arrival and Observation times 
# processEvents(events) - Heart of the simulator, processes list of events. Each
#                         event in list is iterated through and acted on based on
#						  event type
# setupEvents(simTime, rho) - Completes all set up of sorted list of events
#
###############################################################################


class Event(Enum):
	ARRIVAL = 1
	DEPARTURE = 2
	OBSERVATION = 3

def getDifference(current, previous):
	if current == previous:
		return 1
	try:
		return (abs(current - previous) / previous)
	except ZeroDivisionError:
		return 0

def calculateDepartureTimes(sortedDES):
	numEvents = sortedDES.shape[0]
	departureTimes = np.zeros(numEvents)
	
	for i in range(numEvents):
		# Case that packet arrives after previous has departed
		if i == 0 or sortedDES[i, 0] >= departureTimes[i-1]:
			departureTimes[i] = sortedDES[i, 0] + sortedDES[i, 2]
		# Case that packet arrives before previous has departed, need to add packet to queue
		else:
			departureTimes[i] = departureTimes[i-1] + sortedDES[i, 2]
	return departureTimes

def generateEventTimes(lam, simTime):
	eventTimes = np.zeros(int(simTime*(2*lam)))
	runningTime = 0
	i = 0
	while runningTime < simTime:
		time = generateRV(lam)
		runningTime += time
		eventTimes[i] = runningTime
		i += 1
	eventTimes = np.trim_zeros(eventTimes, 'b')
	return np.array(eventTimes)

def processEvents(events):
	N_a = 0
	N_d = 0
	N_o = 0
	avgQueue = 0
	idleCounter = 0
	for event in events: 
		if event[0] == Event.ARRIVAL:
			N_a += 1
		elif event[0] == Event.DEPARTURE:
			N_d += 1
		elif event[0] == Event.OBSERVATION:
			N_o += 1
			diff = N_a - N_d
			# Case that all packets that have arrived have also departed, therefore no packet in queue
			if diff == 0:
				idleCounter += 1
			# Calculation of Cumulative moving average: https://en.wikipedia.org/wiki/Moving_average
			avgQueue = (avgQueue * (N_o - 1) + diff) / N_o
	# As observation times are random, probability of the queue being idle is simply number of times
	# observed as idle over the number of observations
	P_idle = idleCounter/N_o
	return {'avgQueue': avgQueue, 'P_idle': P_idle}

def setupEvents(simTime, rho):
	L = 2000
	C = 1e6
	lam = C*rho/L
	alpha = lam*5

	arrivalTimes = generateEventTimes(lam, simTime)
	packetLengths = generateRVArray(1/L, arrivalTimes.shape[0])
	serviceTimes = packetLengths / C

	DES = np.column_stack((arrivalTimes.T, packetLengths.T, serviceTimes.T))
	sortedDES = DES[DES[:, 0].argsort()]

	departureTimes = calculateDepartureTimes(sortedDES)
	completeDES = np.column_stack((sortedDES, departureTimes.T))

	observationTimes = generateEventTimes(alpha, simTime)

	arrivalLabels = np.full((arrivalTimes.shape[0]), Event.ARRIVAL)
	departureLabels = np.full((departureTimes.shape[0]), Event.DEPARTURE)
	observationLabels = np.full((observationTimes.shape[0]), Event.OBSERVATION)

	arrivalEvents = np.column_stack((arrivalLabels.T, sortedDES[:,0]))
	departureEvents = np.column_stack((departureLabels.T, completeDES[:,3]))
	observationEvents = np.column_stack((observationLabels.T, observationTimes))   	

	events = np.vstack((arrivalEvents, departureEvents, observationEvents))
	return events[events[:, 1].argsort()]

# Run simualtor for 0.25<=rho<=9.5.
# Simlulator starts with a simulation time of 1000 s and doubles that if there is a difference of over 5%
# in a metric of interest between two runs.
def main():
	# Prevent long outputs from being truncated
	np.set_printoptions(threshold=sys.maxsize)	
	simTime = 1000
	error = 1
	errors = np.zeros(8)
	prevousResult = [{'avgQueue': 0 , 'P_idle': 0} for n in range(8)]
	firstRun = True
	print("============================BEGIN SIMULATION============================")
	print("Sim. T, Rho, Average in queue, Idle propability, differnce w/ last run: ")
	while error > 0.05:
		for i in range(8):
			rho = round(0.25 + 0.1*i, 2)
			sortedEvents = setupEvents(simTime, rho)
			result = processEvents(sortedEvents)
			if prevousResult[i]['avgQueue'] != 0 and prevousResult[i]['P_idle'] != 0:
				# Check error/difference for both metrics of interest
				errors[i] = max(getDifference(result['avgQueue'], prevousResult[i]['avgQueue']), getDifference(result['P_idle'], prevousResult[i]['P_idle']))

			print(simTime,", ", rho,", ", round(result['avgQueue'], 8),", ",round(result['P_idle'], 8) ,", ", round(errors[i],8))
			prevousResult[i]['avgQueue'] = result['avgQueue']
			prevousResult[i]['P_idle'] = result['P_idle']

		#Errors should not be calculated on first run
		if not firstRun:
			error = np.max(errors)
		simTime = simTime*2
		firstRun = False
	print("============================SIMULATION COMPLETE============================")

if __name__ == '__main__':
	main()