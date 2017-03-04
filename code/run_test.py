# -*- coding: utf-8 -*-

import re
import sys
import json
import math
import random
import string
import fileinput
from _nlp.util import _id2name, _posdict, _worddict, _stopdict
from models.lda import LDASampler
from models.ldaLocal import LDALocalSampler
from models.ldaLocalGlobal import LDALocalGlobalSampler


def run_tfidf(num_clusters=20, num_displayed=10):
    import numpy as np
    from sklearn import feature_extraction
    from sklearn.feature_extraction.text import TfidfTransformer
    from sklearn.feature_extraction.text import CountVectorizer
    _index, _docs, _freqs, _dicts = 0, [], {}, {}
    for _name, _list in _location_dict.iteritems():
        if len(_list) >= LOCATION_THRES:
            _list = [_entry['_words'] for _entry in sorted(_list, 
                        key=lambda _en:_en['_len'], reverse=True)[:REVIEW_LIMIT]]
            for _doc in _list:
                _docs.append(' '.join(_doc))
                _freqs[_name] = _freqs.get(_name,{})
                _dicts[_name] = _dicts.get(_name,[]) + [_index]
                for _word in _doc:
                    _word = _word.decode('utf-8')
                    _freqs[_name][_word] = _freqs[_name].get(_word,0)+1
                _index += 1
    print len(_dicts)
    transformer, vectorizer = TfidfTransformer(), CountVectorizer()
    tfidf = transformer.fit_transform(vectorizer.fit_transform(_docs))
    _words, _weights = vectorizer.get_feature_names(), tfidf.toarray()
    print 'word vector length:', len(_weights)
    word_vector = []
    for _i, (_name, _list) in enumerate(_dicts.iteritems()):
        _weight = np.array([_weights[_ele] for _ele in _list]).sum(axis=0)
        word_vector.append(_weight)
        _keywords = [u'{},{}'.format(_item['_word'],_freqs[_name].get(_item['_word'],0))
                        for _item in sorted([{'_word':_word,'_value':_value} 
                                                for (_word,_value) in zip(_words,_weight)], 
                                            key=lambda _entry:_entry['_value'], reverse=True)]
        # show location keywords
        print _i, _name, '\t'.join(_keywords[:num_displayed])
    from sklearn.cluster import KMeans
    est = KMeans(n_clusters=num_clusters)
    est.fit(word_vector)
    for _cluster_center in est.cluster_centers_:
        _tuples = [(_value, _word) for _word, _value in enumerate(_cluster_center)]
        _tuples.sort(reverse=True)
        # show cluster keywords
        print '\t'.join([_words[_word] for (_value, _word) in _tuples[:num_displayed]])


def run_lda(model, num_iteration=101, save_step=20, num_topics=20, local_radio=0.6):
    _index, _docs, _conts = 0, [], []
    for _name, _list in _location_dict.iteritems():
        if len(_list) >= LOCATION_THRES:
            _list = [(_entry['_words'],_entry['_cont']) for _entry in 
                        sorted(_list, key=lambda _en:_en['_len'], reverse=True)[:REVIEW_LIMIT]]
            # print _index, _name, len(_list)
            _docs.extend([(_name,_doc[0]) for _doc in _list])
            _conts.extend([(_name,_doc[1]) for _doc in _list])
            _index += 1
    if model == 'LDASampler':
        lda = LDASampler(docs=_docs, num_topics=num_topics, alpha=0.5, beta=0.5)
    if model == 'LDALocalSampler':
        lda = LDALocalSampler(docs=_docs, num_topics=num_topics, alpha=0.5, beta=0.5)
    if model == 'LDALocalGlobalSampler':
        lda = LDALocalGlobalSampler(docs=_docs, conts=_conts, num_topics=num_topics, alpha=0.5, beta=0.5, gama=0.5, lamd=local_radio)
    for _index in range(num_iteration):
        print "iteration:", _index
        perplexity = lda.next()
        if _index % save_step == 0:
            with open('../_result/_ldaLocalGlobal/iteration_{}.txt'.format(str(_index).zfill(3)),'w') as _file:
                print "perplexity:", perplexity
                # save word topic probabilities
                _file.write('word topic probabilities:\n')
                tks = lda.topic_keys()
                for i, tk in enumerate(tks):
                    _file.write('{}\t{}\t{}\n'.format(i, lda.topic_weight(i), '\t'.join(tk)))
                # save local topic probabilities
                _file.write('local topic probabilities:\n')
                dks, entropy = lda.local_topics(), {'topic':0,'probs':{}}
                for l, dk in enumerate(dks):
                    _file.write('{}\n{}\n'.format(lda.locs[l], '\t'.join(['{}:{:.3}'.format(t, p) for (p, t) in dk])))
                    entropy['topic'] += -sum([p*math.log(p) for (p, t) in dk])
                    for (p, t) in dk:
                         entropy['probs'][t] = entropy['probs'].get(t,[])+[p]
                tks, KL = lda.topic_keys(return_prob=True), 0
                for _i, _prob1 in enumerate(tks):
                    for _j, _prob2 in enumerate(tks):
                        if _i != _j:
                            KL += -sum([_p1*math.log(_prob2[_k]/_p1) for _k, _p1 in enumerate(_prob1)])
                print "topic entropy:", entropy['topic']/len(dks)
                print "location entropy:", sum([sum([-p*math.log(p) for p in ps]) for t, ps in entropy['probs'].iteritems()])/len(entropy['probs'])
                print "topic KL-divergence:", KL/(len(tks)*(len(tks)-1))
                # save global topic probabilities
                # if model == 'LDALocalGlobalSampler':
                #     _file.write('global topic probabilities:\n')
                #     _file.write('{}\n'.format('\t'.join(['{}:{:.3}'.format(t, p) for (p, t) in lda.global_topics()])))
                #     lda.doc_locality(ratio=0, locations=["外滩"])


if __name__ == '__main__':

    ########## generate documents for weibo ##########
    if False:
        _location_dict, _weibo_count, _word_count = {}, 0, 0

        for line in fileinput.input('../data/data_weibo.txt'):
            _id, _, _, _, _cont, _seg = line.strip().split('\t')
            try:
                _words = []
                for _ele in _seg.split(' '):
                    _pos = _ele.split('/')[-1]
                    _word = '/'.join(_ele.split('/')[:-1])
                    if len(_word.decode('utf-8')) >= 2 and _pos in _posdict and \
                        not _word[0]=='@' and not _word in _stopdict and _word in _worddict:
                        _words.append(_word)
                if len(_words) >= 1:
                    _weibo_count += 1
                    _word_count += len(_cont)
                    _location_dict[_id2name[_id]] = _location_dict.get(_id2name[_id],[]) + \
                                                    [{'_words':_words,'_len':len(_words),'_cont':_cont}]
            except:
                continue
        fileinput.close()

        print "***  ***  ***  dataset statistics  ***  ***  ***"
        print "weibo count:", _weibo_count
        print "location count:", len(_location_dict)
        print "average word per weibo:", 1.*_word_count/_weibo_count

    ########## generate documents for yelp ##########
    if True:
        _location_dict, _yelp_count, _word_count = {}, 0, 0

        for line in fileinput.input('../data/data_yelp.txt'):
            line = json.loads(line)
            _id, _cont, _seg = line.get(u'business_id','').encode('utf-8'), line.get(u'text','').lower().encode('utf-8'), \
                               re.sub('[{0}]'.format(string.punctuation),'',line.get(u'text','').lower()).encode('utf-8')
            if fileinput.lineno()%10000 == 0:
                print fileinput.lineno()
            try:
                _words = []
                for _word in re.split(r'\s',_seg):
                    if len(_word.decode('utf-8')) >= 2 and not _word in _stopdict and _word in _worddict:
                        _words.append(_word)
                if len(_words) >= 1:
                    _yelp_count += 1
                    _word_count += len(_words)
                    _location_dict[_id2name[_id]] = _location_dict.get(_id2name[_id],[]) + \
                                                    [{'_words':_words,'_len':len(_words),'_cont':_cont}]
            except:
                continue
        fileinput.close()

        print "***  ***  ***  dataset statistics  ***  ***  ***"
        print "yelp count:", _yelp_count
        print "location count:", len(_location_dict)
        print "average word per yelp:", 1.*_word_count/_yelp_count

    LOCATION_THRES, REVIEW_LIMIT = 200, 50

    ########## run algorithm test ##########
    # run_tfidf()
    # run_lda(model='LDASampler',num_iteration=100)
    # run_lda(model='LDALocalSampler',num_iteration=101)
    run_lda(model='LDALocalGlobalSampler',num_iteration=201, local_radio=20.0)

