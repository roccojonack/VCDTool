#!/usr/bin/env python3
##
# -*- coding: utf-8 -*-
import dash
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
import logging
logger = logging.getLogger(__name__)
     
def readJSONInfoFile(filename):
    if os.path.exists(filename):
        with open(filename,"r") as read_file: 
            JSonData = json.load(read_file)
        logger.info('JSON File in use: %s' %(filename))
        return JSonData
    else:
        logger.error('User Error: JSON file %s doesn\'t exist??'%filename)
        sys.exit(0)
   
def run_board(designJson):   
    file_name_VCD = options.filename_VCD
    Port      = options.port_number
    TestName  = options.test_name
    stat      = os.path.getmtime(file_name_VCD)
    TestTime  = time.ctime(stat)
    logger.info("reading data on port %s from files %s"%(Port, file_name_VCD))
    data_vcd = readJSONInfoFile(file_name_VCD)
    module_list = []
    filtered_module_list = []
    module_data = {}
    [module_list.append(value['hierachy']) for value in data_vcd if value['hierachy'] not in module_list]
    for i in module_list:
        if '.ndn1.' in i:
            continue
        if '.ndn2.' in i:
            continue
        if '.dn.' in i:
            continue
        for j in designJson['interfaces']:
            if i.endswith(j['agent']):
                filtered_module_list.append(i)
    for value in data_vcd:
        if value['hierachy'] not in module_data:
            module_data[value['hierachy']] = []
        module_data[value['hierachy']].append(value)
    app = dash.Dash(__name__)
    
    app.layout = html.Div(children=[
        html.H1(children='Result Visualization'),
        html.Div(children='input date '+TestTime),
        html.Div(id='my-output'),
       
        dcc.Tabs([
            dcc.Tab(label='modules', children=[
                dcc.Dropdown(filtered_module_list, filtered_module_list[0], id="my-input"),
                dcc.Graph(id='updated-graph'),
                dcc.Graph(id='updated-hist-graph'),
                dcc.Graph(id='updated-pivot-graph')
            ]),
        ])
    ])
    
    @app.callback(
        Output(component_id='updated-graph', component_property='figure'),
        Input(component_id='my-input', component_property='value')
    )
    def update_figure(input_value):
        updated_value = module_data[input_value]
        logger.debug(input_value)
        figure = go.Figure()
        filtered_values = []
        for i in updated_value:
            if 'avg' not in i:
                continue
            filtered_values.append(i)
            logger.debug(i)
        figure.add_trace(go.Bar(x=[i['name'] for i in filtered_values], y=[i['max'] for i in filtered_values], name='max'))
        figure.add_trace(go.Bar(x=[i['name'] for i in filtered_values], y=[i['avg'] for i in filtered_values], name='avg'))
        figure.add_trace(go.Bar(x=[i['name'] for i in filtered_values], y=[i['min'] for i in filtered_values], name='min'))
        return figure

    @app.callback(
        Output(component_id='updated-hist-graph', component_property='figure'),
        Input(component_id='my-input', component_property='value')
    )
    def update_hist_figure(input_value):
        updated_value = module_data[input_value]
        logger.debug(input_value)
        figure = go.Figure()
        x_min = min([i['min'] for i in updated_value if 'histogram' in i])
        x_max = max([i['max'] for i in updated_value if 'histogram' in i])
        x_list = []
        for i in range(x_min,x_max+2):
            x_list.append(i)
        for i in updated_value:
            if 'histogram' not in i:
                continue
            if i['histogram'] is None:
                continue
            y_list = []
            for j in range(int(i['max']+1)):
                if str(j) in i['histogram'].keys():
                    y_list.append(i['histogram'][str(j)])
                else:
                    y_list.append(0)
            y_list.append(0)
            figure.add_trace(go.Scatter(x=x_list, y=y_list, line_shape='hv',name=i['name']))
        figure.update_xaxes(title_text="Values of counters as histogram")
        figure.update_yaxes(title_text="Percentage of time")
        return figure

    @app.callback(
        Output(component_id='updated-pivot-graph', component_property='figure'),
        Input(component_id='my-input', component_property='value')
    )
    def update_hist_figure(input_value):
        updated_value = module_data[input_value]
        logger.debug(input_value)
        figure = go.Figure()
        x_min = min([i['min'] for i in updated_value if 'histogram' in i])
        x_max = max([i['max'] for i in updated_value if 'histogram' in i])
        x_list = []
        for i in range(x_min,x_max+2):
            x_list.append(i)
        for i in updated_value:
            if 'histogram' not in i:
                continue
            if i['histogram'] is None:
                continue
            y_list = []
            running_value = 100
            if i['firstVal']==i['max']:
                for j in range(int(i['max']),int(i['min'])-1,-1):
                    y_list.append(running_value)
                    if str(j) in i['histogram'].keys():
                        running_value-=i['histogram'][str(j)]
            else:
                for j in range(int(i['min']),int(i['max'])+1):
                    y_list.append(running_value)
                    if str(j) in i['histogram'].keys():
                        running_value-=i['histogram'][str(j)]
            y_list.append(0)       
            figure.add_trace(go.Scatter(x=x_list, y=y_list, line_shape='hv',name=i['name']))
        figure.update_xaxes(title_text="distribution of counter values")
        figure.update_yaxes(title_text="Percentage of time")
        return figure

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
    designJson = {}
    if options.jsonfile:
        designJson = readJSONInfoFile(options.jsonfile)
        for i in ["dce0", "dce1", "dce2"]:
            elem = {}
            elem['agent'] = i
            designJson['interfaces'].append(elem)
    run_board(designJson)
