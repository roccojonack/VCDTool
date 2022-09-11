#!/usr/bin/env python3
import json
import sys
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
    if options.design_info:
        globals.ncore_stats = reader.readJSONInfoFile(options.ncore_stat_info)
        globals.design_info = reader.readJSONInfoFile(options.design_info)
        now = time.time()
        logger.info("reading JSON took %.2f sec"%(now-start))
        start = now
    reader.addSignals(data, "")
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
    parser.add_option("--NcoreStats", dest="ncore_stat_info", default="test/ncore_stats.json",
                      help="read JSON file <filename> for Ncore statistics", metavar="FILE")
    parser.add_option("-d", "--debug", action="store_true", dest="debug", 
                      help="enable debugging output", metavar="")
    (options, args)  = parser.parse_args()
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG if options.debug  else logging.INFO)
    do_analysis(options)
