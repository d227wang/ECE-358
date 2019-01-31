#!/usr/bin/env python3
import sys
import GenerateRV
import MM1QueueSim
import MM1KQueueSim

def main():
	while True:
		command = input("Choose to run: \n 1.Generate Random Variable Test \n 2.MM1 Queue Simulator \n 3.MM1K Queue Simulator \n")
		if command == "1":
			GenerateRV.main()
		elif command == "2":
			MM1QueueSim.main()
		elif command == "3":
			MM1KQueueSim.main()
		else:
			print ("Invalid input, please enter a selection")
if __name__ == '__main__':
    main()