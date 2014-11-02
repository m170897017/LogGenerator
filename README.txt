TIPS:
1. DO NOT operate on feature branch which you don't have authority.
2. This tool will combine all the test reports in the feature you select and compare with LSV branch. A final report will be generated in final_report folder.
3. You can edit the final report as you like, BUT then DO NOT forget to copy and save it to another file before you close it. HTML won't save it for you.
4. Click Run.py to start.
5. Make sure there is report in any build(your frature or LSV) you select on Jenkins.


Release note:
2014.9.24/1.2: 
try to get final report from both saved and savednotes to avoid re-generating reports
lose comparison standard, treat failed TCs without TR comments as the same
Only create final report in re-test path, since Jenkins will automatically combine it with first run result
2014.9.15/1.1:  fix UnicodeDecodeError, add .decode('utf-8')
2014.8.29/1.0:  First Version



test111112

