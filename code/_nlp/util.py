# -*- coding: utf-8 -*-

import json
import fileinput

# genenrate location id name mapping
_id2name = {}
for line in fileinput.input('../data/weibo_place.txt'):
    _, _id, _name, _, _, _, _ = line.strip().split('\t')
    _id2name[_id] = _name
fileinput.close()
for line in fileinput.input('../data/yelp/yelp_academic_dataset_business.json'):
	line = json.loads(line)
	_id2name[line.get(u'business_id','').encode('utf-8')] = line.get(u'name','').encode('utf-8')

# generate selected words by pos and frequency
_posdict = {_pos:True for _pos in 
            ['n','nr','nr1','nr2','nrj','nrf','ns','nsf',\
             'nt','nz','nl','vn','an']}

_stopdict = {line.strip():True
                for line in fileinput.input('./_nlp/_stop.txt')}

_worddict = {line.strip().split('\t')[0]:True
                for line in fileinput.input('./_nlp/_freq.txt')
                    if int(line.strip().split('\t')[1]) >= 30}
