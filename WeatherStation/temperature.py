import sys
import time
import board
import requests
import argparse
import adafruit_dht


class BadRead(Exception):
    pass


def complete_request(func, addr, *args, **kwargs):
    """
    Exponential backoff
    """
    try:
        recv = func(addr, **kwargs)
    except requests.exceptions.ReadTimeout:
        recv = R()
        recv.ok = False

    succeeded = recv.ok
    n = 1
    while not succeeded and n <= 5:
        print(". BACKOFF: {} ({}ms)".format(n, int(1000 * (2 ** n) / 100)))
        try:
            recv = func(addr, **kwargs)
            succeeded = recv.ok
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
            print(".   ERROR:", e)
            time.sleep((2 ** n) / 100)
            n += 1
        else:
            n += 1
    if n > 5:
        print(".   FAILED")

    return recv


def main(buffer=60*30, measure_delay=10*60,
         inside_sensor=adafruit_dht.DHT11(board.D23),
         outside_sensor=adafruit_dht.DHT11(board.D24)):
    temp_i_buffer = []
    temp_o_buffer = []

    humi_i_buffer = []
    humi_o_buffer = []

    dt_buffer = []
    while True:
        temp_i_buffer = []
        temp_o_buffer = []

        humi_i_buffer = []
        humi_o_buffer = []

        dt_buffer = []
        for i in range(buffer // measure_delay):
            read_success = False
            
            attempt = 0
            while not read_success:
                print("\t(", i, ", ", attempt, ")", sep='')
                attempt += 1
                try:
                    # Print the values to the serial port
                    temperature_c_i = inside_sensor.temperature
                    if temperature_c_i is None:
                        raise BadRead
                    temperature_f_i = temperature_c_i * (9 / 5) + 32
                    humidity_i = inside_sensor.humidity
                    print("\tINSIDE:")
                    print("\t\tTemp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(
                        temperature_f_i, temperature_c_i, humidity_i))

                    temperature_c_o = outside_sensor.temperature
                    if temperature_c_o is None:
                        raise BadRead
                    temperature_f_o = temperature_c_o * (9 / 5) + 32
                    humidity_o = outside_sensor.humidity
                    print("\tOUTSIDE:")
                    print("\t\tTemp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(
                        temperature_f_o, temperature_c_o, humidity_o))

                    read_success = True

                except RuntimeError as error:
                    # Errors happen fairly often, DHT's are hard to read, just keep going
                    print("\n\t", error.args[0].upper(), "\n")
                    read_success = False
                except BadRead:
                    print("\n\tBAD READ\n")
                    read_success = False
                    time.sleep(1)

            temp_i_buffer.append(temperature_f_i)
            temp_o_buffer.append(temperature_f_o)
            humi_i_buffer.append(humidity_i)
            humi_o_buffer.append(humidity_o)
            dt_buffer.append(int(time.time()))
            print("\t{}".format(time.time()))
            
            time.sleep(measure_delay)
            
        r1 = complete_request(requests.post, "http://cmaks-weather.herokuapp.com/add-data/temperature",
                      json={'dt': dt_buffer,
                            'inside': temp_i_buffer,
                            'outside': temp_o_buffer}, timeout=20)
        
        r2 = complete_request(requests.post, "http://cmaks-weather.herokuapp.com/add-data/humidity",
                      json={'dt': dt_buffer,
                            'inside': humi_i_buffer,
                            'outside': humi_o_buffer}, timeout=20)
        
        time.sleep(buffer)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", dest="buffer")
    parser.add_argument("--measure", dest="measure_delay")

    args = parser.parse_args(sys.argv[1:])

    main(int(args.buffer), int(args.measure_delay))
