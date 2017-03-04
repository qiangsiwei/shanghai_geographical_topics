# -*- coding: utf-8 -*-

import math
import random

class LDALocalGlobalSampler(object):
    def __init__(self, docs=None, conts=None, num_topics=None, alpha=0.5, beta=0.5, gama=0.2, lamd=1.0):
        self.a, self.b, self.c, self.d, self.T = float(alpha), float(beta), float(gama), float(lamd), int(num_topics)
        self.docs, self.conts = docs, conts
        self.locs = list(set(doc[0] for doc in self.docs))
        self.vocab = list(set(word for doc in self.docs for word in doc[1]))
        self.L, self.W = len(self.locs), len(self.vocab)
        self.to_id = {loc: i for (i, loc) in enumerate(self.locs)}
        self.to_int = {word: w for (w, word) in enumerate(self.vocab)}
        self.nt = [0] * self.T
        self.ndc = [[0] * 2 for _ in self.docs]
        self.ng, self.nl = 0, [0 for _ in self.locs]
        self.ngt, self.nlt = [0] * self.T, [[0] * self.T for _ in self.locs]
        self.nwt = [[0] * self.T for _ in self.vocab]
        self.assignments = []
        for _d, (_loc, _doc) in enumerate(self.docs):
            for _i, _word in enumerate(_doc):
                _l = self.to_id[_loc]
                _w = self.to_int[_word]
                _c = int(random.randint(0, max(1,self.d)) >= 1)
                _t = random.randint(0, self.T-1)
                _z = [_d, _l, _w, _c, _t]
                self.assignments.append(_z)
        for _z in self.assignments:
            _d, _l, _w, _c, _t = _z
            self.ndc[_d][_c] += 1
            if _c:
                self.nl[_l] += 1
                self.nlt[_l][_t] += 1
            else:
                self.ng += 1
                self.ngt[_t] += 1
            self.nt[_t] += 1
            self.nwt[_w][_t] += 1

    def next(self):
        return math.exp(-sum([self.sample(z) for z in self.assignments])/sum(self.nt))

    def sample(self, z):
        _d, _l, _w, _c_old, _t_old = z
        # restore
        self.ndc[_d][_c_old] -= 1
        if _c_old:
            self.nl[_l] -= 1
            self.nlt[_l][_t_old] -= 1
        else:
            self.ng -= 1
            self.ngt[_t_old] -= 1
        self.nt[_t_old] -= 1
        self.nwt[_w][_t_old] -= 1
        # sample
        unnorm_ps = [(0, t, self.h1(_w,t)*self.f(_d,0)) for t in range(self.T)] + \
                    [(1, t, self.h2(_l,_w,t)*self.f(_d,1)*self.d) for t in range(self.T)]
        r = random.random() * sum([_p[2] for _p in unnorm_ps])
        _c_new, _t_new = 1, self.T-1
        for i in range(2*self.T):
            r = r - unnorm_ps[i][2]
            if r < 0:
                _c_new, _t_new, _ = unnorm_ps[i]
                break
        # compute log properbility
        _properbility = math.log(self.h2(_l,_w,_t_new) if _c_new else self.h1(_w,_t_new))
        # update
        z[3], z[4] = _c_new, _t_new
        self.ndc[_d][_c_new] += 1
        if _c_new:
            self.nl[_l] += 1
            self.nlt[_l][_t_new] += 1
        else:
            self.ng += 1
            self.ngt[_t_new] += 1
        self.nt[_t_new] += 1
        self.nwt[_w][_t_new] += 1
        return _properbility

    def f(self, d, c): # sample for locality
        return self.ndc[d][c] + self.c

    def h1(self, w, t): # sample for global topic
        return (self.ngt[t] + self.a) / (self.ng + self.a * self.T) * \
               (self.nwt[w][t] + self.b) / (self.nt[t] + self.b * self.W)

    def h2(self, l, w, t): # sample for local topic
        return (self.nlt[l][t] + self.a) / (self.nl[l] + self.a * self.T) * \
               (self.nwt[w][t] + self.b) / (self.nt[t] + self.b * self.W)

    def pw_z(self, w, t):
        return (self.nwt[w][t] + self.b) / (self.nt[t] + self.b * self.W)

    def estimate_phi(self):
        return [[self.pw_z(w, t) for w in range(self.W)] for t in range(self.T)]

    def pz_d(self, l, t):
        return (self.nlt[l][t] + self.a) / (self.nl[l] + self.a * self.T)

    def estimate_theta(self):
        return [[self.pz_d(l, t) for t in range(self.T)] for l in range(self.L)]

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
        theta, dks = self.estimate_theta(), []
        for t_ps in theta:
            tuples = [(p, t) for t, p in enumerate(t_ps)]
            tuples.sort(reverse=True)
            dks.append(tuples)
        return dks

    def global_topics(self):
        tuples = [(p, t) for t, p in enumerate([
            (self.ngt[t] + self.a) / (sum(self.ngt) + self.a * self.T)
                for t in range(self.T)])]
        tuples.sort(reverse=True)
        return tuples

    def doc_locality(self, ratio, locations=[]):
        _dict = {}
        for z in self.assignments:
            _d, _l, _w, _c, _t = z
            _dict[_d] = _dict.get(_d,{'len':0,'glob':0,'local':0})
            _dict[_d]['len'] += 1
            _dict[_d]['glob'] += self.h1(_w,_t)
            _dict[_d]['local'] += self.h2(_l,_w,_t)
        _tuples = [(_v['local']/_v['len'],[_v['local']/_v['glob'], _d]) for _d, _v in _dict.iteritems()]
        _tuples.sort(reverse=True)
        for _index in xrange(int(len(_tuples)*ratio), int(len(_tuples)*ratio)+10**4):
            if self.conts[_tuples[_index][1][1]][0] in locations:
                print _tuples[_index], '\t'.join(self.conts[_tuples[_index][1][1]])

