# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt

def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)

def plot_parameter_effect():
    fig, host = plt.subplots(1,2,figsize=(16,5))
    fig.subplots_adjust(right=0.85,bottom=0.15,wspace=0.6)
    for index, title in ((0,'Weibo'),(1,'Yelp')):
        host[index].set_title(title,fontdict={'fontweight':'semibold'})
        par1 = host[index].twinx()
        par2 = host[index].twinx()
        par2.spines["right"].set_position(("axes", 1.2))
        make_patch_spines_invisible(par2)
        par2.spines["right"].set_visible(True)
        if not index:
            x = [0.2, 0.4, 0.6, 0.8, 1.0, 2.0, 4.0, 8.0, 20.0]
            y1 = [3759.37, 2697.21, 2357.94, 2468.87, 2630.36, 3498.75, 4451.54, 5102.42, 5432.86]
            y2 = [1.7893, 1.3318, 1.1998, 1.2327, 1.2620, 1.3436, 1.4141, 1.4484, 1.4950]
            y3 = [1.3089, 1.6275, 1.7494, 1.7392, 1.7302, 1.7136, 1.6817, 1.6338, 1.5771]
        else:
            x = [0.2, 0.4, 0.6, 0.8, 1.0, 2.0, 4.0, 8.0, 20.0]
            y1 = [4378.06, 3042.49, 2388.75, 2021.72, 2347.08, 3312.15, 3737.55, 3779.86, 3810.08]
            y2 = [2.3748, 1.4553, 0.9555, 0.6608, 0.7233, 0.9458, 1.1261, 1.2636, 1.3113]
            y3 = [0.6605, 1.4963, 1.9730, 2.2852, 2.2589, 2.1678, 2.1212, 2.1128, 2.1060]
        # p1, = host[index].semilogx(x, y1, "k^-", markeredgecolor='k', markerfacecolor='none', label="$Perplexity$")
        # p2, = par1.semilogx(x, y2, "b^-", markeredgecolor='b', markerfacecolor='none', label="$Entropy_{topic}$")
        # p3, = par2.semilogx(x, y3, "g^-", markeredgecolor='g', markerfacecolor='none', label="$KL-divergence$")
        p1, = host[index].semilogx(x, y1, "k*-", markeredgecolor='k', markerfacecolor='none', label="$Perplexity$")
        p2, = par1.semilogx(x, y2, "ko-", markeredgecolor='k', markerfacecolor='none', label="$Entropy_{topic}$")
        p3, = par2.semilogx(x, y3, "k^-", markeredgecolor='k', markerfacecolor='none', label="$KL-divergence$")
        host[index].set_xlim(0, 25)
        if not index:
            host[index].set_ylim(2000, 6000)
            par1.set_ylim(1.0, 2.0)
            par2.set_ylim(1.0, 2.0)
            host[index].plot([0.6,0.6],[2000, 6000],'k--')
        else:
            host[index].set_ylim(1500, 6000)
            par1.set_ylim(0.0, 3.0)
            par2.set_ylim(0.0, 3.0)
            host[index].plot([0.8,0.8],[1500, 6000],'k--')
        host[index].set_xticks([0.2,0.6,1.0,10.0])
        host[index].set_xticklabels(["0.2","0.6","1.0","10.0"])
        host[index].set_xlabel("$Local-global$ $weight$ $ratio$ $\lambda$")
        host[index].set_ylabel("$Perplexity$")
        par1.set_ylabel("$Topic$ $entropy$")
        par2.set_ylabel("$KL-divergence$")
        host[index].yaxis.label.set_color(p1.get_color())
        par1.yaxis.label.set_color(p2.get_color())
        par2.yaxis.label.set_color(p3.get_color())
        tkw = dict(size=4, width=1.5)
        host[index].tick_params(axis='y', colors=p1.get_color(), **tkw)
        par1.tick_params(axis='y', colors=p2.get_color(), **tkw)
        par2.tick_params(axis='y', colors=p3.get_color(), **tkw)
        host[index].tick_params(axis='x', **tkw)
        lines = [p1, p2, p3]
        host[index].legend(lines, [l.get_label() for l in lines], loc=4, fontsize=13)
    plt.show()
    # plt.savefig('../_latex/_plots/parameter_effect.eps', format='eps', dpi=1000)
    # for postfix in ('eps','png'):
    #     plt.savefig('../figure/{0}/01.{0}'.format(postfix))


if __name__ == '__main__':
    plot_parameter_effect()

