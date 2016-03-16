import math 

class WGS84toNED:
		
	def __init__(self):
		
		#//! Semi-major axis.
		self.c_wgs84_a = 6378137.0
		#//! First eccentricity squared.
		self.c_wgs84_e2 = 0.00669437999013
		# Dictionaries
		self.wgs84 = {'latitude': 0,'longitude': 0,'height': 0}
		

	def computeRn(self, lat):
		
		lat_sin = math.sin(lat)
		return (self.c_wgs84_a / math.sqrt(1 - self.c_wgs84_e2 * (lat_sin * lat_sin)))
    
    #   
	#Convert WGS-84 coordinates to ECEF (Earth Center Earth Fixed) coordinates.
	#
	#param[in] lat WGS-84 latitude (rad).
	#param[in] lon WGS-84 longitude (rad).
	#param[in] hae WGS-84 coordinate height (m).
	#param[out] x storage for ECEF x coordinate (m).
	#param[out] y storage for ECEF y coordinate (m).
	#param[out] z storage for ECEF z coordinate (m).
	
	def toECEF(self,wgs84):
		
		ecef = {'x':0,'y':0,'z':0}
		
		cos_lat = math.cos(wgs84.get('latitude'))
		sin_lat = math.sin(wgs84.get('latitude'))
		cos_lon = math.cos(wgs84.get('longitude'))
		sin_lon = math.sin(wgs84.get('longitude'))
		rn = self.computeRn(wgs84.get('latitude'))
		
		#print ("antes",ecef)
		ecef['x'] = (rn + wgs84.get('height')) * cos_lat * cos_lon
		ecef['y'] = (rn +  wgs84.get('height')) * cos_lat * sin_lon
		ecef['z'] = (((1.0 - self.c_wgs84_e2) * rn) + wgs84.get('height')) * sin_lat
		#print ("despues",ecef)
		return ecef
    

    #
    # Compute North-East-Down displacement between two WGS-84
    # coordinates.
    #
    #param pointA WGS-84 coordinates of point A.
    #param pointB WGS-84 coordinates of point B.
    #return displacement in North-East-Down coordinates.
	def displacement(self, pointA, pointB):
		
		ned = {'north': 0, 'east': 0, 'down': 0}
		ecefA = self.toECEF(pointA)
		ecefB = self.toECEF(pointB)
		print ("A",ecefA)
		print ("B",ecefB)
	
		ox = ecefB.get('x') - ecefA.get('x')
		oy = ecefB.get('y') - ecefA.get('y')
		oz = ecefB.get('z') - ecefA.get('z')

		slat = math.sin(pointA.get('latitude'))
		clat = math.cos(pointA.get('latitude'))
		slon = math.sin(pointA.get('longitude'))
		clon = math.cos(pointA.get('longitude'))


		ned['north'] = -slat * clon * ox - slat * slon * oy + clat * oz
		ned['east'] = -slon * ox + clon * oy
		ned['down'] = -clat * clon * ox - clat * slon * oy - slat * oz
		
		return ned
		
		
'''       
def main():
	
	pointA = {'latitude' : 39.4938288117,'longitude' : -0.37795945543,'height' : -5.21203333446}
	pointB = {'latitude' : 39.4941939544,'longitude' : -0.377955617355,'height' : -4.52252019332}
	# deberia dar x:16.6071179549
	tranformWGS = WGS84toNED()
	print(tranformWGS.displacement(pointA,pointB))
	


if __name__ == "__main__":
	main()    
'''    
    
