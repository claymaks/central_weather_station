import time
import board
import adafruit_dht

inside_sensor = adafruit_dht.DHT11(board.D23)
ouside_sensor = adafruit_dht.DHT11(board.D24)


while True:
    try:
        # Print the values to the serial port
        temperature_c_i = inside_sensor.temperature
        temperature_f_i = temperature_c_i * (9 / 5) + 32
        humidity_i = inside_sensor.humidity
	print("\tTemp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(
              temperature_f_i, temperature_c_i, humidity_i
            )
        )

		     
        temperature_c_o = inside_sensor.temperature
        temperature_f_o = temperature_c_o * (9 / 5) + 32
        humidity_o = inside_sensor.humidity
        print("\tTemp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(
                temperature_f_o, temperature_c_o, humidity_o
            )
        )
        
    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
 
    time.sleep(2.0)

