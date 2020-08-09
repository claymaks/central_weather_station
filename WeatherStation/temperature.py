import time
import board
import adafruit_dht
import requests

inside_sensor = adafruit_dht.DHT11(board.D23)
ouside_sensor = adafruit_dht.DHT11(board.D24)
measure_delay = 10 # * 60
buffer = 60 * 60
temp_i_buffer = []
temp_o_buffer = []

humi_i_buffer = []
humi_o_buffer = []

dt_buffer = []

while True:
    for i in range(buffer // measure_delay):
        read_success = False
        
        attempt = 0
        while not read_success:
            print("(", i, ", ", attempt, ")", sep='')
            attempt += 1
            try:
                # Print the values to the serial port
                temperature_c_i = inside_sensor.temperature
                if temperature_c_i is None:
                    raise ValueError
                temperature_f_i = temperature_c_i * (9 / 5) + 32
                humidity_i = inside_sensor.humidity
                print("\tINSIDE:")
                print("\t\tTemp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(
                    temperature_f_i, temperature_c_i, humidity_i))

                temperature_c_o = ouside_sensor.temperature
                if temperature_c_o is None:
                    raise ValueError
                temperature_f_o = temperature_c_o * (9 / 5) + 32
                humidity_o = ouside_sensor.humidity
                print("\tOUTSIDE:")
                print("\t\tTemp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(
                    temperature_f_o, temperature_c_o, humidity_o))

                read_success = True

            except RuntimeError as error:
                # Errors happen fairly often, DHT's are hard to read, just keep going
                print("\n", error.args[0].upper(), "\n")
                read_success = False
            except ValueError:
                print("\nBAD READ\n")
                read_success = False

        temp_i_buffer.append(temperature_f_i)
        temp_o_buffer.append(temperature_f_o)
        humi_i_buffer.append(humidity_i)
        humi_o_buffer.append(humidity_o)
        dt_buffer.append(int(time.time()))
        
        time.sleep(measure_delay)
        
    r1 = requests.post("http://cmaks-weather.herokuapp.com/add-data/temperature",
                  json={'dt': dt_buffer,
                        'inside': temp_i_buffer,
                        'outside': temp_o_buffer}, timeout=20)
    print(r1.status_code)
    r2 = requests.post("http://cmaks-weather.herokuapp.com/add-data/humidity",
                  json={'dt': dt_buffer,
                        'inside': humi_i_buffer,
                        'outside': humi_o_buffer}, timeout=20)
    print(r2.status_code)
    time.sleep(buffer)
