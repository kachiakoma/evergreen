import BME280_read as BME
import adafruit_mcp3008 as readadc


# This error.py file is used for a framework for implementing errors among
# detection within the given environment
# For scalability purposes, try to implement additional features as its own
# function for referencing additional resources for easier integration to the
# mqtt broker handling for message publication
def temp_flag(temp): # temp_flag passes parameter obtained from app.py temperature variable
    Temp = {'msg':0, 'temp':0} # Temp is a dictionary storing the results for condition testing
    # msg will print the error message flag set if the temp parameter falls out of boundary conditions
    Temp['temp'] = temp 
    if(temp < 50.0):
        Temp['msg'] = 'temp to cold'
    elif(temp > 90.0):
        Temp['msg'] = 'temp to hot'

    return Temp



def wind_flag():
    speed = readadc.wind_speed()
    errSpeed = {'msg':0, 'windSpeed':0}
    errSpeed['windSpeed'] = speed
    if(speed == 0):
        errSpeed['msg'] = 'no wind movement'
     
    return errSpeed
        
