import utime as time
# from filtering import KalmanFilter
from peers import Target, Result
from machine import Pin, UART


class SwarmbeeError(Exception):
    pass


class RangingError(SwarmbeeError):

    def __init__(self, mac, code, *args):
        super(RangingError, self).__init__(*args)
        self.__reason = {0: "success ranging result valid",
                         1: "(1) ranging to own ID",
                         2: "(2) no hardware ack received",
                         3: "(3) ranging unsuccessful, ranging timer expired",
                         5: "(5) overload, try again",
                         6: "(6) medium blocked CSMA timer expired"}.get(code, "Not a valid error code {}".format(code))
        self.__mac = mac

    @property
    def reason(self):
        return self.__reason

    def __str__(self):
        return "RangingError during ranging of {}: {}".format(self.__mac, self.reason)


class ResponseError(SwarmbeeError):
    pass


class Swarmbee:
    CH1 = {"uart_nr": 4, "baudrate": 115200,
           "pwr_pin": "B2", "rst_pin": "B1", "enable_pin": "B0", "amode_pin": "B4",
           "channel": 1, "led_pin": "C1"}
    CH2 = {"uart_nr": 3, "baudrate": 115200,
           "pwr_pin": "B8", "rst_pin": "B7", "enable_pin": "B6", "amode_pin": "B12",
           "channel": 2, "led_pin": "C2"}

    @staticmethod
    def decode_pin(val):
        return {4: val & 0b1000 > 0, 3: val & 0b0100 > 0, 2: val & 0b0010 > 0, 1: val & 0b0001 > 0}

    def __init__(self, *, reset=False, buffer=512, verbose_mode=True):
        self.__filters_dict = {}
        self.__power_pin = Pin(Swarmbee.CH2.get('pwr_pin'), Pin.OUT)
        self.__reset_pin = Pin(Swarmbee.CH2.get('rst_pin'), Pin.OUT)
        self.__amode_pin = Pin(Swarmbee.CH2.get('amode_pin'), Pin.OUT)
        self.__enable_pin = Pin(Swarmbee.CH2.get('enable_pin'), Pin.OUT)
        self.__led_pin = Pin(Swarmbee.CH2.get('led_pin'), Pin.OUT)
        self.__led_pin.low()
        self.__power_pin.high()
        # self.__reset_pin.high()
        self.__amode_pin.low()
        # time.sleep(1)
        self.__enable_pin.high()
        self.__uart = UART(Swarmbee.CH2.get('uart_nr'), Swarmbee.CH2.get('baudrate'))
        self.__uart.init(Swarmbee.CH2.get('baudrate'), rxbuf=buffer)
        time.sleep_ms(50)
        self.__reset_pin.low()
        print("Activating reset now")
        time.sleep_ms(50)
        self.__reset_pin.high()
        time.sleep_ms(1500)
        startup = self.__uart.read()
        if verbose_mode:
            print(startup)
            # print(self.get_node_id())
        if reset:
            self.send("SFAC",
                      verbose=verbose_mode, hint="Back to factory settings")

    def get_fac_settings(self, reset=True, verbose_mode=True):
        if reset:
            self.send("SFAC", verbose=verbose_mode, hint="Set factory settings")
        self.send("GSET", verbose=verbose_mode, hint="Get factory settings")

    def configure(self, *, syncword=1, csma_threshold=11, verbose_mode=True):
        self.send("BRAR 0",
                  verbose=verbose_mode, hint="Broadcast RAnging Results")
        self.send("SROB 00",
                  verbose=verbose_mode, hint="Sets  range  on  broadcast")
        self.send("STXP 63",
                  verbose=verbose_mode, hint="Sets transmission (TX) Power of the node")
        self.send("SSYC {:02d}".format(syncword),
                  verbose=verbose_mode, hint="Set the PHY SYnCword of swarmnode")
        self.send("SFEC 1",
                  verbose=verbose_mode, hint="Switches Forward Error Correction (FEC) on / off")
        self.send("CSMA 3 5 {}".format(csma_threshold),  # 24 works , 25 not (here)
                  verbose=verbose_mode, hint="Switches CSMA mode and determines back-off factor for CSMA")
        self.send("SDAM 1",
                  verbose=verbose_mode, hint="Sets the node’s data mode to 80/4")
        self.send("ERRN 0",
                  verbose=verbose_mode, hint="Disable Ranging result notification")
        self.send("EDAN 0",
                  verbose=verbose_mode, hint="Disable Data notification")
        self.send("EDNI 0",
                  verbose=verbose_mode, hint="Disable Broadcast notification.")
        self.send("EBID 0",
                  verbose=verbose_mode, hint="Disable Broadcast.")
        self.send("EMSS 0",
                  verbose=verbose_mode, hint="Disable MEMS.")
        self.send("EBMS 0",
                  verbose=verbose_mode, hint="Disable temperature blink.")
        self.send("gpio 0 0 1 0 0",  # GPIO pin_number mode speed push_pull/open_drain no_pull/pull_up/pull_down
                  verbose=verbose_mode, hint="Set Pin 0 as push-pull, 2MHz input with no pull.")
        self.send("gpio 1 0 1 0 0",
                  verbose=verbose_mode, hint="Set Pin 1 as push-pull, 2MHz input with no pull.")
        self.send("gpio 2 0 1 0 0",
                  verbose=verbose_mode, hint="Set Pin 2 as push-pull, 2MHz input with no pull.")
        self.send("gpio 3 0 1 0 0",
                  verbose=verbose_mode, hint="Set Pin 3 as push-pull, 2MHz input with no pull.")
        self.send("SSET", verbose=verbose_mode, hint="Save th config.")

    def save(self):
        self.send("SSET")
        print("saved.")

    def get_gpio_state(self) -> int:
        return int(self.send("gpin").replace("=", ""))

    def get_node_id(self, verbose=False):
        return self.send("GNID", verbose=verbose, hint="Get Node ID").strip()[1:]

    def set_node_id(self, new_mac, verbose_mode=False):
        if isinstance(new_mac, int):
            new_mac = "{:012X}".format(new_mac)
        elif isinstance(new_mac, Target):
            new_mac = "{}".format(new_mac.prepared_mac())
        self.send("SNID {}".format(new_mac),
                  verbose=verbose_mode, hint="Set new ID to {}".format(new_mac))

    def deactivate(self):
        """Kill the Swarmbee."""
        self.__uart.deinit()
        self.__amode_pin.low()
        self.__power_pin.low()
        self.__enable_pin.low()

    def send(self, cmd: str, *, verbose=True, hint=""):
        if not cmd.endswith("\r\n"):
            cmd += "\r\n"
        if verbose and hint != "":
            print(">>", cmd.strip(), " #", hint)
        elif verbose and hint == "":
            print(">>", cmd.strip())
        try:
            self.__uart.write(cmd.encode('UTF-8'))
            # self.__uart.flush()
            time.sleep_ms(200)
            res = self.__uart.read().decode('UTF-8')
            if verbose:
                print("<< {}".format(res.strip()))
        except OSError:
            raise SwarmbeeError("UART connection broken")
        except AttributeError:
            ...
        else:
            return res

    def cont_read(self, cmd, verbose=True):
        if verbose:
            print(">>", cmd.strip())
        if not cmd.endswith("\r\n"):
            cmd += "\r\n"
        try:
            self.__uart.write(cmd.encode('UTF-8'))
            res = self.__uart.read().decode('UTF-8')
            n = 0
            if res.startswith("#"):
                n = int(res[1:])
                print(n)
            while n > 0:
                res += self.__uart.read().decode('UTF-8')
                n -= 1
        except OSError:
            raise SwarmbeeError("UART connection broken")
        if verbose:
            print("<<", res.strip())
        return res

    def reset_filter(self, mac=None):
        if mac is not None:
            if mac in self.__filters_dict:
                del self.__filters_dict[mac]
        else:
            self.__filters_dict.clear()

    def range(self, target: Target):
        try:
            self.__uart.write("RATO 0 {}\r\n".format(target.prepared_mac()).encode("UTF-8"))
            t_start = time.time()
            result = None
            try:
                while True:
                    try:
                        result = self.__uart.read().decode("UTF-8").strip().split(",")
                    except AttributeError:
                        continue
                    except KeyboardInterrupt:
                        break
                    else:
                        break
                print('Result:', result)
                error, dist, rssi = result
                if error != "=0":
                    raise RangingError(target.prepared_mac(), int(error[1]))
                return Result(target, int(dist), int(rssi), took_s=time.time() - t_start)
            except RangingError:
                err = RangingError(target.prepared_mac(), int(error[1]))
                print(err.reason)
                ...
            except ValueError as ve:
                raise ResponseError(str(ve))
        except OSError:
            raise SwarmbeeError("UART connection broken")

    # def filtered_range(self, target: Target, uncertainty=1.5, a_allowed=1.5):
    #     result = self.range(target)
    #     if target.mac not in self.__filters_dict:
    #         self.__filters_dict[target.mac] = KalmanFilter(initial_x=result.distance / 100,
    #                                                        initial_v=0.0,
    #                                                        accel_variance=a_allowed)
    #     else:
    #         self.__filters_dict[target.mac].introduce_new_measurement(meas_value=result.distance / 100,
    #                                                                   meas_variance=uncertainty, age=result.took)
    #     return result, Result(result, self.__filters_dict[target.mac].distance * 100, result.rssi, result.took)


if __name__ == '__main__':
    ...
# import argparse

# parser = argparse.ArgumentParser()
# parser.add_argument("uart", help="path to the device.")
# parser.add_argument("--sync", default=10, type=int, help="Used syncword.")
# parser.add_argument("-mac", "--target", help="Target id to be ranged.")
# parser.add_argument("--reset", default=False, action="store_true", help="Reset to factory settings.")
# parser.add_argument("--save", default=False, action="store_true", help="Save settings.")
# parser.add_argument("-c", "--cmd", default=(), nargs='+', help="Reset to factory settings.")
# parser.add_argument("-n", "--range_amount", default=1, type=int, help="Number of Rangings.")
