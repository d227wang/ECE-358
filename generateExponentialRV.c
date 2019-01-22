#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <float.h>
#include <time.h>

int main()
{
	double findMean(double[], int);
	double findVariance(double[], int, double);

	double lambda = 75; 
	srand(time(NULL));
	
	double randomNumArray[1000]; 

	for (int i = 0; i < 1000; i++){
		double U = rand() / nextafter(RAND_MAX, DBL_MAX);
		double x = -(1/lambda)*log(1-U);
		randomNumArray[i] = x;
	}

	double mean = findMean(randomNumArray, 1000);
	double var = findVariance(randomNumArray, 1000, mean);
	
	printf("expected mean: 1/75 = 0.0133\n");
	printf("expected var: 1/(75^2) = 0.000178\n");
	printf("mean: %lf \n", mean);
	printf("var: %lf \n", var);
}

double findMean(double numbers[], int arrayLength)
{
	double sum = 0; 
	for (int i = 0; i < arrayLength; i++) {
		sum += numbers[i];
	}
	return sum / arrayLength; 
}

double findVariance(double numbers[], int arrayLength, double mean)
{
	double var = 0; 
	for (int i = 0; i < arrayLength; i++) {
		var += pow((numbers[i] - mean), 2);
	}
	return var/arrayLength; 
}

