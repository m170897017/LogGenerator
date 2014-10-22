#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Jun 19, 2014

@author: eccglln
'''

import HTMLParser
import re
import requests
import json
from Settings import *
import time

class HTTPHandler(object):
    '''
    This class contains all kinds of HTTP operations.
    '''


    def __init__(self, domain, username, password):
        '''
        Constructor
        '''
        # log in and create a keep-alive session
        self.session  = requests.session()
        login_rsp = self.session.get(domain, auth=(username, password), verify=False)
        
        assert login_rsp.status_code == 200, 'Log in Jenkins failed!!'
        
        
        
        self.createReportData = {'mode': 'create',
                                 'formerNotes': 'no final report found',
                                 'buildList': '--none--',
                                 'offiBuildList': '--none--',
                                 'formerComReport': 'no comparison report found',
                                 'formerReport': 'no created report found',
                                 'json': '{"mode":{"value":"create"}}',
                                 'Submit': 'Apply',
                                 }
        self.commonHeaders = {'Accept': 'text/html, application/xhtml+xml',
                                    'Accept-Language': 'en-US',
                                    'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
                                    'Content-type': 'application/x-www-form-urlencoded',
                                    'Accept-Encoding': 'gzip, deflate',
                                    'Connection': 'Keep-Alive',
                                    }

        self.domainPattern = re.compile('http://\d+.\d+.\d+.\d+')

    
    def get_content_from_url(self, relative_path=None):
        '''
        relative_path : should be a string like '/view/SASN_PROGRAM/job/GOYA/'
        return        : html page info got from relative_path
        '''
        
        return self.session.get(relative_path).text.encode('utf8')
        
    def createFinalReport(self, create_path, saved_report_path):
        '''
        create_path       : where to create final report
        saved_report_path : where report is saved after creating
        return            : final report content
        '''
        print 'We have to wait for 6mins at most'
        self.session.post(create_path, self.createReportData)
        retryTimes = 7
        while retryTimes >= 0:
            retryTimes -= 1
            info = self.get_content_from_url(saved_report_path)
            if 'Cannot execute the process' in info or 'no created report found' in info:
                print 'now start fetching content of saved report'
                print 'nothing has been saved so far, we have to wait 60s'
                time.sleep(60)
                continue
            
            break
        assert retryTimes >=0, 'after 7 retries, there is still no report generated. Maybe something wrong with Jenkins.'
        return info

    def __del__(self):
        ''' release connection '''
        self.session.close()        

class HTMLHandler(HTMLParser.HTMLParser):
    
    def __init__(self):
        '''
        This class handles all kinds of HTML parsing operation
        '''
        HTMLParser.HTMLParser.__init__(self)
        self.all    = []
        self.data        = []
        self.options     = []
        self.programList = []
        self.buildNum    = []
        self.LSVbuildNum = []
        self.pipelineData = []
        self.displayName  = []
        self.displayNameVSNumber = {}
        self.next        = None
        self.TSpattern = ['FW', 'Total test cases', 'Passed', 'Failed', 'Skipped']
        self.TSname = 'FW'
        self.totalTC = 'Total test cases'
        self.passTC = 'Passed'
        self.failTC = 'Failed'
        self.skipTC = 'Skipped'
        self.testResultEnd = '#+'
        self.buildVariable = 'buildData'
        self.buildDataPattern = re.compile(self.buildVariable)
        self.LSVbuildNo = re.compile('displayName":"\d+\/\w+"')
        
        
        
    def handle_starttag(self, tag, attri):
        '''
        tag    : eg. href, a etc.
        attri  : eg. value etc.
        return : None
        '''
        
        #to get reports number from ericoll report page
        if tag == 'option':
            for i in attri:
                if i[0] == 'value':
                    self.options.append(i[1])
#         print 'tag is: ', tag
#         print 'attri is: ', attri
        
    def handle_data(self, data):
        '''  
        data   : handle data from different pages
        return : None
        save what we want in self.data, keep it as a list
        
        Example for self.buildData: '{"id":1524332842,"build":{"dependencyIds":[2015584660],"displayName":"#24",
        "duration":"1 hr 20 min","extId":"PL_BUILD_FEATURE_CBC_ICAP_ABSOLUTE_PATH#24","hasPermission":true,
        "hasUpstreamBuild":true,"isBuilding":false,"isComplete":true,"isPending":false,"isSuccess":true,
        "isReadyToBeManuallyBuilt":false,"isManualTrigger":false,"isRerunable":true,"isLatestBuild":true,
        "isUpstreamBuildLatest":false,"isUpstreamBuildLatestSuccess":false,"number":24,"progress":0,"progressLeft":100,
        "startDate":"Aug 15, 2014","startTime":"9:21:55 AM","status":"SUCCESS",
        "url":"job/PL_BUILD_FEATURE_CBC_ICAP_ABSOLUTE_PATH/24/","userId":"eyiilei","estimatedRemainingTime":null}} ' 
        
        I get it from HTML info. It refers to JS structure on Jenkins.
        
        '''
#         print 'data is: ', data
        self.all.append(data)
        
        # in pipelineData of feature branch, it will look like [24, 4, 3, 23, 3, 2, ...] 
        # where three numbers pergroup, 
        # 24 is pipeline number, 4 is first run number, 3 is retest number and then cycle
        
        # in pipelineData of LSV branch, it will look like [37, 22, null, null, null, ...]
        # where five numbers per group
        # 37 is pipeline number, 22 is first run number, null is retest number and then cycle
        # we ignore the rest two elements
                
        if self.buildDataPattern.search(data):
            self.buildData = json.loads(data[data.index(self.buildVariable)+12:data.index('}};')+2])
            if not self.buildData['build']['extId']:
                self.pipelineData.append(self.buildData['build']['extId'])
            else:
                self.pipelineData.append(re.search('\d+', self.buildData['build']['extId']).group())
            
            # we only need displayName like 10/R1A49_00    
            displayName = self.buildData['build']['displayName']
            if displayName and '/' in displayName:
                self.displayName.append(displayName) 
            
            if self.buildData['project']['name'] == 'PL_SCOPE_FT_FULL_RETEST_LSV':
                self.displayNameVSNumber[self.buildData['build']['displayName']] = self.buildData['build']['number']    

            
        res = self.LSVbuildNo.search(data) 
        if res:
            self.LSVbuildNum.append(res.group().replace('displayName":"', '').replace('"', ''))
            
        # to get program list on PL_SASN_PROGRAM page            
        if data.startswith('FEATURE_'):
            self.programList.append(data)
            
        # to get test result from report
        elif re.search(self.TSname, data):
            # when get '(FW)-*', save it
            self.next = 'Total'
            self.data.append(data)
        elif self.next == 'Total' and re.search(self.totalTC, data):
            # when get 'Total test cases', save it
            self.next = 'Passed'
            self.data.append(data)
        elif self.next == 'Passed' and re.search(self.passTC, data):
            # when get 'Passed *', save it
            self.next = 'Failed'
            self.data.append(data)
        elif self.next == 'Failed' and not re.search(self.failTC, data):
            # when get 'TC-* #PA/RET', save it
            self.data.append(data)
        elif self.next == 'Failed' and re.search(self.failTC, data):
            # when get 'Failed *', save it
            self.next = 'Skipped'
            self.data.append(data)
        elif self.next == 'Skipped' and not re.search(self.skipTC, data):
            # when get 'TC-*', save it
            # sometimes we will get '....' in this line, we need to skip it
            if not re.search('\.+', data):
                self.data.append(data)
        elif self.next == 'Skipped' and re.search(self.skipTC, data):
            # when get 'Skipped *', save it
            self.next = 'skipped TCs'
            self.data.append(data)
        elif self.next == 'skipped TCs':
            if re.search(self.testResultEnd, data):
                # when reach the end '####*', end saving
                self.next = 'end'
            else:
                # when get 'TC-*', save it
                self.data.append(data)
        
if __name__ == '__main__':
    
    p = HTTPHandler(DOMAIN)
#     path = '/view/SASN_PROGRAM/job/GOYA/'
#     print p.get_content_from_url(relative_path=path)
#     print '--------------------------------------------------------'
#     print p.get_content_from_url(relative_path=path)
#     print p.createFinalReport('/view/SASN_PROGRAM/job/GOYA/253/report/createReport')
            
    URL = 'https://sasn-jenkins-pc.mo.sw.ericsson.se/view/LSV/'
    URL1 = 'https://sasn-jenkins-pc.mo.sw.ericsson.se/view/PL_SASN_PROGRAM/view/FEATURE_CBC_ICAP_FIXED_NETWORK/'
    
    URL2 = 'https://sasn-jenkins-pc.mo.sw.ericsson.se/view/PL_SASN_PROGRAM/view/FEATURE_CBC_ICAP_ABSOLUTE_PATH/job/PL_SCOPE_FT_FULL_RETEST_FEATURE_CBC_ICAP_ABSOLUTE_PATH/3/report/createReport'
    URL3 = 'https://sasn-jenkins-pc.mo.sw.ericsson.se/view/PL_SASN_PROGRAM/view/FEATURE_CBC_ICAP_ABSOLUTE_PATH/job/PL_SCOPE_FT_FULL_RETEST_FEATURE_CBC_ICAP_ABSOLUTE_PATH/3/report/saved'
    
    URL4 = 'https://sasn-jenkins-pc.mo.sw.ericsson.se/view/PL_SASN_PROGRAM/view/FEATURE_CBC_ICAP_ABSOLUTE_PATH/job/PL_SCOPE_FT_FULL_RETEST_FEATURE_CBC_ICAP_ABSOLUTE_PATH/2/report/createReport'
    URL5 = 'https://sasn-jenkins-pc.mo.sw.ericsson.se/view/PL_SASN_PROGRAM/view/FEATURE_CBC_ICAP_ABSOLUTE_PATH/job/PL_SCOPE_FT_FULL_RETEST_FEATURE_CBC_ICAP_ABSOLUTE_PATH/2/report/saved'
    
    U6 = 'https://sasn-jenkins-pc.mo.sw.ericsson.se/view/PL_SASN_PROGRAM/view/FEATURE_CBC_ICAP_ABSOLUTE_PATH/job/PL_SCOPE_FT_FULL_FEATURE_CBC_ICAP_ABSOLUTE_PATH/5/report/createReport'
    U7 = 'https://sasn-jenkins-pc.mo.sw.ericsson.se/view/PL_SASN_PROGRAM/view/FEATURE_CBC_ICAP_ABSOLUTE_PATH/job/PL_SCOPE_FT_FULL_FEATURE_CBC_ICAP_ABSOLUTE_PATH/5/report/saved'
    
    
    
#     p.createFinalReport(create_path=U6, saved_report_path=U7)
    u = 'https://sasn-jenkins-pc.mo.sw.ericsson.se/view/PL_SASN_PROGRAM/view/FEATURE_CBC_ICAP_ABSOLUTE_PATH/job/PL_SCOPE_FT_FULL_FEATURE_CBC_ICAP_ABSOLUTE_PATH/4/report/savednotes'
    u1 = 'https://sasn-jenkins-pc.mo.sw.ericsson.se/view/LSV/job/PL_SCOPE_FT_FULL_RETEST_LSV/24/report/savednotes'
    
    info = p.get_content_from_url(u1)
    
    f = open('C:\\Temp\\lch222.txt', 'w')
    f.write(info)
    f.close()
    print 'done'
        
        
        
        
        
        
        
        
        
        
        