#!/usr/bin/env python3
##
# -*- coding: utf-8 -*-
import dash
from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
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
    result = []
    with open(filename) as tsv_file:
        for line in tsv_file:
            columns = line.split("\t")
            for index, i in enumerate(columns):
                vals = i.split(":")
                if len(vals)>1:
                    # print(index, vals[0], vals[1])
                    if vals[0] == "name":
                        namevals = vals[1].split(".")
                        if len(namevals) > 4:
                            name = '.'.join(namevals[7:-1])
                            signal = namevals[-1]
                        signalDict = {}
                        signalDict['module'] = name
                        signalDict[vals[0]] = signal
                    else:
                        if vals[0] == "histogram":
                            histvals = vals[1].split(";")
                            signalDict[vals[0]] = {}
                            for j in histvals:
                                tmp = j.split("/")
                                if len(tmp)==2:
                                    signalDict[vals[0]][tmp[0]] = int(tmp[1])
                            signalDict['acchist'] = {}
                            sum = 0
                            for j in range(int(signalDict['min']), int(signalDict['max'])):
                                if str(j) in signalDict['histogram']:
                                    signalDict['acchist'][str(j)] = sum + int(signalDict['histogram'][str(j)])
                                else:
                                    signalDict['acchist'][str(j)] = sum 
                                sum = signalDict['acchist'][str(j)]
                            # print(signal['acchist'],signal['histogram'])
                        else:
                            if vals[0]=='key':
                                signalDict[vals[0]] = vals[1]
                            else:
                               signalDict[vals[0]] = float(vals[1])
            result.append(signalDict)
    return result    
     
def run_jsonanalysis(options):
    
    Port      = options.port_number
    TestName  = options.test_name
    filename  = options.jsonfile
    # print ("reading data on port %s from files %s %s %s"%(Port, file_name_sum, file_name_masterLat, file_name_slaveLat))
    
    data = parse_tsv(filename)
    df = pd.DataFrame(data, columns=['module','name','max','min','average'])
    # print(df)
    my_list = []
    for module in df['module'].unique():
        my_list.append(module)
    app = dash.Dash(__name__)
    app.layout = html.Div(children=[
        html.H1(children='ArchSim VCD based Result Visualization'),
        # html.Div(children='simulation results for test '+TestName+'; test ran '),
        dcc.Tabs([
            dcc.Tab(label='numbers per module', children=[
                dcc.Dropdown(
                    my_list, my_list[0], id="my-input"
                ),
                dcc.Dropdown(id="my-input1"
                ),
                dcc.Graph(id='graph'
                ),
                dash_table.DataTable(df.to_dict('records'), [{"name":i, "id":i} for i in df.columns])
            ]),
        ])
    ])
    
    @app.callback(
        Output(component_id='graph', component_property='figure'),
        # Output(component_id='my-input1', component_property='options'),
        Input(component_id='my-input', component_property='value')
    )
    def update_figure(input_value):
        filtered_df = df[df.module==input_value]
        print(filtered_df)
        
        fig = px.bar()
        fig.add_trace(go.Bar(name='max values',x=filtered_df['name'],y=filtered_df['max']))
        fig.add_trace(go.Bar(name='min values',x=filtered_df['name'],y=filtered_df['min']))
        fig.add_trace(go.Bar(name='average values',x=filtered_df['name'],y=filtered_df['average']))
        fig.update_layout()
        return fig
    app.run_server(debug=True, port=Port)
     
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-d", "--directory", dest="directory",default="./",
                      help="read files from directory < dir name >", metavar="FILE")
    parser.add_option("-p", "--port_number", dest="port_number",default=8050,
                      help="using port number for web server", metavar="INT")
    parser.add_option("-t", "--test_name", dest="test_name",default="Test1",
                      help="test name", metavar="")
    parser.add_option("-j", "--json", dest="jsonfile",default="",
                      help="nme of JSON file with analysis data", metavar="")
    (options, args) = parser.parse_args()
    if options.jsonfile:
        # test(options.jsonfile)
        run_jsonanalysis(options)
 
