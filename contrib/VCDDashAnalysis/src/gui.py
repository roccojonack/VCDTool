#!/usr/bin/env python3
##

import subprocess
import sys
import PySimpleGUI as sg
#import PySimpleGUIWeb as sg

def main():
    sg.ChangeLookAndFeel('BrownBlue') # change style
    layout = [
        [sg.Text('NCore3 ArchSim simulation arguments')],
        [sg.Text('Choose a Scenario File', size=(35, 1)), sg.InputText('', key='_SCEN_'), sg.FileBrowse(), sg.Button('Edit')],
        [sg.Text('Other options', size=(35, 1)), sg.InputText(key='_IN_')],
        [sg.Text('', size=(35, 1)),sg.Checkbox('Use DRAM target', key='_DRAM_', size=(35, 1), default=True)],
        [sg.Text('', size=(35, 1)),sg.Checkbox('Analyze Performance', key='_ANALYZE_', size=(35, 1), default=True)],
        [sg.Text('', size=(80, 1), key='_OUTPUT_')],
        [sg.Button('Run'), sg.Button('Show Waveform', key='Waveform', disabled=True), sg.Button('Exit')],
        [sg.Output(size=(140, 20), font=("Fixedsys", 9))]  # an output area where all print output will go
        ] 

    window = sg.Window('NCore3 ArchSim GUI', layout)
    
    while True:             # Event Loop
        event, values = window.Read()
        if event in (None, 'Exit', sg.WIN_CLOSED):         # checks if user wants to exit
            break

        if event == 'Run':                  # the two lines of code needed to get button and run command
            runSim(cmd=values['_IN_'], dram=values['_DRAM_'], scenario=values['_SCEN_'], window=window)
            window.Element('Waveform').update(disabled=False)
            if values['_ANALYZE_']:
                runAnalysis(scenario=values['_SCEN_'], window=window)
        
        if event == 'Waveform':
            runWaveform()
            
        if event == 'Edit':
            import notepad
            notepad.show(values['_SCEN_'])
                        
    window.Close()

# This function does the actual "running" of the command.  Also watches for any output. If found output is printed
def runSim(cmd, scenario, dram=None, timeout=None, window=None):
    command = 'build/Release/bin/ncore3_archsim -b -t ArchSim -s {} --use-dram-target {}'.format(scenario, cmd) if dram else 'build/Release/bin/ncore3_archsim -b -t ArchSim -s {} {}'.format(scenario, cmd)
    if window:
        window.Element('_OUTPUT_').update("Executing "+command)
        print("Executing "+command)
        window.Refresh()
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = ''
    for line in p.stdout:
        line = line.decode(errors='replace' if (sys.version_info) < (3, 5) else 'backslashreplace').rstrip()
        output += line
        print(line)
        window.Refresh() if window else None        # yes, a 1-line if, so shoot me
    res =  p.wait(timeout)
    if window:
        window.Element('_OUTPUT_').update('')
    return (res, output)

def runAnalysis(scenario, window=None):
    command = 'python3 osci-lib/contrib/TransactionAnalyzer/src/SCV_analyser.py -f ArchSim.txlog --scenario_filename={} -b -d --summary_output ArchSim.csv --parallel'%(scenario)
    if window:
        window.Element('_OUTPUT_').update("Executing "+command)
        window.Refresh()
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout:
        line = line.decode(errors='replace' if (sys.version_info) < (3, 5) else 'backslashreplace').rstrip()
        print(line)
        window.Refresh() if window else None        # yes, a 1-line if, so shoot me
    res =  p.wait()
    if window:
        window.Element('_OUTPUT_').update('')
    subprocess.Popen("python3 contrib/ArchSimGUI/src/dash-app.py ArchSim.csv", shell=True)
    return res

def runWaveform():
    subprocess.Popen("scviewer ArchSim.txlog", shell=True)

if __name__ == '__main__':
    main()
