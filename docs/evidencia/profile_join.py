import os
from pathlib import Path
SALIDA = Path(__file__).resolve().parent
import pandas as pd
base = str(Path(os.environ.get("ANID_CRUDO") or (Path(__file__).resolve().parents[2] / "data" / "crudo")) / "")
out=open(SALIDA/'profile_join.txt','w',encoding='utf-8')
def P(*a):
    s=' '.join(str(x) for x in a); print(s); out.write(s+'\n')
po=pd.read_csv(base+'Postulaciones/POSTULACIONES_2016_2025.csv',dtype=str,keep_default_na=False,sep=';',encoding='utf-8-sig')
h=pd.read_csv(base+'Historico-de-Proyectos-Adjudicados/BDH_HISTORICA.csv',dtype=str,keep_default_na=False,sep=';',encoding='utf-8-sig')
hc=set(h['CODIGO_PROYECTO'])
P('postulaciones codigos:', po['CODIGO_PROYECTO'].nunique(), '| historico codigos:', len(hc))
P('postulaciones por estado:')
for est, g in po.groupby('ESTADO_RESOLUCION_CONCURSO'):
    c=set(g['CODIGO_PROYECTO'])
    P('  %-16s filas=%-7d codigos=%-7d en historico: %-7d (%.1f%%)' % (est, len(g), len(c), len(c&hc), 100*len(c&hc)/max(len(c),1)))
P('')
P('postulaciones 2016-2025 ADJUDICADO con institucion recuperable via historico: %d de %d (%.1f%%)' % (
   len(set(po.loc[po['ESTADO_RESOLUCION_CONCURSO']=='ADJUDICADO','CODIGO_PROYECTO'])&hc),
   po.loc[po['ESTADO_RESOLUCION_CONCURSO']=='ADJUDICADO','CODIGO_PROYECTO'].nunique(),
   100*len(set(po.loc[po['ESTADO_RESOLUCION_CONCURSO']=='ADJUDICADO','CODIGO_PROYECTO'])&hc)/po.loc[po['ESTADO_RESOLUCION_CONCURSO']=='ADJUDICADO','CODIGO_PROYECTO'].nunique()))
P('')
P('NO ADJUDICADO: %d codigos sin institucion en ninguna base (no hay denominador por institucion)' % po.loc[po['ESTADO_RESOLUCION_CONCURSO']=='NO ADJUDICADO','CODIGO_PROYECTO'].nunique())
P('')
P('tasa de adjudicacion por REGION (factible):')
t=po.assign(adj=(po['ESTADO_RESOLUCION_CONCURSO']=='ADJUDICADO')).groupby('REGION_EJECUCION')['adj'].agg(n='count', adj='sum')
t['tasa_%']=(100*t['adj']/t['n']).round(1)
P(t.sort_values('n',ascending=False).to_string())
out.close()
