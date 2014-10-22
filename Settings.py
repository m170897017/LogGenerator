#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Jun 19, 2014

@author: eccglln

ATTENTION:
1. Use %s instead of %d


'''
# Jenkins server domain
DOMAIN = 'https://sasn-jenkins-pc.mo.sw.ericsson.se/'

# URL for log in 
URL_LOG_IN = DOMAIN + 'login?from=%2F'

# URL for PL_SASN_PROGRAM
URL_PL_SASN_PROGRAM = DOMAIN + 'view/PL_SASN_PROGRAM/'

# URL for LSV programs
URL_LSV_PROGRAM = DOMAIN + 'view/LSV/'


# URL to show final report
FINAL_REPORT_PATH = DOMAIN + 'view/PL_SASN_PROGRAM/view/%s/job/PL_SCOPE_FT_FULL_RETEST_%s/%s/report/saved'

# URL to first test report
FIRST_TEST_REPORT_PATH = DOMAIN + 'view/PL_SASN_PROGRAM/view/%s/job/PL_SCOPE_FT_FULL_%s/%s/report/saved'

# URL to show LSV final report
LSV_FINAL_REPORT_PATH = DOMAIN + 'view/LSV/job/PL_SCOPE_FT_FULL_RETEST_LSV/%s/report/savednotes'


# create final report for feature branch
CREATE_FINAL_REPORT_PATH = DOMAIN + 'view/PL_SASN_PROGRAM/view/%s/job/PL_SCOPE_FT_FULL_RETEST_%s/%s/report/createReport'

# URL to saved report
URL_SAVED_REPORT = DOMAIN + 'view/PL_SASN_PROGRAM/view/%s/job/PL_SCOPE_FT_FULL_RETEST_%s/%s/report/saved'

# template for final report
TEMPLATE_PATH = 'final_report_template.html'

# where to put final report
FINAL_PATH = 'final_report\\'

# test result template for each TS
RESULT_PATH = 'test_result_template.html'

