#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Jun 19, 2014

@author: eccglln
'''
from Tkinter import *


class ProgramSelectGUI(object):
    
    def __init__(self, programList):
        
        super(ProgramSelectGUI, self).__init__()
        
        self.top = Tk()
        self.programList = programList
        self.selection = [None]
        
    def buttonPressed(self):
        
        print 'please wait.....'
        for i in self.programListBox.curselection():
            self.selection[0] = self.programListBox.get(i)
        self.top.destroy()
        
    def createGUI(self):
        
        self.top.title('program selection dialog')
        self.top.geometry('600x250+500+500')
        topFrame = Frame(self.top)
        topFrame.pack()
        
        bottomFrame = Frame(self.top)
        bottomFrame.pack(side=BOTTOM)
        programFrame = LabelFrame(topFrame, text='Chose one program you want to operate')
        programFrame.pack(fill='both', expand='yes')
        
        programScrollBar = Scrollbar(programFrame)
        programScrollBar.pack(side=RIGHT, fill=Y)
        self.programListBox = Listbox(programFrame, selectmode=SINGLE, yscrollcommand=programScrollBar.set, \
                                  exportselection=False, bd=10, width=60)
        for item in self.programList:
            self.programListBox.insert(END, item)
        self.programListBox.pack()
        programScrollBar.configure(command=self.programListBox.yview)                            
        
        selectButton = Button(bottomFrame, text='Next', command=self.buttonPressed)
        selectButton.pack()
        

        
    def mainLoop(self):
        
        self.createGUI()
        print 'Load successfully!'
        self.top.mainloop()
        

class MyGUI(object):
    
    def __init__(self, srcReport, cmpReport):
        
        super(MyGUI, self).__init__()
        
        self.top = Tk()
        self.srcReportNo = srcReport
        self.cmpReportNo = cmpReport
        self.srcReportSelection = []
        self.cmpReportSelection = [None]

    def buttonPressed(self):
        '''
        When button is pressed, return what is selected
        '''
        
        for i in self.srcListBox.curselection():
            self.srcReportSelection.append(self.srcListBox.get(i))
        for i in self.cmpListBox.curselection():
            self.cmpReportSelection[0] = (self.cmpListBox.get(i))
        self.srcReportSelection = list(set(self.srcReportSelection))
        self.cmpReportSelection = list(set(self.cmpReportSelection))
        self.srcReportSelection.sort()
        
        self.finalSelection = [self.srcReportSelection, self.cmpReportSelection]
        self.top.destroy()
        
    
    def createGUI(self):
        ''' create my own GUI '''
        self.top.title('Test Report Generator')
        self.top.geometry('400x250+500+500')
        topFrame = Frame(self.top)
        topFrame.pack()
        
        bottomFrame = Frame(self.top)
        bottomFrame.pack(side=BOTTOM)
        
        srcReportFrame = LabelFrame(topFrame, text='Chose test report from feature branch')
        srcReportFrame.pack(fill='both', expand='yes', side=LEFT)
        
        cmpReportFrame = LabelFrame(topFrame, text='Chose test report from LSV')
        cmpReportFrame.pack(fill='both', expand='yes', side=RIGHT)
    
    
        srcScrollBar = Scrollbar(srcReportFrame)
        srcScrollBar.pack(side=RIGHT, fill=Y)
        self.srcListBox = Listbox(srcReportFrame, selectmode=MULTIPLE, yscrollcommand=srcScrollBar.set, \
                                  exportselection=False)
        for item in self.srcReportNo:
            self.srcListBox.insert(END, item)
        self.srcListBox.pack()
        srcScrollBar.configure(command=self.srcListBox.yview)
        
        cmpScrollBar = Scrollbar(cmpReportFrame)
        cmpScrollBar.pack(side=RIGHT, fill=Y)
        self.cmpListBox = Listbox(cmpReportFrame, selectmode=SINGLE, yscrollcommand=cmpScrollBar.set, \
                                  exportselection=False)
        for item in self.cmpReportNo:
            self.cmpListBox.insert(END, item)
        self.cmpListBox.pack()
        cmpScrollBar.configure(command=self.cmpListBox.yview)    
        

        
        generateButton = Button(bottomFrame, text='Generate', command=self.buttonPressed)
        generateButton.pack()
        
        
    def mainLoop(self):
        
        self.createGUI()
        print 'Load successfully!'
        self.top.mainloop()

        
if __name__ == '__main__':
    pass

                
                
                
                
                
                
                
                
                
                
                
                
                
                