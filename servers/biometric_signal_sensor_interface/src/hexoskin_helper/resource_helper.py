from __future__ import absolute_import, division, print_function
from threading import Thread
import sys
import time
import requests
import ConfigParser
import calendar
import logging
import utility_helper as util
import pandas as pd
import numpy as np
import anomaly_database_helper as db
sys.path.insert(0, '../anomaly_detector')
import respiration_AD as respiration

requests.packages.urllib3.disable_warnings()

# Logging Config
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

__author__ = 'abhijith'

'''
biometric resourceHelper provides all methods that retrieves the biometric
data. This helper module is called by the Tango server module providing a
clear line of abstraction.
'''


def get_record_list(auth, limit="100", user='', deviceFilter=''):
    '''
    Each astronaut session with the hexoskin is a record. Record starts when
    he plugs the device to his shirt, and stops when the device is plugged
    into the system when the astronaut returns to the station.

    Returns the results records corresponding to the selected filters
        @param auth:            The authentication token to use for the call
        @param limit:           The limit of results to return. Passing 0
                                returns all the records
        @param userFilter:      The ID of the user to look for
        @param deviceFilter:    The device ID to look for. Takes the form
                                HXSKIN12XXXXXXXX, where XXXXXXXX is the
                                0-padded serial number.
                                Example : HXSKIN1200001234
        @return :               The record list
    '''
    filters = dict()
    if limit != "100":
        filters['limit'] = limit
    if user != '':
        filters['user'] = user
    if deviceFilter != '':
        filters['device'] = deviceFilter
    out = auth.api.record.list(filters)
    return out.response.result['objects']


def get_active_record_list(auth, limit="100", user='', deviceFilter=''):
    '''
    Returns the results records that are measuring in realtime corresponding
    to the selected filters
        @param auth:            The authentication token to use for the call
        @param limit:           The limit of results to return. Passing 0
                                returns all the records
        @param userFilter:      The ID of the user to look for
        @param deviceFilter:    The device ID to look for. Takes the form
                                HXSKIN12XXXXXXXX, where XXXXXXXX is the
                                0-padded serial number.
                                Example : HXSKIN1200001234
        @return :               The realtime measuring record list
    '''
    recordList = get_record_list(auth, limit, user, deviceFilter)
    response = []

    for record in recordList:
        if(record['status'] == "realtime"):
            response.append(record['id'])

    return response


def get_data(auth, recordID, start='', end='', datatypes='',
             downloadRaw=True):
    """
    This function fetches the specified data range. Called by getRangeData
    and getRecordData
        @param auth:        The authentication token to use for the call
        @param recordID:    Record ID of record
        @param start:       Start timestamp for data to be fetched
        @param end:         End timestamp for data to be fetched
        @param datatypes:   Datatypes to be fetched
                            If not passed, all raw_datatypes (based on next
                            param value) and other datatypes downloaded
        @param downloadRaw: Flag to fetch raw-datatypes also
        @return :           returns a dictionary containing all datatypes
                            in separate entries
    """
    record = auth.api.record.get(recordID)
    if start == '':
        start = record.start
    if end == '':
        end = record.end

    final_dat = {}
    if datatypes != '':
        for dataID in datatypes:
            raw_flag = 0
            d_items = util.datatypes.items()
            key = [d_key for d_key, value in d_items if value == [
                dataID]]
            if not key:
                d_items = util.raw_datatypes.items()
                key = [d_key for d_key, value in d_items if value == [dataID]]
                raw_flag = 1
            logging.info("Downloading " + key[0])
            if raw_flag:
                data = get_unsubsampled_data_helper(
                    auth=auth, userID=record.user, start=start, end=end,
                    dataID=util.raw_datatypes[key[0]])
            else:
                data = get_unsubsampled_data_helper(
                    auth=auth, userID=record.user, start=start, end=end,
                    dataID=util.datatypes[key[0]])
            final_dat[dataID] = data
    else:
        if downloadRaw is True:
            for rawID in util.raw_datatypes:
                logging.info("Downloading" + rawID)
                raw_dat = get_unsubsampled_data_helper(
                    auth=auth, userID=record.user, start=record.start,
                    end=record.end, dataID=util.raw_datatypes[rawID])
                final_dat[rawID] = raw_dat
        for dataID in util.datatypes:
            logging.info("Downloading " + dataID)
            data = get_unsubsampled_data_helper(
                auth=auth, userID=record.user, start=record.start,
                end=record.end, dataID=util.datatypes[dataID])
            final_dat[dataID] = data
    logging.info(final_dat)
    return final_dat


def get_unsubsampled_data_helper(auth, userID, start, end, dataID):
    """
    All data comes in subsampled form if the number of samples
    exceeds 65535. If this is the case, fetch data
    page by page to prevent getting subsampled data.
        @param auth:        The authentication token to use for the call
        @param userID:      userID ID of record
        @param start:       Start timestamp for data to be fetched
        @param end:         End timestamp for data to be fetched
        @param datatypes:   Datatypes to be fetched
        @return :           returns a dictionary containing all datatypes
                            in separate entries
    """
    out = []
    # Number of ticks between each sample
    datSampRate = util.dataSampleRate[dataID[0]]
    if datSampRate != []:
        # Number of ticks max size not to overflow 65535 max size
        sampPerIter = 65535 * datSampRate
        a = start
        b = min(end, a + sampPerIter)
        while a < end:
            dat = auth.api.data.list(
                start=a, end=b, user=userID, datatype=dataID)
            try:
                if len(dat.response.result[0]['data'].values()[0]) > 0:
                    ts = zip(*dat.response.result[0][u'data'].values()[0])[0]
                    data = [zip(*dat.response.result[0][u'data'][str(v)])[1]
                            for v in dataID]
                    out.extend(zip(ts, *data))
            except:
                out.extend(zip([], []))

            a = min(a + sampPerIter, end)
            b = min(b + sampPerIter, end)
            # Rate limiting to stay below 5 requests per second
            time.sleep(1)
    else:
        dat = auth.api.data.list(start=start, end=end,
                                 user=userID, datatype=dataID)
        if dat.response.result != []:
            out.extend(dat.response.result[0]['data'][str(dataID[0])])
    out = util.convertTimestamps(out, util.TIMESTAMP)
    return out


def get_realtime_data_helper(auth, user, start, end, datatypes):
    """
    This function fetches the specified data range. Called by
    realtime_data_generator() page by page to prevent getting subsampled data.
        @param auth:        The authentication token to use for the call
        @param userID:      userID ID of record
        @param start:       Start timestamp for data to be fetched
        @param end:         End timestamp for data to be fetched
        @param datatypes:   Datatypes to be fetched
        @return :           returns a dictionary containing all datatypes in
                            separate entries
    """
    final_dat = {}

    for dataID in datatypes:
        raw_flag = 0
        key = [d_key for d_key, value in util.datatypes.items() if value == [
            dataID]]
        if not key:
            data_items = util.raw_datatypes.items()
            key = [d_key for d_key, value in data_items if value == [dataID]]
            raw_flag = 1

        if raw_flag:
            data = get_unsubsampled_data_helper(
                auth=auth, userID=user, start=start, end=end,
                dataID=util.raw_datatypes[key[0]])
        else:
            data = get_unsubsampled_data_helper(
                auth=auth, userID=user, start=start, end=end,
                dataID=util.datatypes[key[0]])
        final_dat[dataID] = data
    return final_dat


def realtime_data_generator(auth, recordID, datatypes):
    '''
    A generator function that yields the realtime data to get_realtime_data()
        @param auth:        The authentication token to use for the call
        @param recordID:    recordID ID of record
        @param datatypes:   Datatypes to be fetched
        @return :           returns a dictionary containing all datatypes in
                            separate entries
    '''
    record = auth.api.record.get(recordID)

    start_epoch = calendar.timegm(time.gmtime())
    start_epoch = start_epoch - (20)
    start = (start_epoch) * 256

    end = (calendar.timegm(time.gmtime()) - 10) * 256

    while True:
        user = record.user
        data = get_realtime_data_helper(auth, user, start, end, datatypes)
        record = auth.api.record.get(recordID)
        start = end
        end = (calendar.timegm(time.gmtime()) - 10) * 256
        time.sleep(6)
        yield data

    return


def get_all_data(auth, recordID, datatypes):
    '''
    Param: auth token, record ID of the record/session and the datatype of the
    metric that needs to be measured.

    Realtime data collector for all datatypes passed. Called by the Tango
    server.

    This function fetches the specified data range.
        @param auth:        The authentication token to use for the call
        @param recordID:    recordID ID of record
        @param datatypes:   Datatypes to be fetched
        @return :           Runs till the record is active and returns the
                            data of the user regularly, adding to the record.
                            -1, if data not being collected in realtime
    '''
    record = auth.api.record.get(recordID)
    user = record.user
    start_epoch = calendar.timegm(time.gmtime())
    start_epoch = start_epoch - (10)
    start = (start_epoch) * 256
    end = (calendar.timegm(time.gmtime()) - 5) * 256

    data = get_realtime_data_helper(auth, user, start, end, datatypes)

    return data


def AF_realtime(auth, recordID, func, window_size='64', datatypes=''):
    '''
    Param: auth token, record ID of the record/session and the datatype of the
    metric that needs to be measured.

    Realtime data collector for Atrial Fribillation

    This function fetches the specified data range.
        @param auth:        The authentication token to use for the call
        @param recordID:    recordID ID of record
        @param datatypes:   Datatypes to be fetched
        @return :           Runs till the record is active and returns the
                            data of the user regularly, adding to the record.
                            -1, if data not being collected in realtime
    '''
    record = auth.api.record.get(recordID)
    if record.status != 'realtime':
        logging.warning(
            "No realtime data available with this record. Already docked.")
        return -1

    exitCounter = 5

    rr_timestamp = []
    rr_values = []
    hrq_timestamp = []
    hrq_values = []

    for data in realtime_data_generator(auth, recordID, datatypes):
        # For debugging
        logging.debug(len(data), "AF")
        if len(data[datatypes[0]]) == 0:
            exitCounter = exitCounter - 1
            if exitCounter == 0:
                break
        else:
            exitCounter = 5
            for a in data[datatypes[0]]:
                if a[1] is not None:
                    rr_timestamp.append(a[0])
                    rr_values.append(a[1])
                    db.add_data(a[0], a[1], datatypes[0])

            for a in data[datatypes[1]]:
                if a[1] is not None:
                    hrq_timestamp.append(a[0])
                    hrq_values.append(a[1])
                    db.add_data(a[0], a[1], datatypes[1])

            logging.info("Added raw data to db")

            logging.debug("Collected {} data points".format(len(rr_timestamp)))
            if (len(rr_timestamp) >= window_size and
                    len(hrq_timestamp) >= window_size):
                # Pandas Dataframe
                rr_df = pd.DataFrame(np.column_stack([rr_timestamp,
                                                      rr_values]))
                hrq_df = pd.DataFrame(np.column_stack([hrq_timestamp,
                                                       hrq_values]))
                rr_timestamp = []
                rr_values = []
                hrq_timestamp = []
                hrq_values = []

                start = int(len(rr_df) / 64)
                end = int(len(rr_df) / 64) + 64
                rr_df = rr_df[start:end]
                rr_df.reset_index(drop=True, inplace=True)
                # Call anomaly detection endpoint here
                rr_df.columns = ["hexoskin_timestamps", "rr_int"]
                hrq_df.columns = ["hexoskin_timestamps", "quality_ind"]

                anomaly = func(rr_df, hrq_df[0:64])
                if anomaly == -1:
                    print("No Anomaly")
                if anomaly != -1:
                    db.add_af(anomaly)

    return


def VT_realtime(auth, recordID, VTBD, datatypes=''):
    '''
    Param: auth token, record ID of the record/session and the datatype of the
    metric that needs to be measured.


    This function fetches the specified data range.
        @param auth:        The authentication token to use for the call
        @param recordID:    recordID ID of record
        @param datatypes:   Datatypes to be fetched
        @return :           Runs till the record is active and returns the
                            data of the user regularly, adding to the record.
                            -1, if data not being collected in realtime
    '''
    record = auth.api.record.get(recordID)
    if record.status != 'realtime':
        logging.warning(
            "No realtime data available with this record. Already docked.")
        return -1

    exitCounter = 5

    ecg_timestamp = []
    ecg_values = []
    rr_timestamp = []
    rr_values = []
    rrs_timestamp = []
    rrs_values = []
    hr_timestamp = []
    hr_values = []
    hrq_timestamp = []
    hrq_values = []

    beat_analyze_flag = 0

    for data in realtime_data_generator(auth, recordID, datatypes):
        logging.debug(len(data))
        if len(data[datatypes[0]]) == 0:
            exitCounter = exitCounter - 1
            if exitCounter == 0:
                break
        else:
            exitCounter = 5
            skipFlag = 0
            for a in data[datatypes[0]]:
                if a[1] is not None:
                    ecg_timestamp.append(int(a[0]))
                    ecg_values.append(int(a[1]))
                    if skipFlag % 300 == 0:
                        db.add_data(int(a[0]), int(a[1]), datatypes[0])
                    skipFlag += 1

            for a in data[datatypes[1]]:
                if a[1] is not None:
                    rr_timestamp.append(int(a[0]))
                    rr_values.append(float(a[1]))

            for a in data[datatypes[2]]:
                if a[1] is not None:
                    rrs_timestamp.append(int(a[0]))
                    rrs_values.append(int(a[1]))

            skipFlag = 0
            for a in data[datatypes[3]]:
                if a[1] is not None:
                    hr_timestamp.append(int(a[0]))
                    hr_values.append(float(a[1]))
                    db.add_data(int(a[0]), float(a[1]), datatypes[3])

            for a in data[datatypes[4]]:
                if a[1] is not None:
                    hrq_timestamp.append(int(a[0]))
                    hrq_values.append(int(a[1]))

            logging.info("Added raw data to db")
            ecg_dict = dict(zip(ecg_timestamp, ecg_values))

            rr_dict = {}
            for _time, rr, rrs in zip(rrs_timestamp, rr_values, rrs_values):
                rr_dict[_time] = (rr, rrs)

            hr_dict = {}
            for _time, hr, hrq in zip(hr_timestamp, hr_values, hrq_values):
                hr_dict[_time] = (hr, hrq)

            beat_analyze_timestamp = rr_timestamp[0]

            ecg_timestamp = []
            ecg_values = []
            rr_timestamp = []
            rr_values = []
            rrs_timestamp = []
            rrs_values = []
            hr_timestamp = []
            hr_values = []
            hrq_timestamp = []
            hrq_values = []

            try:
                # th1 = Thread(target=VTBD.collect_data, args=[
                #              ecg_dict, rr_dict, hr_dict])
                # th1.start()
                VTBD.collect_data(ecg_dict, rr_dict, hr_dict)

                if beat_analyze_flag == 0:
                    th2 = Thread(target=VTBD.beat_analyze,
                                 args=[beat_analyze_timestamp])
                    th2.start()
                    beat_analyze_flag = 1

            except:
                continue
    return


def APC_PVC_realtime(auth, recordID, obj, datatypes=''):
    '''
    Param: auth token, record ID of the record/session and the datatype of the
    metric that needs to be measured.


    This function fetches the specified data range.
        @param auth:        The authentication token to use for the call
        @param recordID:    recordID ID of record
        @param datatypes:   Datatypes to be fetched
        @return :           Runs till the record is active and returns the
                            data of the user regularly, adding to the record.
                            -1, if data not being collected in realtime
    '''
    record = auth.api.record.get(recordID)
    if record.status != 'realtime':
        logging.warning(
            "No realtime data available with this record. Already docked.")
        return -1

    exitCounter = 5

    ecg_timestamp = []
    ecg_values = []
    rrs_timestamp = []
    rrs_values = []

    first_analyze_flag = 0

    for data in realtime_data_generator(auth, recordID, datatypes):
        logging.debug(len(data[4113]), len(data[1004]))

        if len(data[datatypes[0]]) == 0:
            exitCounter = exitCounter - 1
            if exitCounter == 0:
                break
        else:
            exitCounter = 5
            for a in data[datatypes[0]]:
                if a[1] is not None:
                    ecg_timestamp.append(int(a[0]))
                    ecg_values.append(int(a[1]))

            for a in data[datatypes[1]]:
                if a[1] is not None:
                    rrs_timestamp.append(int(a[0]))
                    rrs_values.append(int(a[1]))

            ecg_dict = dict(zip(ecg_timestamp, ecg_values))
            rrs_dict = dict(zip(rrs_timestamp, rrs_values))

            try:
                first_analyze_timestamp = rrs_timestamp[0]
            except:
                continue

            ecg_timestamp = []
            ecg_values = []
            rrs_timestamp = []
            rrs_values = []

            try:
                # th1 = Thread(target=VTBD.collect_data, args=[
                #              ecg_dict, rr_dict, hr_dict])
                # th1.start()
                obj[0].populate_DS(ecg_dict, rrs_dict)

                obj[1].populate_data(ecg_dict, rrs_dict)

                if first_analyze_flag == 0:
                    print("Starting APC_PVC and PVC_Hamilton")
                    time.sleep(5)
                    th2 = Thread(target=obj[0].popluate_aux_structures,
                                 args=[first_analyze_timestamp])
                    th2.start()

                    th4 = Thread(target=obj[1].beat_classf_analyzer,
                                 args=[first_analyze_timestamp])
                    th4.start()

                    th3 = Thread(
                        target=obj[0].apcObj.absolute_arrhythmia,
                        args=[])
                    th3.start()

                    first_analyze_flag = 1

            except Exception as e:
                print(e)
                continue
    return


def resp_realtime(auth, recordID, obj, datatypes=''):
    '''
    Param: auth token, record ID of the record/session and the datatype of the
    metric that needs to be measured.


    This function fetches the specified data range.
        @param auth:        The authentication token to use for the call
        @param recordID:    recordID ID of record
        @param datatypes:   Datatypes to be fetched
        @return :           Runs till the record is active and returns the
                            data of the user regularly, adding to the record.
                            -1, if data not being collected in realtime
    '''
    record = auth.api.record.get(recordID)
    if record.status != 'realtime':
        logging.warning(
            "No realtime data available with this record. Already docked.")
        return -1

    exitCounter = 5

    tidal_v_timestamp = []
    tidal_v_values = []
    minv_timestamp = []
    minv_values = []
    resp_timestamp = []
    resp_values = []
    br_timestamp = []
    br_values = []
    brq_timestamp = []
    brq_values = []
    insp_timestamp = []
    insp_values = []
    exp_timestamp = []
    exp_values = []

    config = ConfigParser.RawConfigParser()
    config.read('../anomaly_detector/anomaly_detector.cfg')

    first_analyze_flag = 0

    for data in realtime_data_generator(auth, recordID, datatypes):
        logging.debug(len(data[4129]), len(data[35]))
        if len(data[datatypes[0]]) == 0:
            exitCounter = exitCounter - 1
            if exitCounter == 0:
                break
        else:
            exitCounter = 5
            for a in data[datatypes[0]]:
                if a[1] is not None:
                    tidal_v_timestamp.append(int(a[0]))
                    tidal_v_values.append(int(a[1]))
                    db.add_data(int(a[0]), int(a[1]), datatypes[0])

            for a in data[datatypes[1]]:
                if a[1] is not None:
                    minv_timestamp.append(int(a[0]))
                    minv_values.append(int(a[1]))
                    db.add_data(int(a[0]), int(a[1]), datatypes[1])

            skipFlag = 0
            for a in data[datatypes[2]]:
                if a[1] is not None:
                    resp_timestamp.append(int(a[0]))
                    resp_values.append(int(a[1]))
                    if skipFlag % 100 == 0:
                        db.add_data(int(a[0]), int(a[1]), datatypes[2])
                    skipFlag += 1

            for a in data[datatypes[3]]:
                if a[1] is not None:
                    br_timestamp.append(int(a[0]))
                    br_values.append(int(a[1]))

            for a in data[datatypes[4]]:
                if a[1] is not None:
                    brq_timestamp.append(int(a[0]))
                    brq_values.append(int(a[1]))

            for a in data[datatypes[5]]:
                if a[1] is not None:
                    insp_timestamp.append(int(a[0]))
                    insp_values.append(int(a[1]))
                    db.add_data(int(a[0]), int(a[1]), datatypes[5])

            for a in data[datatypes[6]]:
                if a[1] is not None:
                    exp_timestamp.append(int(a[0]))
                    exp_values.append(int(a[1]))
                    db.add_data(int(a[0]), int(a[1]), datatypes[6])

            tidalv_dict = dict(zip(tidal_v_timestamp, tidal_v_values))
            minv_dict = dict(zip(minv_timestamp, minv_values))
            resp_dict = dict(zip(resp_timestamp, resp_values))
            br_dict = dict(zip(br_timestamp, br_values))
            brq_dict = dict(zip(brq_timestamp, brq_values))
            insp_dict = dict(zip(insp_timestamp, insp_values))
            exp_dict = dict(zip(exp_timestamp, exp_values))

            try:
                # first_analyze_timestamp = tidal_v_timestamp[0]
                first_analyze_timestamp = resp_timestamp[0]
            except:
                continue

            tidal_v_timestamp = []
            tidal_v_values = []
            minv_timestamp = []
            minv_values = []
            resp_timestamp = []
            resp_values = []
            br_timestamp = []
            br_values = []
            brq_timestamp = []
            brq_values = []
            insp_timestamp = []
            insp_values = []
            exp_timestamp = []
            exp_values = []

            if not first_analyze_flag:
                respObj = respiration.RespiratoryAD(config,
                                                    first_analyze_timestamp)

            respObj.populate_DS(tidalv_dict, minv_dict, resp_dict, br_dict,
                                brq_dict, insp_dict, exp_dict)

            try:
                if first_analyze_flag == 0:
                    print("Starting Respiration AD")

                    th2 = Thread(target=respObj.tidal_volume_anomaly, args=[])
                    th2.start()

                    th3 = Thread(target=respObj.minute_ventilation_anomaly,
                                 args=[])
                    th3.start()

                    th4 = Thread(target=respObj.resp_variation, args=[])
                    th4.start()

                    th5 = Thread(target=respObj.resp_classf, args=[])
                    th5.start()

                    th6 = Thread(target=respObj.delete_DS, args=[])
                    th6.start()

                    first_analyze_flag = 1

            except Exception as e:
                print(e)
                continue
    return


def sleep_ad(auth, recordID):
    '''
    Param: auth token, record ID of the record/session and the datatype of the
    metric that needs to be measured.


    This function fetches the specified data range.
        @param auth:        The authentication token to use for the call
        @param recordID:    recordID ID of record
        @param datatypes:   Datatypes to be fetched
        @return :           Runs till the record is active and returns the
                            data of the user regularly, adding to the record.
                            -1, if data not being collected in realtime
    '''

    sleepphase_file = open("../anomaly_detector/sleepphase.txt", "w")
    sleeppos_file = open("../anomaly_detector/sleepposition.txt", "w")

    try:

        data = auth.api.data.list(record=recordID, datatype=[270, 280])
        sleepphase = data.response.result[0]['data'][str(280)]
        sleeppos = data.response.result[0]['data'][str(270)]

        for a in sleepphase:
            if a[1] is None:
                sleepphase_file.write(str(int(a[0])) + ",null\n")
            else:
                sleepphase_file.write(str(int(a[0])) + "," + str(a[1]) + "\n")

        for a in sleeppos:
            if a[1] is None:
                sleeppos_file.write(str(int(a[0])) + ",null\n")
            else:
                sleeppos_file.write(str(int(a[0])) + "," + str(a[1]) + "\n")

        sleepphase_file.close()
        sleeppos_file.close()
    except:
        pass

    return


def main(argv):
    '''
    Main Function
    '''
    pass


if __name__ == "__main__":
    main(sys.argv)
