import os
import sys
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model.feature_extraction import org_extractor
from model.feature_extraction import law_extractor
from model.feature_extraction import time_extractor
from model.feature_extraction import article_extractor


def testpipe():

    f = open('test_pack/zahra.json', 'r+', encoding='utf-8')
    res = open('test_pack/result.txt', 'w+', encoding='utf-8')
    res.flush()
    testcases = json.load(f)

    passed, o, l, d, s = 0, 0, 0, 0, 0
    total = len(testcases)

    for i, testcase in enumerate(testcases):
        
        artext = article_extractor.article_extractor(testcase['input'])
        art = artext.result

        datext = time_extractor.time_extractor(testcase['input'])
        date = datext.result
        
        orgext = org_extractor.org_extractor(testcase['input'])
        org = orgext.find_org()

        lawext = law_extractor.LawExtractor()
        law = lawext.extract(testcase['input'])

        res.write(f'======== TEST {i+1:02d} ========\n')
        res.write(f'INPUT_TEXT: {testcase["input"]}\n')

        # statute reference / article
        res.write('\nARTICLE:\n')

        if art == testcase['output']['Statute reference']:
            res.write(f'PASSED ===> article: {art}')
            s += 1
        
        else:
            res.write(f'FAILED ===> expected {testcase["output"]["Statute reference"]}, returned {art} \n')


        # date / time
        res.write('\nDATE:\n')
        if date == testcase['output']['Date']:
            res.write(f'PASSED ===> date: {date}\n')
            s += 1
        
        else:
            res.write(f'FAILED ===> expected {testcase["output"]["Date"]}, returned {date} \n')


        # defined terms / orgaization
        res.write('\nDEFINED TERMS:\n')
        if sorted(org) == sorted(testcase['output']['Defined terms']):
            res.write(f'PASSED ===> org: {org}\n')
            o += 1
        
        else:
            res.write(f'FAILED ===> expected {testcase["output"]["Defined terms"]}, returned {org} \n')


        # law
        res.write('\nLAW:\n')
        if law == testcase['output']['law']:
            res.write(f'PASSED ===> law: {law}')
            l += 1
        
        else:
            res.write(f'FAILED ===> expected {testcase["output"]["law"]}, returned {law} \n')

        res.write('\n\n')

    res.write('\n================================\nSTATS:\n')
    res.write(f'TOTAL PASSED: {passed}/{total}\nSTATUTE REFERENCE: {s}/{total}\ndate: {d}/{total}\nDEFINED TERMS: {o}/{total}\nLAW: {l}/{total}')

testpipe()