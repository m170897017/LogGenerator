#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Jun 19, 2014

@author: eccglln
'''

import re
import copy
import HTTPHandler

class ContentProcessor(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.logFoundPa = re.compile('REGRESSION RESULTS')
        self.myHTMLParser = HTTPHandler.HTMLHandler()
        self.content = None
        
        self.patterns = [(re.compile('CHANGES/FIXES [A-Z :<>/tdrb-]+'),            
                          # start of content of CHANGES/FIXES SINCE PREVIOUS BUILD 
                          re.compile('<tr><td>-+[\r<>/tdrb ]+REGRESSION RESULTS')),  
                         # end of content of CHANGES/FIXES SINCE PREVIOUS BUILD
                          (re.compile('REGRESSION RESULTS:'),
                          #start of content of REGRESSION RESULTS    
                          re.compile('<tr><td>-+[\r<>/tdrb ]+FUNCTIONAL TESTS')),
                         # end of content of REGRESSION RESULTS
                         
                         ]
        
    def isFinalReportFound(self, pageInfo):
        ''' return true if there is final report '''
        return True if self.logFoundPa.findall(pageInfo) else False
    
    def __locateContent(self, (start, end)):
        '''
        start  : where content starts
        end    :   where content ends
        return : content between start and end, in html format 
        '''
        
        tempRes = start.findall(self.content)[0]
        assert tempRes, 'Something is wrong when parseing pageInfo to find start!'
        startIndex = self.content.index(tempRes)
        startLen   = len(tempRes)
        
        tempRes = end.findall(self.content)[0]
        assert tempRes, 'Something is wrong when parseing pageInfo to find end!'
        endIndex = self.content.index(tempRes)
        
        # 10 is length of </td></tr>
        return self.content[startIndex+startLen:endIndex-10]        
        

    def getFinalReportContent(self, content):
        '''
        content : original html page info
        return  : a list, changes/regress content in html format, test result in dict
        '''
        
        # I don't want to change content of CHANGES/FIXES and REGRESSION RESULTS, so I put re parsing here
        # I need to customize content of FUNCTIONAL TESTS, so I put content parsing in myHTMLParser
        self.content = content
        [changesContent, regressContent] = map(self.__locateContent, self.patterns)

        self.myHTMLParser.feed(content)
        with open('C:\\Temp\\all.txt', 'w') as f:
            f.write(repr(self.myHTMLParser.all))
        # if build number exists in the list, remove it
        # after this line, list would look like  
        # ['(FW)-(PatternMidflowsTS)-PatternMidflowsTS :', '- Total test cases: 3', '- Passed: 3', '- Failed: 0', '- Skipped: 0']
        if re.match('\d+', self.myHTMLParser.data[0]):
            self.myHTMLParser.data.pop(0)
        resultList = copy.deepcopy(self.myHTMLParser.data)
        
        resultDict = self.__changeListtoDict(resultList)
        
        return [changesContent, regressContent, resultDict]
        
    def __initDict(self):
        
        return   {'version': None,
                  'platform': None,
                  'Total': '0',
                  'Passed': '0',
                  'PA/RET TCs': [],
                  'Failed': '0',
                  'Failed TCs': [],
                  'Skipped': '0',
                  'Skipped TCs': [],}
            
    def __changeListtoDict(self, resultList):
        '''
        resultList: like ['(FW)-NSTcr6447-NSTcr6447_standalone-remote (NSTcr6447-no_branch_31bf59c-20140725):', \
                                                '- Total test cases: 3', '- Passed: 3', '- Failed: 0', '- Skipped: 0']
        resultDict: like {'(FW)-NSTcr6447-NSTcr6447_standalone-remote':{'version': None,
                                  'platform': 'standalone-remote',
                                  'Total': '3',
                                  'Passed': '3',
                                  'PA/RET TCs': None,
                                  'Failed': '3',
                                  'Failed TCs': None,
                                  'Skipped': '0',
                                  'Skipped TCs': None,}}        
        '''
        assert isinstance(resultList, list), 'please deliver a list to __changeListtoDict'
        
        res = {}
        nextL = None
        for i in resultList:
            if re.search('FW', i):
                TSname = i.split()[0]
                res[TSname] = self.__initDict()
                if 'standalone-remote' in i:
                    res[TSname]['platform'] = 'standalone-remote'
                elif 'ssr-sim' in i:
                    res[TSname]['platform'] = 'ssr-sim'
                elif 'cluster' in i:
                    res[TSname]['platform'] = 'cluster'
                nextL = 'Total'
            elif nextL == 'Total' and re.search('Total', i):
                res[TSname]['Total'] = re.findall('\d+', i)[0]
                nextL = 'Passed'
            elif nextL == 'Passed' and re.search('Passed', i):
                res[TSname]['Passed'] = re.findall('\d+', i)[0]
                nextL = 'Failed'
            elif nextL == 'Failed' and not re.search('Failed', i):
                res[TSname]['PA/RET TCs'].append(i.strip())
            elif nextL == 'Failed' and re.search('Failed', i):
                res[TSname]['Failed'] = re.findall('\d+', i)[0]
                nextL = 'Skipped'
            elif nextL == 'Skipped' and not re.search('Skipped', i) and \
                re.search('TC-', i):
                res[TSname]['Failed TCs'].append(i.strip())
            elif nextL == 'Skipped' and re.search('Skipped', i):
                res[TSname]['Skipped'] = re.findall('\d+', i)[0]
                nextL = 'Skipped TCs'
            elif nextL == 'Skipped TCs' and not re.search('Skipped', i):
                res[TSname]['Skipped TCs'].append(i.strip())

        return res
            

        
                
if __name__ == '__main__':
    
    pass

    
                    
                    
                    
                    
                    