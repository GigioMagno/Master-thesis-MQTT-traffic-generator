##################################### CLASS #############################################
################################# DISTRIBUTIONS #########################################
# CURRENT # 
# This class contains static methods that are used to generate random number over the
# support [inf, sup]. At the moment uniform, gaussian and exponential distributions are
# implemented.
# Static method have been chosen because is not necessary instantiate an object 
# distribution and also because it is not necessary access to the state of the object.


import numpy as np
import math

class Distributions:
		
	@staticmethod
	def draw_from_uniform(inf, sup, default=1.0):
		
		if inf is not None and sup is not None:

			return np.random.uniform(inf, sup)
		else:

			return default




	@staticmethod
	def draw_from_exponential(inf, sup, default=1.0):
		
		if inf is not None and sup is not None:

			scale = max(0.001, (sup - inf)/2)
			period = np.random.exponential(scale) + inf
			return min(max(period, inf), sup)	#clamp within range [inf, sup]
		else:

			return default




	@staticmethod
	def draw_from_gaussian(inf, sup, default=1.0):
		
		if inf is not None and sup is not None:

			mean = (inf + sup)/2
			stddev = max(0.001, (sup - inf)/4)
			period = np.random.normal(mean, stddev)
			return min(max(period, inf), sup)	#clamp within range [inf, sup]
		else:

			return default