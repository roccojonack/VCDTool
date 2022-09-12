#!/usr/bin/env python3
##
# -*- coding: utf-8 -*-
from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.graph_objs as go
import glob
import csv
import sys
import re
import os
import time
import json
from optparse import OptionParser
# from datetime import datetime

def parse_csv(filename):
    result = []
    prog = re.compile(r'^lgto_.*')
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if len(result) == 0:
                for cell in row:
                    result.append([cell])
            else:
                for idx, cell in enumerate(row):
                    if len(cell) == 0:
                        result[idx].append(0)
                    else:
                        result[idx].append(cell)
    return result    

def parse_tsv(filename):
    result = {}
    with open(filename) as tsv_file:
        for line in tsv_file:
            columns = line.split("\t")
            for index, i in enumerate(columns):
                vals = i.split(":")
                if len(vals)>1:
                    print(index, vals[0], vals[1])
                    if vals[0] == "name":
                        namevals = vals[1].split(".")
                        if len(namevals) > 4:
                            name = '.'.join(namevals[7:-1])
                            signal = namevals[-1]
                            # print(i, name, signal)
                        if name not in result:
                            result[name] = {}
                        if signal not in result[name]:
                            result[name][signal] = {}
                    else:
                        if vals[0] == "histogram":
                            histvals = vals[1].split(";")
                            result[name][signal][vals[0]] = {}
                            for j in histvals:
                                tmp = j.split("/")
                                if len(tmp)==2:
                                    result[name][signal][vals[0]][tmp[0]] = tmp[1]
                        else:
                            result[name][signal][vals[0]] = vals[1]
    return result    
    
def readJSONInfoFile(filename):
    if os.path.exists(filename):
        with open(filename,"r") as read_file: JSonData = json.load(read_file)
        #logger.info('JSON File in use: %s' %(filename))
        return JSonData
    else:
        #logger.error('User Error: JSON file %s doesn\'t exist??'%filename)
        sys.exit(0)

   
def run_board():
    
    file_name_VCD = options.filename_VCD
    # file_name_sum = options.filename_sum
    Port      = options.port_number
    TestName  = options.test_name
    stat      = os.path.getmtime(file_name_VCD)
    TestTime  = time.ctime(stat)
    print ("reading data on port %s from files %s"%(Port, file_name_VCD))
    # data_sum = parse_csv(file_name_sum)
    data_vcd = readJSONInfoFile(file_name_VCD)

    app = dash.Dash(__name__)
    
    app.layout = html.Div(children=[
        html.H1(children='Result Visualization'),
        html.Div(children='input date '+TestTime),
        html.Div(id='my-output'),
       
        dcc.Tabs([

            dcc.Tab(label='modules', children=[
                dcc.Dropdown(
                    [value for key, value in enumerate(data_vcd)], list(data_vcd.keys())[0], id="my-input"
                ),
                dcc.Graph(
                    id='graph',
                    figure={
                        'data': [
                            {
                                'x': [i['name'] for i in data_vcd['caiu0']],
                                'y': [i['max'] for i in data_vcd['caiu0']],
                                'type': 'bar', 'name': 'max'
                            },
                            {
                                'x': [i['name'] for i in data_vcd['caiu0']],
                                'y':  [i['average'] for i in data_vcd['caiu0']],
                                'type': 'bar', 'name': 'avg'
                            },
                            {
                                'x': [i['name'] for i in data_vcd['caiu0']],
                                'y': [i['min'] for i in data_vcd['caiu0']],
                                'type': 'bar', 'name': 'min'
                            },
                         ],
                        'layout': go.Layout(title='caiu0')
                    }
                )
            ]),
        ])
    ])
    
    @app.callback(
        Output(component_id='my-output', component_property='children'),
        Input(component_id='my-input', component_property='value')
    )
    def update_output_div(input_value):
        return f'Output: ' + data_vcd[input_value][0]['name']

    app.run_server(debug=True,port=Port)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-f", "--filename_VCD", dest="filename_VCD",default="my.json",
                      help="read files from directory < dir name >", metavar="FILE")
    parser.add_option("-s", "--filename_sum", dest="filename_sum",default="sum.cvs",
                      help="read files from directory < dir name >", metavar="FILE")
    parser.add_option("-p", "--port_number", dest="port_number",default=8050,
                      help="using port number for web server", metavar="INT")
    parser.add_option("-t", "--test_name", dest="test_name",default="Test1",
                      help="test name", metavar="")
    parser.add_option("-j", "--json", dest="jsonfile",default="",
                      help="nme of JSON file with analysis data", metavar="")
    (options, args) = parser.parse_args()
    #if options.jsonfile:
    #    run_jsonanalysis()
    #else :
    run_board()
