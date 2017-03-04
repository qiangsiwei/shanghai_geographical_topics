# -*- coding: utf-8 -*-

import math
import random

class LDASampler(object):
    def __init__(self, docs=None, num_topics=None, alpha=0.1, beta=0.1):
        self.a, self.b, self.T = float(alpha), float(beta), int(num_topics)
        self.locs, self.docs, self.dicts = [], [], {}
        for _index, (_name, _doc) in enumerate(docs):
            self.dicts[_name] = self.dicts.get(_name,[])+[_index]
            self.docs.append(_doc)
        self.vocab = list(set(word for doc in self.docs for word in doc))
        self.D, self.W = len(self.docs), len(self.vocab)  
        self.to_int = {word: w for (w, word) in enumerate(self.vocab)}
        self.nt = [0] * self.T
        self.nd = [len(doc) for doc in self.docs]
        self.nwt = [[0] * self.T for _ in self.vocab]
        self.ndt = [[0] * self.T for _ in self.docs]
        self.assignments = []
        for d, doc in enumerate(self.docs):
            for i, word in enumerate(doc):
                w = self.to_int[word]
                t = random.randint(0, self.T-1)
                z = [d, i, w, t]
                self.assignments.append(z)
        for z in self.assignments:
            d, _, w, t = z
            self.nt[t] += 1
            self.nwt[w][t] += 1
            self.ndt[d][t] += 1

    def next(self):
        return math.exp(-sum([self.sample(z) for z in self.assignments])/sum(self.nt))

    def sample(self, z):
        d, _, w, old_t = z
        self.nt[old_t] -= 1
        self.ndt[d][old_t] -= 1
        self.nwt[w][old_t] -= 1
        unnorm_ps = [self.f(d, w, t) for t in range(self.T)]
        r = random.random() * sum(unnorm_ps)
        new_t = self.T - 1
        for i in range(self.T):
            r = r - unnorm_ps[i]
            if r < 0:
                new_t = i
                break
        _properbility = math.log(self.f(d, w, new_t))
        z[3] = new_t
        self.nt[new_t] += 1
        self.ndt[d][new_t] += 1
        self.nwt[w][new_t] += 1
        return _properbility

    def f(self, d, w, t):
        return (self.nwt[w][t] + self.b) / (self.nt[t] + self.W * self.b) * \
               (self.ndt[d][t] + self.a) / (self.nd[d] + self.T * self.a)
    
    def pw_z(self, w, t): 
        return (self.nwt[w][t] + self.b) / (self.nt[t] + self.W * self.b)
    
    def pz_d(self, d, t): 
        return (self.ndt[d][t] + self.a) / (self.nd[d] + self.T * self.a)
    
    def estimate_phi(self):
        return [[self.pw_z(w, t) for w in range(self.W)] for t in range(self.T)]
    
    def estimate_theta(self):
        return [[self.pz_d(d, t) for t in range(self.T)] for d in range(self.D)]
    
    def topic_weight(self, t):
        return self.nt[t]

    def topic_keys(self, return_prob=False, num_displayed=10):
        phi, tks = self.estimate_phi(), []
        for w_ps in phi:
            if return_prob:
                tks.append([p for p in w_ps])
            else:
                tuples = [(p, self.vocab[i]) for i, p in enumerate(w_ps)]
                tuples.sort(reverse=True)
                tks.append([word for (p, word) in tuples[:num_displayed]])
        return tks
    
    def local_topics(self):
        theta, lks = self.estimate_theta(), []
        dks = [[p for p in t_ps] for t_ps in theta]
        for _name, _list in self.dicts.iteritems():
            self.locs.append(_name)
            _tuples = [0] * len(dks[0])
            for _doc in _list:
                _tuples = [_x + _y for _x, _y in zip(_tuples, dks[_doc])]
            _tuples = [(p/len(_list), i) for i, p in enumerate(_tuples)]
            _tuples.sort(reverse=True)
            lks.append(_tuples)
        return lks
