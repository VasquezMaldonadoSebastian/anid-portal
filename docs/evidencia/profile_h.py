import pandas as pd, numpy as np, sys, io, json, collections, re, unicodedata
pd.set_option('display.width', 200)
base = 'C:/Users/sebas/AppData/Local/hermes/cache/scratch/anid-gh/'
out = open('C:/Users/sebas/AppData/Local/hermes/cache/scratch/anid-gh/profile_historico.txt','w',encoding='utf-8')
def P(*a):
    s=' '.join(str(x) for x in a)
    print(s); out.write(s+'\n')

h = pd.read_csv(base+'Historico-de-Proyectos-Adjudicados/BDH_HISTORICA.csv', dtype=str, keep_default_na=False, sep=None, engine='python')
P('=== BDH_HISTORICA.csv ===')
P('shape:', h.shape)
P('cols:', list(h.columns))
P('encoding ok, empty-string counts per col:')
for c in h.columns:
    blank = (h[c].str.strip()=='').sum()
    P('  %-28s blank=%-7d distinct=%d' % (c, blank, h[c].nunique()))
out.close()
