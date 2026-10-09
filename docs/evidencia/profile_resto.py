import os
from pathlib import Path
SALIDA = Path(__file__).resolve().parent
import pandas as pd, csv, io, os, re
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 300)
base = str(Path(os.environ.get("ANID_CRUDO") or (Path(__file__).resolve().parents[2] / "data" / "crudo")) / "")
out = open(SALIDA/'profile_resto.txt','w',encoding='utf-8')
def P(*a):
    s=' '.join(str(x) for x in a); print(s); out.write(s+'\n')

files = [
 ('CONSOLIDADO_INSTITUCIONES','Colaboracion_Institucional/CONSOLIDADO_INSTITUCIONES.csv'),
 ('SPI_INVESTIGADORES','Colaboracion_Institucional/SPI_INVESTIGADORES.csv'),
 ('POSTULACIONES_2016_2025','Postulaciones/POSTULACIONES_2016_2025.csv'),
 ('POSTULACIONES_MILENIO','Postulaciones/POSTULACIONES_MILENIO.csv'),
 ('BDH_BECAS','Becas/BDH_BECAS SCH.csv'),
 ('BDH_PROYECTOS_MILENIO','Historico-de-Proyectos-Adjudicados/BDH_PROYECTOS_MILENIO.csv'),
 ('PK_PROYECTOS','Palabras_claves/BD_Palabras_claves_Proyectos.csv'),
 ('PK_BECAS','Palabras_claves/BD_Palabras_claves_Becas.csv'),
]
KEYS = re.compile(r'REGION|MACROZONA|INSTITUCION|SUBDIRECCION|PROGRAMA|ESTADO|ROL|PAIS|SEXO|MONEDA|MONTO|AGNO|ANNO|ANIO|DISCIPLINA|AREA|BECA|TIPO|PALABRA|DESTINO|NIVEL|GRUPO|INSTRUMENTO|CODIGO', re.I)

dfs = {}
for name, rel in files:
    p = base+rel
    if not os.path.exists(p):
        P('### %s MISSING' % name); continue
    raw = open(p,'rb').read(4000)
    head = raw.decode('utf-8-sig', errors='replace').splitlines()[0]
    delim = ';' if head.count(';') > head.count(',') else ','
    enc = 'utf-8-sig'
    try:
        df = pd.read_csv(p, sep=delim, dtype=str, keep_default_na=False, encoding=enc, engine='python')
    except Exception as e:
        P('### %s parse fail (delim=%s): %s' % (name, delim, str(e)[:150]))
        # fallback sniff
        df = pd.read_csv(p, sep=None, dtype=str, keep_default_na=False, encoding='utf-8-sig', engine='python')
    dfs[name]=df
    P('\n' + '='*90)
    P('### %s   file=%s   delim=%r   rows=%d  cols=%d  size=%.1f MB' % (name, rel, delim, df.shape[0], df.shape[1], os.path.getsize(p)/1e6))
    P('cols:', list(df.columns))
    for c in df.columns:
        if KEYS.search(c):
            blank = (df[c].str.strip()=='').sum()
            nd = df[c].nunique()
            P('  -- %-32s blank=%-7d distinct=%-7d' % (c, blank, nd))
            if nd <= 30 and nd > 0:
                P('     ' + ' | '.join('%s(%d)' % (k, v) for k, v in df[c].value_counts().head(30).items()))
    # numeric-ish check for montos
    for c in df.columns:
        if re.search(r'MONTO|^N$|DURACION', c, re.I):
            s = df[c].str.replace('.','',regex=False).str.replace(',','.',regex=False)
            num = pd.to_numeric(s, errors='coerce')
            P('  NUM %-30s parsed=%-7d of %-7d  sum=%.4g  median=%.4g  max=%.4g' % (c, num.notna().sum(), len(df), num.sum(), num.median(), num.max()))

# Cruces
P('\n' + '='*90)
P('### CRUCES')
h = pd.read_csv(base+'Historico-de-Proyectos-Adjudicados/BDH_HISTORICA.csv', dtype=str, keep_default_na=False, sep=';', encoding='utf-8-sig')
h['anno']=pd.to_numeric(h['AGNO_FALLO'],errors='coerce')
if 'CONSOLIDADO_INSTITUCIONES' in dfs:
    ci = dfs['CONSOLIDADO_INSTITUCIONES']
    hc = set(h['CODIGO_PROYECTO']); cc=set(ci['CODIGO_PROYECTO'])
    P('historico codigos:', len(hc), '| colaboracion codigos:', len(cc), '| interseccion:', len(hc&cc))
    P('colaboracion codigos que NO estan en historico:', len(cc-hc))
    P('historico codigos que NO estan en colaboracion:', len(hc-cc))
    # por año
    h2 = h[h['anno']>=2016]
    P('historico >=2016: filas %d codigos %d ; de esos con colaboracion: %d' % (len(h2), h2['CODIGO_PROYECTO'].nunique(), len(set(h2['CODIGO_PROYECTO'])&cc)))
    P('colaboracion AGNO_FALLO:', ci['AGNO_FALLO'].value_counts().sort_index().to_dict())
    P('colaboracion filas por proyecto (top):', ci.groupby('CODIGO_PROYECTO').size().describe().to_dict())
    P('colaboracion ROLINSTITUCION:', ci['ROLINSTITUCION'].value_counts().to_dict())
    P('colaboracion PAISINSTITUCION distinct:', ci['PAISINSTITUCION'].nunique(), ci['PAISINSTITUCION'].value_counts().head(5).to_dict())
    P('colaboracion REGIONINSTITUCION:', ci['REGIONINSTITUCION'].value_counts().to_dict())
if 'POSTULACIONES_2016_2025' in dfs:
    po = dfs['POSTULACIONES_2016_2025']
    P('postulaciones codigos:', po['CODIGO DEL PROYECTO'].nunique() if 'CODIGO DEL PROYECTO' in po.columns else po.iloc[:,0].nunique())
out.close()
