#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Jun 19, 2014

@author: eccglln
'''
import HTTPHandler
import ContentProcessor
import GUI
import re
import datetime
import getpass
from Settings import *


class testReportGenerator(object):
    
    def __init__(self):
        ''' doc '''
        print 'loading...'
        self.username              = raw_input('Please enter your EID: ') 
        self.password              = getpass.getpass('Please enter your windows password: ')
        self.url_sasn_program      = URL_PL_SASN_PROGRAM
        self.srcURL                = None
        self.featureBranch         = None
        self.cmpURL                = URL_LSV_PROGRAM
        self.finalReportPath       = FINAL_REPORT_PATH
        self.firstTestReportPath   = FIRST_TEST_REPORT_PATH
        self.LSVReportPath         = LSV_FINAL_REPORT_PATH
        self.createFinalReportPath = CREATE_FINAL_REPORT_PATH
        self.savedReportPath       = URL_SAVED_REPORT
        self.templatePath          = TEMPLATE_PATH
        self.finalPath             = FINAL_PATH
        self.resultPath            = RESULT_PATH
        self.pipeLineInfo          = {}
        
        self.httpHandler           = HTTPHandler.HTTPHandler(URL_LOG_IN, self.username, self.password)
        self.myHTMLParser          = HTTPHandler.HTMLHandler()
        self.contentProcessor      = ContentProcessor.ContentProcessor()
        
    def __getProgramList(self):
        '''
        return: list of program
        '''
        
        pageInfo = self.httpHandler.get_content_from_url(self.url_sasn_program)
        self.myHTMLParser.feed(pageInfo.decode('utf-8'))
        return self.myHTMLParser.programList
        
        
    def __getBuildInfo(self, programName):
        ''' 
        programName : name of feature branch, like 'FEATURE_CBC_ICAP_ABSOLUTE_PATH'
        return      : build numbers from specific URLs, like
        [u'25', u'24', u'23', u'22', u'21', u'20', u'19', u'18', u'17', u'16']
        [u'10/R1A45_00', u'10/R1A46_00', u'10/R1A47_00', u'10/R1A48_00', u'10/R1A49_00', u'10/R1A50_00', \
                                                                                        u'10/R1A51_00', u'10/R1B01_00']
        '''
        print '\nLoading......\n'      
        
        self.srcURL = self.url_sasn_program + 'view/' + programName + '/'
        
        
        pageInfo = map(self.httpHandler.get_content_from_url, [self.srcURL, self.cmpURL])
        self.myHTMLParser.feed(pageInfo[0].decode('utf-8'))
        
        # store pipeLine from list to dict, like {24:{'firstTestID':4, 'retestID':3}}
        for i in xrange(0, len(self.myHTMLParser.pipelineData), 3):
            self.pipeLineInfo[self.myHTMLParser.pipelineData[i]] = {'firstTestID':self.myHTMLParser.pipelineData[i+1],
                                                                    'retestID':self.myHTMLParser.pipelineData[i+2],
                                                                    }            
            
        
#         srcBuilds = copy.deepcopy(self.myHTMLParser.pipelineData[::3])
        srcBuilds = self.myHTMLParser.pipelineData[::3]
        
        # if you want to use self.myHTMLParser.pipelineData, you have to reset it here to restore new data
        # if not, just let it be
#         self.myHTMLParser.pipelineData = []
        
        self.myHTMLParser.feed(pageInfo[1].decode('utf-8'))
        
        
        cmpBuilds = list(set(self.myHTMLParser.displayName))
        cmpBuilds.sort()
        return [srcBuilds, cmpBuilds]
         
    def __startGUI(self):
        ''' Start my own GUI according to build numbers '''

        programGUI = GUI.ProgramSelectGUI(self.__getProgramList())
        programGUI.mainLoop()
        self.featureBranch = programGUI.selection[0]
        
        srcReports, LSVReports = self.__getBuildInfo(self.featureBranch)
        generatorGUI = GUI.MyGUI(srcReports, LSVReports)
        generatorGUI.mainLoop()

        [self.srcReportSelection, self.cmpReportSelection] = generatorGUI.finalSelection
        
        
    
    def __getReportFromURL(self, reportPath, createFinalReportPath=None, savedReportPath=None, stillCreate=0):
        '''
        reportPath            : URL to get final report
        createFinalReportPath : URL to create final report
        savedReportPath       : URL to get saved report
        stillCreate           : 1 stands for creating final report no matter if final report already exists
                                0 stands for not creating final report if final report already exists
        return                : list, report content in customized format 
        '''   
        
        # we will try to fetch final report from two places
        showSavedPageInfo = self.httpHandler.get_content_from_url(reportPath)
        showFinalReportPageInfo = self.httpHandler.get_content_from_url(reportPath.replace('saved', 'savednotes'))
        
#         with open('C:\\Temp\\saved.txt', 'w') as f:
#             f.write(showSavedPageInfo)
#             
#         with open('C:\\Temp\\savednotes.txt', 'w') as f:
#             f.write(showFinalReportPageInfo)
#         assert 0
        try:
            if 0 == stillCreate and self.contentProcessor.isFinalReportFound(showSavedPageInfo):
                return self.contentProcessor.getFinalReportContent(showSavedPageInfo)
            elif 0 == stillCreate and self.contentProcessor.isFinalReportFound(showFinalReportPageInfo):
                return self.contentProcessor.getFinalReportContent(showFinalReportPageInfo)
            elif createFinalReportPath and savedReportPath:
                # if there is no final report or has final report but stillCreate=1, then create it
                return self.contentProcessor.getFinalReportContent(\
                                                self.httpHandler.createFinalReport(createFinalReportPath, savedReportPath))
            else:
                assert 0, "Final report isn't found in LSV branch you selected, you should make sure there is."
        except AssertionError as e:
            print '='*20
            print str(e)
            print '='*20
            raw_input('Now press enter to exit.')
            exit()
        except Exception as e:
            print '='*20
            print 'It seems there is no test result in your feature branch.'
            print '='*20
            raw_input('Now press enter to exit.')
            exit()
            
        
            
    def getReportAndCompare(self, srcBuildNoList, cmpBuildNo):
        '''
        srcBuildNoList : build number of source report by user selection, like ['24', '17']
        cmpBuildNo     : build number of cmp report by user selection, like ['10/R1A48_00']
        return         : a list including formatted report content
        '''
        # lists to store report data
        srcReport = []
        dstReport = []
        
        # dicts to store final compared data
        failDiff  = {}
        failSame  = {}
        passDiff  = {}
        passSame  = {}
        missingTS = {}
        
#         srcReports, LSVReports = self.__getBuildInfo(self.featureBranch)
        
        for num in srcBuildNoList:
            buildNo = str(self.pipeLineInfo[num]['retestID'])
            finalReportPath = self.finalReportPath % (self.featureBranch, self.featureBranch, buildNo)
            firstTestReportPath = self.firstTestReportPath % (self.featureBranch, self.featureBranch, buildNo)
            createFinalReportPath = self.createFinalReportPath % (self.featureBranch, self.featureBranch, buildNo)
            savedReportPath = self.savedReportPath % (self.featureBranch, self.featureBranch, buildNo)
            
            # store report of first run 
#             srcReport.append(self.__getReportFromURL(firstTestReportPath, createFinalReportPath, savedReportPath))
            # store report of retest
            srcReport.append(self.__getReportFromURL(finalReportPath, createFinalReportPath, savedReportPath))
        LSVbuildNo = self.myHTMLParser.displayNameVSNumber[cmpBuildNo[0]]    
        reportPath = self.LSVReportPath % LSVbuildNo         
        dstReport = self.__getReportFromURL(reportPath)
        
        # source reports have been stored in srcReport by order, so I use content of srcReport at largest number 
        # if there is any conflict when combining all the source reports
        srcReportNums = len(srcReport)
        print 'Now start to combine %d source reports' % srcReportNums 
        finalReportChangesContent = srcReport[-1][0]
        finalReportRegressContent = srcReport[-1][1]
        finalReportTestResult = srcReport[0][2]
        for i in xrange(1, srcReportNums):
            finalReportTestResult.update(srcReport[i][2])
        LSVReportTestResult = dstReport[2]
        
#         with open('C:\\Temp\\002.txt', 'w') as f:
#             f.write(repr(finalReportTestResult))
#             f.write('#'*100)
#             f.write(repr(LSVReportTestResult))
        
        
        # start to compare src report with LSV report and store result into 4 dicts
        print 'Now start to compare feature reports with LSV reports\nPlease wait...'
        total = 0
        failed = 0
        skipped = 0
        passed = 0
        for TSname in LSVReportTestResult.keys():
            if finalReportTestResult.has_key(TSname):
                if finalReportTestResult[TSname]['Failed'] == '0':
                    if finalReportTestResult[TSname] == LSVReportTestResult[TSname]:
                        passSame[TSname] = finalReportTestResult[TSname]
                    else:
                        passDiff[TSname] = finalReportTestResult[TSname]
                elif finalReportTestResult[TSname]['Failed'] != '0':
                    if finalReportTestResult[TSname] == LSVReportTestResult[TSname]:
                        failSame[TSname] = finalReportTestResult[TSname]
                    else:
                        failDiff[TSname] = finalReportTestResult[TSname]
                total += int(finalReportTestResult[TSname]['Total'])
                failed += int(finalReportTestResult[TSname]['Failed'])
                skipped += int(finalReportTestResult[TSname]['Skipped'])
                passed += int(finalReportTestResult[TSname]['Passed'])
                
            else:
                missingTS[TSname] = LSVReportTestResult[TSname]
        summary = [total, failed, skipped, passed]
        # sometimes # will appear in the keys of missingTS, we need to delete it 
        if missingTS.has_key('#'):
            missingTS.pop('#')
            
        # after comparison, use 4 dicts to generater final report html file
        self.generateFinalReport(changes = finalReportChangesContent, 
                                 regressionResult = finalReportRegressContent, 
                                 failDiffFromLSV = failDiff, 
                                 failSameAsLSV = failSame,
                                 passDiffFromLSV = passDiff, 
                                 passSameAsLSV = passSame, 
                                 missingTSComparedToLSV = missingTS,
                                 summary = summary)
        
        print "#"*30    
        print 'Done!!!\nNow you can check your report in final_report folder!'
        print "#"*30
        
    def generateFinalReport(self, changes, regressionResult, failDiffFromLSV, failSameAsLSV, passDiffFromLSV,
                            passSameAsLSV, missingTSComparedToLSV, summary):
        '''
        changes                : content of changes/fixes since previous build
        regressionResult       : content of regression results
        failDiffFromLSV        : failed TS and different from LSV
        failSameAsLSV          : failed TS and same with LSV
        passDiffFromLSV        : passed TS and different from LSV
        passSameAsLSV          : passed TS and same with LSV
        missingTSComparedToLSV : run in LSV but not in current report
        summary                : test executive summary, like [100, 10, 10, 80], which means total, failed, skipped, passed
        return                 : None. 
        
        Final report will be created during this function
        '''
        
        with open(self.templatePath, 'r') as f: 
            template = f.read()
            
        # calculate pass rate
        passRate = '{:.0%}'.format(float(summary[3])/float(summary[0]))
        TRsum = 'Total test cases: %d, Failed test cases: %d, Skipped test cases: %d, passed test cases: %d. \
        Pass rate is %s.' % (summary[0], summary[1], summary[2], summary[3], passRate)
        
        template = re.sub('replace_changes_fixes', changes, template)
        template = re.sub('replace_regression_results', regressionResult, template)
        template = re.sub('replace_executive_sum', TRsum, template)
        template = re.sub('replace_failDiff', self.__renderHTML(failDiffFromLSV), template)
        template = re.sub('replace_failSame', self.__renderHTML(failSameAsLSV), template)
        template = re.sub('replace_passDiff', self.__renderHTML(passDiffFromLSV), template)
        template = re.sub('replace_passSame', self.__renderHTML(passSameAsLSV), template)
        template = re.sub('replace_missingTS', self.__renderHTML(missingTSComparedToLSV), template)
        
        
        
        filename = 'final_report_' + datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S') + '.html'
        
        with open(self.finalPath+filename, 'w') as f: 
            f.write(template)

    def __renderHTML(self, result):
        '''
        result : a dictionary, like {
        '(FW)-NSTgycounter-gycounter_standalone-remote': {'platform': 'standalone-remote',
         'Skipped TCs': ['TC-CR8140-GXGY0020', 'TC-CR8140-GXRAAER0050'], 'version': None, 'PA/RET TCs': [],
          'Passed': '46', 'Failed': '0', 'Skipped': '2', 'Total': '48', 'Failed TCs': []},    
                                   }
        return : a string in HTML format
        '''
        finalFormattedResult = ''
        if result:
            with open(self.resultPath, 'r') as f:
                resultTemplate = f.read()
                
            for TSname in result.keys():
                formattedResult = resultTemplate.replace('replace_TSname', TSname)
                formattedResult = formattedResult.replace('replace_total', result[TSname]['Total'])
                formattedResult = formattedResult.replace('replace_passed', result[TSname]['Passed'])
                if result[TSname]['PA/RET TCs']:
                    paretTCs = '<br>'.join(result[TSname]['PA/RET TCs'])
                    formattedResult = formattedResult.replace('replace_paretTCs', paretTCs)
                else:
                    formattedResult = formattedResult.replace('replace_paretTCs', '')
                formattedResult = formattedResult.replace('replace_failed', result[TSname]['Failed'])
                if result[TSname]['Failed TCs']:
                    failedTCs = '<br>'.join(result[TSname]['Failed TCs'])
                    formattedResult = formattedResult.replace('replace_FailedTCs', failedTCs)
                else:
                    formattedResult = formattedResult.replace('replace_FailedTCs', '')
                formattedResult = formattedResult.replace('replace_skipped', result[TSname]['Skipped'])
                if result[TSname]['Skipped TCs']:
                    skippedTCs = '<br>'.join(result[TSname]['Skipped TCs'])
                    formattedResult = formattedResult.replace('replace_SkippedTCs', skippedTCs)
                else:
                    formattedResult = formattedResult.replace('replace_SkippedTCs', '')
                finalFormattedResult += formattedResult
                
        return finalFormattedResult
        
        
        
    def run(self):
        
        self.__startGUI()
        print 'You selected build %s from feature branch %s' % (str(self.srcReportSelection), str(self.featureBranch))
        print 'Now start to compare with LSV build ', self.cmpReportSelection
        self.getReportAndCompare(self.srcReportSelection, self.cmpReportSelection)
        raw_input('Now press enter to exit.')
        
if __name__ == '__main__':
    
    
    # Based Python 2.7

    
    
    my = testReportGenerator()
    my.run()

    
    
    
    
    
    
    