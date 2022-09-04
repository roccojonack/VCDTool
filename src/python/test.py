#!/usr/bin/env python3
import json
import sys
from pyDigitalWaveTools.vcd.parser import VcdParser
from pprint import pprint
if len(sys.argv) > 1:
    fname = sys.argv[1]
else:
    print('Give me a vcd file to parse')
    sys.exit(-1)

with open(fname) as vcd_file:
    vcd = VcdParser()
    vcd.parse(vcd_file)
    # pprint(vcd)vcd_dumpvars()
    print(vcd.scope.name)
    data = vcd.scope.toJson()
    # print(json.dumps(data, indent=4, sort_keys=True))
    