#!/usr/bin/env python3
import json
import sys
import os
from pyDigitalWaveTools.vcd.parser import VcdParser
from optparse import OptionParser
# from analysis import *           
import logging
import time
import reader
import globals
logger = logging.getLogger(__name__)

def do_analysis(options):
    start = time.time()
    data = reader.readVCDFile(options.filename)
    now = time.time()
    logger.info("parsing VCD took %.2f sec"%(now-start))
    start = now
    path = os.path.abspath(os.path.dirname(sys.argv[0]))
    print (path)
    if options.mode=="ncore":
        globals.design_info = reader.readJSONInfoFile(path + "/../../test/ncore_stats.json")
        if options.design_info:
            globals.stats = reader.readJSONInfoFile(options.design_info)
            now = time.time()
            logger.info("reading JSON took %.2f sec"%(now-start))
            start = now
        reader.addNcoreSignals(data, "")
    else:
        globals.stats = reader.readJSONInfoFile(path + "/../../test/codacache_stats.json")
        print (globals.stats)
        reader.addCCSignals(data,"")
    now = time.time()
    logger.info("generating summary took %.2f sec"%(now-start))
    start = now
    if options.outputfile:
        with open(options.outputfile, "w") as out_file : print(json.dumps(globals.result, indent=4, sort_keys=True), file=out_file)
        now = time.time()
        logger.info("writing JSON output took %.2f sec"%(now-start))
        start = now
    
if __name__== "__main__":    
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      help="read VCD file <filename>", metavar="FILE")
    parser.add_option("-i", "--DesignInfo", dest="design_info",
                      help="read JSON file <filename> for additional information about design", metavar="FILE")
    parser.add_option("-o", "--outputfile", dest="outputfile",
                      help="output to JSON file <filename>", metavar="FILE")
    parser.add_option("--Stats", dest="stat_info", default="test/ncore_stats.json",
                      help="read JSON file <filename> for statistics", metavar="FILE")
    parser.add_option("-m", "--Mode", dest="mode", default="ncore",
                      help="mode for interpreting VCD [codacache|ncore|flexnoc]", metavar="")
    parser.add_option("-d", "--debug", action="store_true", dest="debug", 
                      help="enable debugging output", metavar="")
    (options, args)  = parser.parse_args()
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG if options.debug  else logging.INFO)
    do_analysis(options)
