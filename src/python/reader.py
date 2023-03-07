import json
import sys
from pyDigitalWaveTools.vcd.parser import VcdParser
import logging
import time
import globals
import os.path as path           # This one is needed for file handling, (Trace,Protocol spec,etc files)

logger = logging.getLogger(__name__)

def addCCSignals(data, scope):
    if 'children' in data:
        for value in data['children']:
            if value['type']['name']=='struct':
                logger.debug("hierachy: %s "%value["name"])
                addCCSignals(value, scope + "/" + value["name"] )
            if value['type']['name']=='wire':
                if len(value['data'])>1:
                    res = []
                    hist = {}
                    startTime = 0
                    val = currentTime = weightedSum = 0
                    min_value = max_value = avg = -1
                    stat_type = "unknown"
                    unit_name = scope.split('/')[-1]
                    container_name = scope.split('/')[-2]
                    stat_name = value['name'].split('(')[0]
                    stat_type = globals.stats['AIU'][stat_name]

                    for i in value['data']:
                        previousVal = val
                        previousTime = currentTime
                        currentTime = i[0]
                        if i[1][0]=='b':
                            val = int(i[1][1:], 2)
                        elif i[1][0]=='h':
                            val = int(i[1][1:], 16)
                        else:
                            val = int(i[1], 2)
                        weightedSum += (currentTime-previousTime)*previousVal
                        if stat_type == "level":
                            if previousVal in hist:
                                hist[previousVal] += (currentTime-previousTime)
                            else:
                                hist[previousVal] = (currentTime-previousTime)
                        res.append(val)
                    logger.debug("scope %s value %s res %s"%(scope, value['name'], res))
                    avg = weightedSum/(int(value['data'][-1][0])-int(value['data'][0][0]))
                    min_value = min(res)
                    max_value = max(res)

                    res = {}
                    res['scope'] = scope
                    res['name'] = value['name']
                    res['type'] = stat_type
                    res['unit_type'] = "auis"
                    res['transitions'] = len(value['data'])
                    res['min'] = min_value
                    res['average'] = avg
                    res['max'] = max_value
                    res['first_time'] = value['data'][0][0]
                    res['last_time'] = value['data'][-1][0]
                    res['histogram'] = hist
                    if unit_name not in globals.result:
                        globals.result[unit_name] = [] 
                    globals.result[unit_name].append(res)
                    logger.debug("    %s %s %s %s %s %s %s %s %s %s %s", scope, value['name'], stat_name, stat_type, value['type']['width'], len(value['data']), min_value, avg, max_value, value['data'][0][0], value['data'][-1][0])

def addNcoreSignals(data, scope):
    if 'children' in data:
        for value in data['children']:
            if value['type']['name']=='struct':
                logger.debug("hierachy: %s "%value["name"])
                addNcoreSignals(value, scope + "/" + value["name"] )
            if value['type']['name']=='wire':
                if len(value['data'])>1:
                    res = []
                    hist = {}
                    startTime = 0
                    legato = False
                    unit_type = "unknown"
                    val = currentTime = weightedSum = 0
                    min_value = max_value = avg = -1
                    unit_name = scope.split('/')[-1]
                    container_name = scope.split('/')[-2]
                    stat_name = value['name'].split('(')[0]
                    stat_type = "unknown"

                    if unit_name=="aui_core":
                        unit_name = container_name
                    if container_name=="ndn1" :
                        legato = True
                    if container_name=="dn" :
                        legato = True
                    if container_name=="ndn2" :
                        legato = True
                    if container_name=="ndn3" :
                        legato = True
                    if legato:
                        unit_type = container_name
                    else:    
                        if 'interfaces' in globals.design_info:
                            for name in globals.design_info['interfaces']:
                                if name['agent'] == unit_name:
                                    if name['agent']!=name['unit']:
                                        stat_name = stat_name.rstrip("_0123456789")
                                    type = name['type']
                                    direction = name['direction']

                                    if direction =="in" and type == "AXI4":
                                        logger.debug("found IOAIU in designinfo ")
                                        stat_type = globals.stats['IOAIU'][stat_name]
                                        unit_type = "IOAIU"
                                    if direction =="out" and type == "AXI4":
                                        logger.debug("found DMI in designinfo ")
                                        stat_type = globals.stats['DMI'][stat_name]
                                        unit_type = "DMI"

                                    if direction =="in" and type == "CHI":
                                        logger.debug("found CAIU in designinfo ")
                                        stat_type = globals.stats['CAIU'][stat_name]
                                        unit_type = "CAIU"
                                        
                    for i in value['data']:
                        previousVal = val
                        previousTime = currentTime
                        currentTime = i[0]
                        if i[1][0]=='b':
                            val = int(i[1][1:], 2)
                        elif i[1][0]=='h':
                            val = int(i[1][1:], 16)
                        else:
                            val = int(i[1], 2)
                        weightedSum += (currentTime-previousTime)*previousVal
                        if stat_type == "level":
                            if previousVal in hist:
                                hist[previousVal] += (currentTime-previousTime)
                            else:
                                hist[previousVal] = (currentTime-previousTime)
                        res.append(val)
                    # print(scope, value['name'], res)
                    avg = weightedSum/(int(value['data'][-1][0])-int(value['data'][0][0]))
                    min_value = min(res)
                    max_value = max(res)

                    res = {}
                    res['scope'] = scope
                    res['name'] = value['name']
                    res['type'] = stat_type
                    res['unit_type'] = unit_type
                    res['transitions'] = len(value['data'])
                    res['min'] = min_value
                    res['average'] = avg
                    res['max'] = max_value
                    res['first_time'] = value['data'][0][0]
                    res['last_time'] = value['data'][-1][0]
                    res['histogram'] = hist
                    if legato:
                        if container_name in globals.result:
                            if unit_name in globals.result[container_name]:
                                globals.result[container_name][unit_name].append(res)
                            else:
                                globals.result[container_name][unit_name] = [] 
                        else: 
                            globals.result[container_name] = {}
                            globals.result[container_name][unit_name] = [] 
                            globals.result[container_name][unit_name].append(res)
                    else:
                        if unit_name not in globals.result:
                            globals.result[unit_name] = [] 
                        globals.result[unit_name].append(res)
                    logger.debug("    %s %s %s %s %s %s %s %s %s %s %s", scope, value['name'], stat_name, stat_type, value['type']['width'], len(value['data']), min_value, avg, max_value, value['data'][0][0], value['data'][-1][0])

def readVCDFile(filename):
    with open(filename) as vcd_file:
        vcd = VcdParser()
        vcd.parse(vcd_file)
        data = vcd.scope.toJson()
        return data

def readJSONInfoFile(filename):
    if path.exists(filename):
        with open(filename,"r") as read_file: JSonData = json.load(read_file)
        logger.info('JSON File in use: %s' %(filename))
        return JSonData
    else:
        logger.error('User Error: JSON file %s doesn\'t exist??'%filename)
        sys.exit(0)

