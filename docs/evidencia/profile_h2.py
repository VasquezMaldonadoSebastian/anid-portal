import pandas as pd, numpy as np, re, unicodedata
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 300)
base = 'C:/Users/sebas/AppData/Local/hermes/cache/scratch/anid-gh/'
out = open(base+'profile_historico2.txt','w',encoding='utf-8')
def P(*a):
    s=' '.join(str(x) for x in a); print(s); out.write(s+'\n')

h = pd.read_csv(base+'Historico-de-Proyectos-Adjudicados/BDH_HISTORICA.csv', dtype=str, keep_default_na=False, sep=';', encoding='utf-8-sig')
h['anno'] = pd.to_numeric(h['AGNO_FALLO'], errors='coerce')

P('=== MONEDA ===')
P(h['MONEDA'].value_counts(dropna=False).to_string())
P('\n=== MONTO_ADJUDICADO: parseo ===')
m = h['MONTO_ADJUDICADO'].str.replace('.','',regex=False).str.replace(',','.',regex=False)
h['monto'] = pd.to_numeric(m, errors='coerce')
P('vacios:', (h['MONTO_ADJUDICADO'].str.strip()=='').sum(), '| no parseables:', ((h['MONTO_ADJUDICADO'].str.strip()!='') & h['monto'].isna()).sum())
P('ejemplos no parseables:', h.loc[(h['MONTO_ADJUDICADO'].str.strip()!='') & h['monto'].isna(),'MONTO_ADJUDICADO'].head(5).tolist())
P('\n=== REGION_EJECUCION (todas) ===')
P(h['REGION_EJECUCION'].value_counts(dropna=False).to_string())
P('\n=== MACROZONA_MINCIENCIA ===')
P(h['MACROZONA_MINCIENCIA'].value_counts(dropna=False).to_string())
P('\n=== MONEDA x REGION_EJECUCION ===')
P(pd.crosstab(h['MONEDA'], h['REGION_EJECUCION']).to_string())
P('\n=== cobertura temporal ===')
P('AGNO_FALLO min/max:', h['anno'].min(), h['anno'].max())
bins = [0,1989,1999,2009,2015,2019,2025,2100]
labs = ['<=1989','1990-99','2000-09','2010-15','2016-19','2020-25','>2025']
h['decada'] = pd.cut(h['anno'], bins=bins, labels=labs)
P(pd.crosstab(h['decada'], h['MONEDA']).to_string())
P('\n=== SUBDIRECCION x decada ===')
P(pd.crosstab(h['SUBDIRECCION'], h['decada']).to_string())
P('\n=== PROGRAMA ===')
P(h['PROGRAMA'].value_counts().to_string())
P('\n=== TIPO_BENEFICIARIO ===')
P(h['TIPO_BENEFICIARIO'].value_counts().to_string())
P('\n=== cobertura region/monto por decada (% filas con dato) ===')
tmp = h.assign(reg_ok=~h['REGION_EJECUCION'].str.contains('SIN|NO INF|NO APLICA|EXTRANJERO|OTRA', case=False, na=False),
               monto_ok=h['monto'].notna())
P(tmp.groupby('decada', observed=True)[['reg_ok','monto_ok']].mean().round(3).to_string())
P('\n=== instituciones ===')
def norm(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii','ignore').decode().upper()
    s = re.sub(r'[^A-Z0-9 ]',' ', s)
    s = re.sub(r'\b(DE|DEL|LA|LAS|LOS|EL|Y|E)\b',' ', s)
    s = re.sub(r'\s+',' ', s).strip()
    return s
h['inst_norm'] = h['INSTITUCION_PRINCIPAL'].map(norm)
P('distinct crudo:', h['INSTITUCION_PRINCIPAL'].nunique(), '| normalizado:', h['inst_norm'].nunique())
P('\n=== top 30 instituciones (crudo) ===')
P(h['INSTITUCION_PRINCIPAL'].value_counts().head(30).to_string())
P('\n=== grupos que el normalizador fusiona (>=2 variantes), top 20 ===')
g = h.groupby('inst_norm')['INSTITUCION_PRINCIPAL'].nunique().sort_values(ascending=False)
n=0
for k,v in g.items():
    if v>1:
        n+=1
        if n<=20:
            P('-- %-45s %d variantes: %s' % (k, v, ' | '.join(h.loc[h.inst_norm==k,'INSTITUCION_PRINCIPAL'].value_counts().head(5).index.tolist())))
P('total grupos con >=2 variantes:', n)
P('\n=== RUT? no existe; revisar si institucion trae RUT embebido ===')
P(h['INSTITUCION_PRINCIPAL'].str.contains(r'\d{6,}', regex=True).sum())
P('\n=== montos por moneda ===')
P(h.groupby('MONEDA')['monto'].agg(['count','sum','median','max']).to_string())
P('\n=== regiones no reconocibles ===')
sosp = h[~h['REGION_EJECUCION'].str.contains('REGION|METROPOLITANA|NUBLE|ARICA|TARAPACA|ANTOFAGASTA|ATACAMA|COQUIMBO|VALPARAISO|OHIGGINS|MAULE|BIOBIO|ARAUCANIA|RIOS|MAGALLANES|AYSEN', case=False, na=False)]
P('filas:', len(sosp))
P(sosp['REGION_EJECUCION'].value_counts().head(20).to_string())
P('\n=== duplicados CODIGO_PROYECTO ===')
d = h[h.duplicated('CODIGO_PROYECTO', keep=False)]
P('filas con codigo repetido:', len(d), '| codigos:', d['CODIGO_PROYECTO'].nunique())
P(d[['CODIGO_PROYECTO','AGNO_FALLO','NOMBRE_CONCURSO','INSTITUCION_PRINCIPAL','MONTO_ADJUDICADO']].head(10).to_string())
P('\n=== ejemplos de codigo repetido con datos distintos vs iguales ===')
gg = d.groupby('CODIGO_PROYECTO').apply(lambda x: x.drop(columns=['N','inst_norm']).drop_duplicates().shape[0], include_groups=False)
P('codigos repetidos cuyo contenido difiere:', (gg>1).sum(), 'de', len(gg))
out.close()
