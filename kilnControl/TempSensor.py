print("loading kiln.simTemp")

import sys
this = sys.modules[__name__]
import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

from . import config


class TempSensor():
    def __init__(self, time_step):
        threading.Thread.__init__(self)
        self.daemon = True
        self.temperature = 0
        self.time_step = time_step

def frange(start=0, stop=1, jump=0.1):
    factor = 100
    istart = int(start*factor)
    istop = int(stop*factor)
    ijump = int(jump*factor)
    a = [ x /factor for x in range(istart,istop,ijump)]
    #print (a)
    return a

class SimTemp(TempSensor):
    def __init__(self, oven, time_step, sleep_time):
        self.daemon = True
        self.temperature = 0
        self.time_step = time_step
        self.oven = oven
        self.sleep_time = sleep_time

    def runTo(self,currTime):
        t_env      = config.sim_t_env
        c_heat     = config.sim_c_heat
        c_oven     = config.sim_c_oven
        p_heat     = config.sim_p_heat
        R_o_nocool = config.sim_R_o_nocool
        R_ho_noair = config.sim_R_ho_noair
        R_ho = R_ho_noair

        t = t_env  # deg C  temp in oven
        t_h = t    # deg C temp of heat element
        simTime = frange (0,currTime, self.time_step)
        for s in simTime :
            #heating energy
            Q_h = p_heat * self.time_step * self.oven.heat

            #temperature change of heat element by heating
            t_h += Q_h / c_heat

            #energy flux heat_el -> oven
            p_ho = (t_h - t) / R_ho

            #temperature change of oven and heat el
            t   += p_ho * self.time_step / c_oven
            t_h -= p_ho * self.time_step / c_heat

            #temperature change of oven by cooling to env
            p_env = (t - t_env) / R_o_nocool
            t -= p_env * self.time_step / c_oven
            log.debug("energy sim: -> %dW heater: %.0f -> %dW oven: %.0f -> %dW env" % (int(p_heat * self.oven.heat), t_h, int(p_ho), t, int(p_env)))
            self.temperature = t

            #time.sleep(self.sleep_time)

