import os
from pathlib import Path
SALIDA = Path(__file__).resolve().parent
import pandas as pd
base = str(Path(os.environ.get("ANID_CRUDO") or (Path(__file__).resolve().parents[2] / "data" / "crudo")) / "")
out=open(SALIDA/'profile_join2.txt','w',encoding='utf-8')
def P(*a):
    s=' '.join(str(x) for x in a); print(s); out.write(s+'\n')
po=pd.read_csv(base+'Postulaciones/POSTULACIONES_2016_2025.csv',dtype=str,keep_default_na=False,sep=';',encoding='utf-8-sig')
h=pd.read_csv(base+'Historico-de-Proyectos-Adjudicados/BDH_HISTORICA.csv',dtype=str,keep_default_na=False,sep=';',encoding='utf-8-sig')
be=pd.read_csv(base+'Becas/BDH_BECAS SCH.csv',dtype=str,keep_default_na=False,sep=';',encoding='utf-8-sig')
hc=set(h['CODIGO_PROYECTO']); bc=set(be['CODIGO_BECA'])
adj=po[po['ESTADO_RESOLUCION_CONCURSO']=='ADJUDICADO']
adj=adj.assign(en_h=adj['CODIGO_PROYECTO'].isin(hc), en_b=adj['CODIGO_BECA'] if 'CODIGO_BECA' in adj.columns else adj['CODIGO_PROYECTO'].isin(bc))
P('ADJUDICADO por subdireccion: filas / codigos / en historico / en becas')
for sd,g in adj.groupby('SUBDIRECCION'):
    c=set(g['CODIGO_PROYECTO'])
    P('  %-36s filas=%-7d codigos=%-7d hist=%-7d (%.0f%%) becas=%-7d (%.0f%%)' % (sd,len(g),len(c),len(c&hc),100*len(c&hc)/len(c),len(c&bc),100*len(c&bc)/len(c)))
P('')
P('tasa adjudicacion SOLO proyectos (excluye CAPITAL HUMANO):')
pp=po[po['SUBDIRECCION']!='CAPITAL HUMANO']
t=pp.assign(adj=(pp['ESTADO_RESOLUCION_CONCURSO']=='ADJUDICADO')).groupby('REGION_EJECUCION')['adj'].agg(n='count',adj='sum')
t['tasa_%']=(100*t['adj']/t['n']).round(1)
P(t.sort_values('n',ascending=False).to_string())
P('')
P('global: postulaciones proyectos %d, adjudicadas %d (%.1f%%)' % (len(pp), int(t['adj'].sum()), 100*t['adj'].sum()/len(pp)))
P('global con becas: postulaciones %d, adjudicadas %d (%.1f%%)' % (len(po), int((po['ESTADO_RESOLUCION_CONCURSO']=='ADJUDICADO').sum()), 100*(po['ESTADO_RESOLUCION_CONCURSO']=='ADJUDICADO').mean()))
out.close()
