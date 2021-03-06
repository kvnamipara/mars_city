from __future__ import division, print_function
from collections import OrderedDict
from threading import Thread
import os
import sys
# import csv
import time
import logging
import ConfigParser
sys.path.insert(0, '../hexoskin_helper')
import anomaly_database_helper as db

# import matplotlib.pyplot as plt

__author__ = "Dipankar Niranjan, https://github.com/Ras-al-Ghul"

# Logging config
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)


class RespiratoryAD(object):
    def __init__(self, config, init_val):
        # set the percent change for get_window
        self.window_delta = 0.003
        # the size of the window to be used in the classifier
        self.resp_classf_win_size = 2

        # the first val of the resp data
        self.init_val = init_val

        # get the tidal volume deltas
        self.tidal_volume_delta =\
            config.getfloat('Respiratory AD', 'tidal_volume_delta')
        self.tidal_volume_window_delta =\
            config.getfloat('Respiratory AD', 'tidal_volume_window_delta')

        # get the minute ventilation deltas
        self.minute_ventilation_delta =\
            config.getfloat('Respiratory AD',
                            'minute_ventilation_delta')
        self.minute_ventilation_window_delta =\
            config.getfloat('Respiratory AD',
                            'minute_ventilation_window_delta')

        # get resp up and down thresholds - in raw units from the baseline
        # upper bounds
        self.up_thresh = config.getint('Respiratory AD', 'up_thresh')
        self.down_thresh = config.getint('Respiratory AD', 'down_thresh')
        # lower bounds
        self.up_low = config.getint('Respiratory AD', 'up_low')
        self.down_low = config.getint('Respiratory AD', 'down_low')

        # get respiratory variation threshold for resp_variation() method
        self.resp_variation_thresh =\
            config.getint('Respiratory AD', 'resp_variation_thresh')

        # raw respiratory data as an OrderedDict
        # key:value = timestamp:(thoracic, abdominal)
        self.raw_resp_dict = OrderedDict()

        # breathing rate dict
        # key:value = timestamp:breathing rate
        self.breathing_rate_dict = OrderedDict()

        # breathing rate status dict
        # key:value = timestamp:breathing rate quality
        self.breathing_rate_status_dict = OrderedDict()

        # inspiration dict
        # key:value = timestamp:inspiration
        self.inspiration_dict = OrderedDict()

        # expiration dict
        # key:value = timestamp:expiration
        self.expiration_dict = OrderedDict()

        # tidal volume (vt) dict
        # key:value = timestamp:tidal volume
        self.tidal_volume_dict = OrderedDict()

        # minute ventilation dict
        # key:value = timestamp:minute ventilation
        self.minute_ventilation_dict = OrderedDict()

        # dict of resp anomalies
        # in general Key:value =\
        #     timestamp:(int(breathing rate status mean), 'string')
        # -1 for breathing rate status if not applicable
        # mean is mean of breathing rate status in that period
        # key:value = timestamp:(-1, 'tidal_window'/'tidal_not_window')
        # key:value =\
        #     timestamp:(-1, 'minute_vent_window'/'minute_vent_not_window')
        # key:value = timestamp:(-1, 'insp-exp'/'exp-inp')
        self.resp_anomaly_dict = OrderedDict()

    def delete_DS(self):
        # method to maintain data structures' size

        # initial wait time
        time.sleep(60*10)
        while self.raw_resp_dict:
            for i in xrange(200):
                self.raw_resp_dict.popitem(last=False)

            self.breathing_rate_dict.popitem(last=False)
            self.breathing_rate_status_dict.popitem(last=False)
            self.inspiration_dict.popitem(last=False)
            self.expiration_dict.popitem(last=False)
            self.tidal_volume_dict.popitem(last=False)
            self.minute_ventilation_dict.popitem(last=False)
            time.sleep(20)

        return

    def minute_ventilation_anomaly(self):
        time.sleep(200)
        logging.info("minute ventilation begin")
        # check if i+1 is out of (ith +/- delta) range
        # check if i+1 is out of (i-5 to ith window +/- window delta range)

        # get the initial timestamp
        begin = self.minute_ventilation_dict.popitem(last=False)[0]

        # assuming window size to be 5
        window = []
        # skip 10 timestamps
        count = 0
        while count < 10:
            if begin + 1 in self.minute_ventilation_dict:
                count += 1
                if count >= 6:
                    window.append((begin+1,
                                   self.minute_ventilation_dict
                                   [begin+1]))
            begin += 1

        # set prev and begin
        prev = self.minute_ventilation_dict[begin]
        begin += 1

        while len(self.minute_ventilation_dict) > 30:
            time.sleep(15)
            if begin in self.minute_ventilation_dict:
                cur = self.minute_ventilation_dict[begin]

                # check for non window delta
                percent = (self.minute_ventilation_delta/100) * prev
                if not ((prev - percent) < cur < (prev + percent)):
                    self.resp_anomaly_dict[begin] =\
                        (-1, 'minute_vent_not_window')
                    # Anomaly is detected
                    anomaly_dict = {}
                    anomaly_dict['Resp_hexo_timestamp'] = begin

                    anomaly_dict['BRstatus_mean'] = \
                        self.resp_anomaly_dict[begin][0]

                    anomaly_dict['Anomaly_type'] = \
                        self.resp_anomaly_dict[begin][1]

                    db.add_resp(anomaly_dict)
                    logging.info("%s" % str(anomaly_dict))

                # check for window delta
                windowmean = sum([i[1] for i in window])/len(window)
                percent =\
                    (self.minute_ventilation_window_delta/100) * windowmean
                if not ((windowmean - percent) < cur < (windowmean + percent)):
                    self.resp_anomaly_dict[begin] = (-1, 'minute_vent_window')
                    # Anomaly is detected
                    anomaly_dict = {}
                    anomaly_dict['Resp_hexo_timestamp'] = begin

                    anomaly_dict['BRstatus_mean'] = \
                        self.resp_anomaly_dict[begin][0]

                    anomaly_dict['Anomaly_type'] = \
                        self.resp_anomaly_dict[begin][1]

                    db.add_resp(anomaly_dict)
                    logging.info("%s" % str(anomaly_dict))

                # update window
                window.pop(0)
                window.append((begin, cur))
                # update prev
                prev = self.minute_ventilation_dict[begin]

            # update begin
            begin += 1

            # if begin == 383021389273:
            #   print(self.minute_ventilation_anomaly_dict)
        logging.info("minute ventilation end")
        return

    def tidal_volume_anomaly(self):
        time.sleep(200)
        logging.info("tidal_volume begin")
        # check if i+1 is out of (ith +/- delta) range
        # check if i+1 is out of (i-5 to ith window +/- window delta range)

        # get the initial timestamp
        begin = self.tidal_volume_dict.popitem(last=False)[0]

        # assuming window size to be 5
        window = []
        # skip 10 timestamps
        count = 0
        while count < 10:
            if begin + 1 in self.tidal_volume_dict:
                count += 1
                if count >= 6:
                    window.append((begin+1, self.tidal_volume_dict[begin+1]))
            begin += 1

        # set prev and begin
        prev = self.tidal_volume_dict[begin]
        begin += 1

        while len(self.tidal_volume_dict) > 30:
            time.sleep(15)
            if begin in self.tidal_volume_dict:
                cur = self.tidal_volume_dict[begin]

                # check for non window delta
                percent = (self.tidal_volume_delta/100) * prev
                if not ((prev - percent) < cur < (prev + percent)):
                    self.resp_anomaly_dict[begin] =\
                        (-1, 'tidal_volume_not_window')
                    # Anomaly is detected
                    anomaly_dict = {}
                    anomaly_dict['Resp_hexo_timestamp'] = begin

                    anomaly_dict['BRstatus_mean'] = \
                        self.resp_anomaly_dict[begin][0]

                    anomaly_dict['Anomaly_type'] = \
                        self.resp_anomaly_dict[begin][1]

                    db.add_resp(anomaly_dict)
                    logging.info("%s" % str(anomaly_dict))

                # check for window delta
                windowmean = sum([i[1] for i in window])/len(window)
                percent = (self.tidal_volume_window_delta/100) * windowmean
                if not ((windowmean - percent) < cur < (windowmean + percent)):
                    self.resp_anomaly_dict[begin] = (-1, 'tidal_volume_window')
                    # Anomaly is detected
                    anomaly_dict = {}
                    anomaly_dict['Resp_hexo_timestamp'] = begin

                    anomaly_dict['BRstatus_mean'] = \
                        self.resp_anomaly_dict[begin][0]

                    anomaly_dict['Anomaly_type'] = \
                        self.resp_anomaly_dict[begin][1]

                    db.add_resp(anomaly_dict)
                    logging.info("%s" % str(anomaly_dict))

                # update window
                window.pop(0)
                window.append((begin, cur))
                # update prev
                prev = self.tidal_volume_dict[begin]

            # update begin
            begin += 1

            # if begin == 383021389273:
            #   print(self.tidal_volume_anomaly_dict)
        logging.info("tidal_volume end")
        return

    def resp_variation(self):
        time.sleep(200)
        logging.info("resp_variation begin")
        # finds gap between inspiration and expiration
        inspiration = self.init_val
        while True:
            if inspiration in self.inspiration_dict:
                break
            inspiration += 1

        timestamp = []
        while len(self.inspiration_dict) > 20 and\
                len(self.expiration_dict) > 20:
            time.sleep(15)
            expiration = inspiration
            # find expiration
            while True:
                if expiration in self.expiration_dict:
                    break
                expiration += 1

            # if gap is greater than 3 seconds
            if (expiration - inspiration) > (256*self.resp_variation_thresh):
                logging.info('exp, insp')
                self.resp_anomaly_dict[inspiration] = (-1, 'exp-insp')
                # Anomaly is detected
                anomaly_dict = {}
                anomaly_dict['Resp_hexo_timestamp'] = inspiration

                anomaly_dict['BRstatus_mean'] = \
                    self.resp_anomaly_dict[inspiration][0]

                anomaly_dict['Anomaly_type'] = \
                    self.resp_anomaly_dict[inspiration][1]

                db.add_resp(anomaly_dict)
                logging.info("%s" % str(anomaly_dict))
                timestamp.append(inspiration)

            # find inspiration
            inspiration = expiration
            while True:
                if inspiration in self.inspiration_dict:
                    break
                inspiration += 1

            # if gap is greater than 3 seconds
            if (inspiration - expiration) > (256*self.resp_variation_thresh):
                logging.info('insp, exp')
                self.resp_anomaly_dict[expiration] = (-1, 'insp-exp')
                # Anomaly is detected
                anomaly_dict = {}
                anomaly_dict['Resp_hexo_timestamp'] = expiration

                anomaly_dict['BRstatus_mean'] = \
                    self.resp_anomaly_dict[expiration][0]

                anomaly_dict['Anomaly_type'] = \
                    self.resp_anomaly_dict[expiration][1]

                db.add_resp(anomaly_dict)
                logging.info("%s" % str(anomaly_dict))
                timestamp.append(expiration)

            # if inspiration == 383021388517:
            #   break

        # dicts = dict(zip(list(self.raw_resp_dict.keys()),
        #                  [i[0] for i in
        #                   list(self.raw_resp_dict.values())]))
        # plt.plot(list(self.raw_resp_dict.keys()),
        #          [i[0] for i in list(self.raw_resp_dict.values())])
        # plt.plot(timestamp,
        #          [self.raw_resp_dict[i][0] for i in
        #           list(self.raw_resp_dict.keys()) if i in timestamp], 'ro')
        # plt.show()
        # print(timestamp)
        logging.info("resp_variation end")
        return

    def get_cur_window(self, init):
        # inspiration and expiration windows
        window_insp, window_exp = [], []
        # last value
        ending_val = None

        while not (window_insp and window_exp):
            # get the first inspiration or expiration
            # 'including' the passed timestamp
            # flag is True if key found, False if not
            startinsp, startexp = init, init
            # flags to find the starting point which will be used as prev
            startinspflag, startexpflag = False, False
            for count in xrange(256*20):
                # inspiration
                if (not startinspflag) and\
                        ((startinsp + count) in self.inspiration_dict):
                    # insp val found
                    startinsp += count
                    startinspflag = True
                # expiration
                if (not startexpflag) and\
                        ((startexp + count) in self.expiration_dict):
                    # exp val found
                    startexp += count
                    startexpflag = True

            window_insp, window_exp = [], []
            # if the flags are set, it indicates that prev values can be set
            if (startinspflag and startexpflag):
                previnsp, prevexp = startinsp, startexp
                loopflag = True
                while loopflag:
                    count = 1
                    # flags to indicate that the current values have been found
                    inspinner, expinner = False, False
                    while count <= (256*40):
                        # inspiration
                        if (not inspinner) and\
                                ((previnsp + count) in self.inspiration_dict):
                            curinsp = previnsp + count
                            # the threshold
                            percent =\
                                self.window_delta * \
                                self.inspiration_dict[previnsp]
                            if (self.inspiration_dict[previnsp] - percent <
                                self.inspiration_dict[curinsp] <
                                    self.inspiration_dict[previnsp] + percent):
                                # in the threshold
                                window_insp.append((curinsp,
                                                    self.inspiration_dict
                                                    [curinsp]))
                            else:
                                # outside threshold
                                ending_val = curinsp
                                loopflag = False
                                init = curinsp + 1
                                inspinner = True
                                expinner = True
                                break
                            previnsp = curinsp
                            inspinner = True
                        # expiration
                        if (not expinner) and (prevexp + count)\
                                in self.expiration_dict:
                            curexp = prevexp + count
                            # the threshold
                            percent =\
                                self.window_delta * \
                                self.expiration_dict[prevexp]
                            if (self.expiration_dict[prevexp] - percent <
                                self.expiration_dict[curexp] <
                                    self.expiration_dict[prevexp] + percent):
                                # in the threshold
                                window_exp.append((curexp, self.expiration_dict
                                                   [curexp]))
                            else:
                                # outside threshold
                                ending_val = curexp
                                loopflag = False
                                init = curexp + 1
                                inspinner = True
                                expinner = True
                                break
                            prevexp = curexp
                            expinner = True

                        count += 1

                    # current values not found, end of OrderedDict
                    if not (inspinner and expinner):
                        if window_insp and window_exp:
                            loopflag = False
                            ending_val = max(
                                         window_insp[len(window_insp)-1][0],
                                         window_exp[len(window_exp)-1][0])
                        else:
                            return (-1, -1, -1)
            # flags haven't been set, so there is no prev
            # basically, it means reached end of OrderedDict
            else:
                return (-1, -1, -1)

        # print(window_insp)
        # plt.plot([i[0] for i in window_insp], [i[1] for i in window_insp])
        # print(window_exp)
        # plt.plot([i[0] for i in window_exp], [i[1] for i in window_exp])
        # print(ending_val)
        return (ending_val, window_insp, window_exp)

    def get_breathing_rate(self, first, last):
        # get the breathing rate and breathing rate status
        # includes first and last
        breathing_rate = []
        breathing_rate_status = []
        for i in xrange(first, last + 1):
            if i in self.breathing_rate_dict:
                breathing_rate.append(self.breathing_rate_dict[i])
                breathing_rate_status.append(self.breathing_rate_status_dict
                                             [i])

        return breathing_rate, breathing_rate_status

    def get_closest_breathing_rate(self, first, last):
        # closest - min(distance from first, distance from last)
        minus = None
        counter = first - 1
        while counter >= (counter - (256*20)):
            if counter in self.breathing_rate_dict:
                minus = counter
                break
            counter -= 1
        plus = None
        counter = last + 1
        while counter <= (counter + (256*20)):
            if counter in self.breathing_rate_dict:
                plus = counter
                break
            counter += 1

        if (minus and plus):
            if (first - minus) < (plus - last):
                return [self.breathing_rate_dict[minus]],\
                    [self.breathing_rate_status_dict[minus]]
            else:
                return [self.breathing_rate_dict[plus]],\
                    [self.breathing_rate_status_dict[plus]]
        else:
            return [self.breathing_rate_dict[minus]],\
                [self.breathing_rate_status_dict[minus]]

    def resp_classf(self):
        time.sleep(200)
        logging.info("resp_classf begin")
        ending_val = self.init_val
        while ending_val != -1:
            time.sleep(100)
            ending_val, window_insp, window_exp =\
                self.get_cur_window(ending_val)

            # end reached
            if ending_val == -1:
                break

            # set up which is first and which is second
            # set up upper bounds and lower bounds
            first, second = [], []
            firstbound, secondbound = None, None
            firstlow, secondlow = None, None
            if window_insp[0][0] < window_exp[0][0]:
                first, second = window_insp, window_exp
                firstbound, secondbound = self.up_thresh, self.down_thresh
                firstlow, secondlow = self.up_low, self. down_low
            else:
                first, second = window_exp, window_insp
                firstbound, secondbound = self.down_thresh, self.up_thresh
                firstlow, secondlow = self.down_low, self.up_low

            # make both of them to be of equal length
            if len(first) > len(second):
                first.pop()
            if len(second) > len(first):
                second.pop()

            # calculate the mean of this particular window
            mean = (sum([i[1] for i in first]) + sum([i[1]
                    for i in second]))/(len(first) + len(second))

            i = 0
            while i < len(first):
                valuefirst, valuesecond = first[i][1], second[i][1]

                # anomaly window of self.resp_classf_win_size
                anomaly_window = []

                # classifier
                if abs(valuefirst - mean) > firstbound and\
                        abs(valuesecond - mean) > secondbound:
                    # peaks and troughs are of above average size
                    j = i
                    # check if the trend continues
                    while j < min(len(first), i + self.resp_classf_win_size):
                        valfirst, valsecond = first[j][1], second[j][1]
                        if abs(valfirst - mean) > firstbound and\
                                abs(valsecond - mean) > secondbound:
                            anomaly_window.append(first[j][0])
                        else:
                            break
                        j += 1
                    # check if there are sufficient waves of the same type
                    if len(anomaly_window) == self.resp_classf_win_size:
                        begin, end = anomaly_window[0],\
                            anomaly_window[len(anomaly_window) - 1]
                        breathing_rate, breathing_rate_status = [], []
                        breathing_rate, breathing_rate_status =\
                            self.get_breathing_rate(begin, end)

                        if not (breathing_rate and breathing_rate_status):
                            breathing_rate, breathing_rate_status =\
                                self.get_closest_breathing_rate(begin, end)

                        mean_br = sum(breathing_rate)/len(breathing_rate)
                        logging.info("Above limits")
                        if mean_br > 20:
                            logging.info("possible Hyperventilation %s" %
                                         str(begin))
                            mean_br_status =\
                                sum(breathing_rate_status) / \
                                len(breathing_rate_status)
                            self.resp_anomaly_dict[begin] =\
                                (mean_br_status, 'possible Hyperventilation')
                            # Anomaly is detected
                            anomaly_dict = {}
                            anomaly_dict['Resp_hexo_timestamp'] = begin

                            anomaly_dict['BRstatus_mean'] = \
                                self.resp_anomaly_dict[begin][0]

                            anomaly_dict['Anomaly_type'] = \
                                self.resp_anomaly_dict[begin][1]

                            db.add_resp(anomaly_dict)
                            logging.info("%s" % str(anomaly_dict))
                            # if anomaly_window[0] in self.inspiration_dict:
                            #     plt.plot(anomaly_window,
                            #              [self.inspiration_dict[i]
                            #               for k in anomaly_window])
                            # else:
                            #     plt.plot(anomaly_window,
                            #              [self.expiration_dict[i]
                            #               for k in anomaly_window])
                        if mean_br < 10:
                            logging.info("possible Slow deep breathing %s" %
                                         str(begin))
                            mean_br_status =\
                                sum(breathing_rate_status) / \
                                len(breathing_rate_status)
                            self.resp_anomaly_dict[begin] =\
                                (mean_br_status,
                                 'possible Slow deep breathing')
                            # Anomaly is detected
                            anomaly_dict = {}
                            anomaly_dict['Resp_hexo_timestamp'] = begin

                            anomaly_dict['BRstatus_mean'] = \
                                self.resp_anomaly_dict[begin][0]

                            anomaly_dict['Anomaly_type'] = \
                                self.resp_anomaly_dict[begin][1]

                            db.add_resp(anomaly_dict)
                            logging.info("%s" % str(anomaly_dict))
                            # if anomaly_window[0] in self.inspiration_dict:
                            #     plt.plot(anomaly_window,
                            #              [self.inspiration_dict[i]
                            #               for k in anomaly_window])
                            # else:
                            #     plt.plot(anomaly_window,
                            #              [self.expiration_dict[i]
                            #               for k in anomaly_window])

                if abs(valuefirst - mean) < firstlow and\
                        abs(valuesecond - mean) < secondlow:
                    # peaks and troughs are of below average size
                    j = i
                    # check if the trend continues
                    while j < min(len(first), i + self.resp_classf_win_size):
                        valfirst, valsecond = first[j][1], second[j][1]
                        if abs(valfirst - mean) < firstlow and\
                                abs(valsecond - mean) < secondlow:
                            anomaly_window.append(first[j][0])
                        else:
                            break
                        j += 1
                    # check if there are sufficient waves of the same type
                    if len(anomaly_window) == self.resp_classf_win_size:
                        begin, end = anomaly_window[0],\
                            anomaly_window[len(anomaly_window) - 1]
                        breathing_rate, breathing_rate_status = [], []
                        breathing_rate, breathing_rate_status =\
                            self.get_breathing_rate(begin, end)

                        if not (breathing_rate and breathing_rate_status):
                            breathing_rate, breathing_rate_status =\
                                self.get_closest_breathing_rate(begin, end)

                        mean_br = sum(breathing_rate)/len(breathing_rate)
                        logging.info("Under limits")
                        if mean_br > 20:
                            logging.info("possible Tachypnea %s" % str(begin))
                            mean_br_status =\
                                sum(breathing_rate_status) / \
                                len(breathing_rate_status)
                            self.resp_anomaly_dict[begin] =\
                                (mean_br_status, 'possible Tachypnea')
                            # Anomaly is detected
                            anomaly_dict = {}
                            anomaly_dict['Resp_hexo_timestamp'] = begin

                            anomaly_dict['BRstatus_mean'] = \
                                self.resp_anomaly_dict[begin][0]

                            anomaly_dict['Anomaly_type'] = \
                                self.resp_anomaly_dict[begin][1]

                            db.add_resp(anomaly_dict)
                            logging.info("%s" % str(anomaly_dict))
                            # if anomaly_window[0] in self.inspiration_dict:
                            #     plt.plot(anomaly_window,
                            #              [self.inspiration_dict[i]
                            #               for k in anomaly_window])
                            # else:
                            #     plt.plot(anomaly_window,
                            #              [self.expiration_dict[i]
                            #               for k in anomaly_window])
                        if mean_br < 10:
                            logging.info("possible Hypoventilation %s" %
                                         str(begin))
                            mean_br_status =\
                                sum(breathing_rate_status) / \
                                len(breathing_rate_status)
                            self.resp_anomaly_dict[begin] =\
                                (mean_br_status, 'possible Hypoventilation')
                            # Anomaly is detected
                            anomaly_dict = {}
                            anomaly_dict['Resp_hexo_timestamp'] = begin

                            anomaly_dict['BRstatus_mean'] = \
                                self.resp_anomaly_dict[begin][0]

                            anomaly_dict['Anomaly_type'] = \
                                self.resp_anomaly_dict[begin][1]

                            db.add_resp(anomaly_dict)
                            logging.info("%s" % str(anomaly_dict))
                            # if anomaly_window[0] in self.inspiration_dict:
                            #     plt.plot(anomaly_window,
                            #              [self.inspiration_dict[i]
                            #               for k in anomaly_window])
                            # else:
                            #     plt.plot(anomaly_window,
                            #              [self.expiration_dict[i]
                            #               for k in anomaly_window])
                if (firstlow < abs(valuefirst - mean) < firstbound) and\
                        (secondlow < abs(valuesecond - mean) < secondbound):
                    # peaks and troughs are of regular size
                    j = i
                    # check if the trend continues
                    while j < min(len(first), i + self.resp_classf_win_size):
                        valfirst, valsecond = first[j][1], second[j][1]
                        if (firstlow < abs(valfirst - mean) < firstbound) and\
                                (secondlow < abs(valsecond - mean) <
                                 secondbound):
                            anomaly_window.append(first[j][0])
                        else:
                            break
                        j += 1
                    # check if there are sufficient waves of the same type
                    if len(anomaly_window) == self.resp_classf_win_size:
                        begin, end = anomaly_window[0],\
                            anomaly_window[len(anomaly_window) - 1]
                        breathing_rate, breathing_rate_status = [], []
                        breathing_rate, breathing_rate_status =\
                            self.get_breathing_rate(begin, end)

                        if not (breathing_rate and breathing_rate_status):
                            breathing_rate, breathing_rate_status =\
                                self.get_closest_breathing_rate(begin, end)

                        mean_br = sum(breathing_rate)/len(breathing_rate)
                        # print("Within limits")
                        if mean_br > 20:
                            logging.info("possible rapid breathing %s" %
                                         str(begin))
                            mean_br_status =\
                                sum(breathing_rate_status) / \
                                len(breathing_rate_status)
                            self.resp_anomaly_dict[begin] =\
                                (mean_br_status, 'possible rapid breathing')
                            # Anomaly is detected
                            anomaly_dict = {}
                            anomaly_dict['Resp_hexo_timestamp'] = begin

                            anomaly_dict['BRstatus_mean'] = \
                                self.resp_anomaly_dict[begin][0]

                            anomaly_dict['Anomaly_type'] = \
                                self.resp_anomaly_dict[begin][1]

                            db.add_resp(anomaly_dict)
                            logging.info("%s" % str(anomaly_dict))
                            # if anomaly_window[0] in self.inspiration_dict:
                            #     plt.plot(anomaly_window,
                            #              [self.inspiration_dict[i]
                            #               for k in anomaly_window])
                            # else:
                            #     plt.plot(anomaly_window,
                            #              [self.expiration_dict[i]
                            #               for k in anomaly_window])
                        if mean_br < 10:
                            logging.info("possible slow breathing %s" %
                                         str(begin))
                            mean_br_status =\
                                sum(breathing_rate_status) / \
                                len(breathing_rate_status)
                            self.resp_anomaly_dict[begin] =\
                                (mean_br_status, 'possible slow breathing')
                            # Anomaly is detected
                            anomaly_dict = {}
                            anomaly_dict['Resp_hexo_timestamp'] = begin

                            anomaly_dict['BRstatus_mean'] = \
                                self.resp_anomaly_dict[begin][0]

                            anomaly_dict['Anomaly_type'] = \
                                self.resp_anomaly_dict[begin][1]

                            db.add_resp(anomaly_dict)
                            logging.info("%s" % str(anomaly_dict))
                            # if anomaly_window[0] in self.inspiration_dict:
                            #     plt.plot(anomaly_window,
                            #              [self.inspiration_dict[i]
                            #               for k in anomaly_window])
                            # else:
                            #     plt.plot(anomaly_window,
                            #              [self.expiration_dict[i]
                            #               for k in anomaly_window])

                # if anomaly window is full, it means anomaly is detected
                if len(anomaly_window) == self.resp_classf_win_size:
                    i += self.resp_classf_win_size
                else:
                    i += 1

        # this call for show() is for plots in get_window()
        # plt.show()
        logging.info("resp_classf end")
        return

    # def populate_DS(self):
    def populate_DS(self, tidalv_dict, minv_dict, resp_dict, br_dict,
                    brq_dict, insp_dict, exp_dict):
        # with open('vt.txt', 'r') as f:
        #     testip = list(csv.reader(f, delimiter='\t'))
        #     for i in testip:
        #         self.tidal_volume_dict[int(float(i[0]))] = float(i[1])
        #     f.close()

        self.tidal_volume_dict.update(OrderedDict(tidalv_dict))

        # with open('minuteventilation.txt', 'r') as f:
        #     testip = list(csv.reader(f, delimiter='\t'))
        #     for i in testip:
        #         self.minute_ventilation_dict[int(float(i[0]))] = float(i[1])
        #     f.close()

        self.minute_ventilation_dict.update(OrderedDict(minv_dict))

        # with open('resp.txt', 'r') as f:
        #     testip = list(csv.reader(f, delimiter='\t'))
        #     for i in testip:
        #         self.raw_resp_dict[int(i[0])] = (int(i[1]), int(i[2]))
        #     f.close()

        self.raw_resp_dict.update(OrderedDict(resp_dict))

        # with open('breathingrate.txt', 'r') as f:
        #     testip = list(csv.reader(f, delimiter='\t'))
        #     for i in testip:
        #         self.breathing_rate_dict[int(i[0])] = int(i[1])
        #     f.close()

        self.breathing_rate_dict.update(OrderedDict(br_dict))

        # with open('br_quality.txt', 'r') as f:
        #     testip = list(csv.reader(f, delimiter='\t'))
        #     for i in testip:
        #         self.breathing_rate_status_dict[int(i[0])] = int(i[1])
        #     f.close()

        self.breathing_rate_status_dict.update(OrderedDict(brq_dict))

        # with open('inspiration.txt', 'r') as f:
        #     testip = list(csv.reader(f, delimiter='\t'))
        #     for i in testip:
        #         self.inspiration_dict[int(i[0])] = int(i[1])
        #     f.close()

        self.inspiration_dict.update(OrderedDict(insp_dict))

        # with open('expiration.txt', 'r') as f:
        #     testip = list(csv.reader(f, delimiter='\t'))
        #     for i in testip:
        #         self.expiration_dict[int(i[0])] = int(i[1])
        #     f.close()

        self.expiration_dict.update(OrderedDict(exp_dict))

        logging.info("len of inspdict %s" % str(len(self.inspiration_dict)))
        logging.info("len of expdict %s" % str(len(self.expiration_dict)))
        return


def main():
    config = ConfigParser.RawConfigParser()
    dirname = os.path.dirname(os.path.realpath(__file__))
    cfg_filename = os.path.join(dirname, 'anomaly_detector.cfg')
    config.read(cfg_filename)

    respObj = RespiratoryAD(config, 383021140185)

    th1 = Thread(target=respObj.populate_DS, args=[])
    th1.start()

    th1.join()

    th2 = Thread(target=respObj.tidal_volume_anomaly, args=[])
    th2.start()

    th3 = Thread(target=respObj.minute_ventilation_anomaly, args=[])
    th3.start()

    th4 = Thread(target=respObj.resp_variation, args=[])
    th4.start()

    th5 = Thread(target=respObj.resp_classf, args=[])
    th5.start()

    th6 = Thread(target=respObj.delete_DS, args=[])
    th6.start()

    # print(respObj.resp_anomaly_dict)


if __name__ == '__main__':
    main()
