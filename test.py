#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import sys
from koheron import command, connect
import matplotlib.pyplot as plt
import numpy as np

class AdcDacDma(object):
    def __init__(self, client):
        self.n = 8*1024*1024
        self.client = client
        self.dac = np.zeros((self.n))
        self.adc = np.zeros((self.n))

    @command()
    def select_adc_channel(self, channel):
        pass

    @command()
    def set_dac_data(self, data):
        pass

    def set_dac(self, warning=False, reset=False):
        if warning:
            if np.max(np.abs(self.dac)) >= 1:
                print('WARNING : dac out of bounds')
        dac_data = np.uint32(np.mod(np.floor(8192* self.dac) + 8192, 16384)+8192)
        print dac_data + ( dac_data << 16)
        self.dac = dac_data + ( dac_data << 16) 
        self.set_dac_data(dac_data + ( dac_data << 16))

    @command()
    def start_dma(self):
        pass

    @command()
    def stop_dma(self):
        pass

    @command()
    def get_adc_data(self):
        return self.client.recv_array(self.n/2, dtype='uint32')

    def get_adc(self):
        data = self.get_adc_data()
        self.adc = (np.int32(data % 16384) - 8192) % 16384 - 8192
        self.adc = (np.int32(data >> 16) - 8192) % 16384 - 8192
        #self.adc[::2] = (np.int32(data & 0xFFFF ))
        #self.adc[1::2] = (np.int32(data >> 16) & 0xFFFF )

if __name__=="__main__":
    host = os.getenv('HOST','192.168.1.7')
    client = connect(host, name='adc-dac-dma')
    driver = AdcDacDma(client)


    fs = 125e6
    t = np.arange(driver.n) / fs

    with open(os.path.join(sys.path[0], 'int3_cf125')) as f:
        data = f.read()
    x = [float(i) for i in data.split()]
    x = np.array(x)
    print x
    
    freq_mod = fs / 8 
    driver.dac = x # 0.9 * np.cos(2 * np.pi * freq_mod * t * 1) 
    driver.set_dac()

    adc = np.zeros(driver.n)

    print("Get ADC0 and ADC1 data ({} points)".format(driver.n))
    driver.start_dma()
    driver.get_adc()
    driver.stop_dma()

    n_pts = -1
    print("Plot first {} points".format(n_pts))
    print driver.adc
    plt.plot(driver.dac >> 16)
    plt.plot(driver.adc)
#    plt.ylim((-2**13-1000, 2**13+1000))
    plt.xlabel('Time (ns)')
    plt.ylabel('ADC Raw data')
    plt.show()
