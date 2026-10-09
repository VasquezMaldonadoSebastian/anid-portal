# anid portal

## 1. Metadatos del proyecto

| Campo | Valor |
|-------|-------|
| **Nombre** | anid portal |
| **Versión** | 0.1.0 |
| **Stack** | <lenguaje + versiones + libs clave> |
| **Repositorio** | `<A:\Repositorio Proyectos\anid-portal>` |
| **Dependencias** | ver `requirements.txt` |
| **Inicio rápido** | `bash scripts/run.sh` |
| **Modo instalado** | <si aplica> |

## 2. Contexto de dominio

### ¿Qué es?

<1 párrafo: qué problema resuelve y para quién.>

### Reglas de negocio

| Regla | Descripción |
|-------|-------------|
| <regla> | <descripción> |

### Glosario

| Término | Definición |
|---------|------------|
| <término> | <definición> |

## 3. Arquitectura del sistema

```text
<diagrama ASCII: componentes y flujo de datos>
```

### Árbol de directorios del proyecto

```text
anid-portal\
├── README.md
├── AGENTS.md                  ← este archivo (arquitectura + reglas)
├── MEMORIA.md                 ← estado vivo del proyecto
├── pyproject.toml
├── requirements.txt
├── config/                    ← default.yaml (trackeado) + local.yaml (ignorado)
├── src/                       ← código
├── tests/                     ← tests
├── scripts/                   ← setup.sh / run.sh
├── docs/                      ← modulos.md y planes
├── templates/                 ← plantillas de contenido
├── assets/                    ← recursos
└── logs/                      ← salida (gitignored)
```

### Datos vs código

<Dónde viven los datos reales (vault, Drive, BD) y dónde el código.>

## 4. Convenciones y estándares

- **Idioma:** español en documentación y entregables; inglés en código e identificadores.
- **Tests:** <requisito mínimo — todo módulo con tests; validators con test pass y fail>.
- **Errores:** <política: no silenciar; log + mensaje claro>.
- **Logging:** <niveles y destino>.
- **Nombres de archivo:** kebab-case, sin tildes, ñ ni espacios.

## 5. Roles / personas

### Rol 1 — Líder 🧭 · trigger: `@lider <acción>`
- **Expertise:** alcance, priorización, decisiones de arquitectura.
- **Responsabilidades:** descompone, aprueba planes, valida entregables.
- **Límites:** no implementa código de producción. **Excepciones:** puede escribir el plan y los stubs.
- **Ejemplo:** `@lider descompón <feature> en tareas de 2-5 min` → tabla de tareas con paths exactos.

### Rol 2 — Implementador 🔧 · trigger: `@implementar <tarea>`
- **Expertise:** <stack>.
- **Responsabilidades:** ejecuta la tarea, corre tests, reporta output real.
- **Límites:** no cambia el alcance ni el plan. **Excepciones:** puede proponer cambios al plan si hay bloqueo.
- **Ejemplo:** `@implementar tarea 3` → diff + salida de tests.

### Rol 3 — Revisor 🔍 · trigger: `@revisar <entregable>`
- **Expertise:** compliance vs spec, calidad, seguridad.
- **Responsabilidades:** emite informe con severidad (Critical/Important/Minor).
- **Límites:** no modifica archivos; **solo informe al usuario** en auditorías.
- **Ejemplo:** `@revisar src/` → lista de hallazgos con archivo y línea.

### Matriz de colaboración (C = frecuente, I = ocasional)

| ↓ habla con → | Líder | Implementador | Revisor |
|---------------|-------|---------------|---------|
| **Líder** | — | C | I |
| **Implementador** | I | — | C |
| **Revisor** | I | I | — |

## 6. Flujos de trabajo

### Feature
1. `@lider` descompone en tareas de 2-5 min (path exacto, comando, salida esperada).
2. Usuario aprueba el plan → se guarda en `docs/plans/`.
3. `@implementar` ejecuta tarea por tarea con test en rojo → verde.
4. `@revisar` valida spec y calidad.
5. Documentar (`MEMORIA.md`, nota de sesión).

**Checklist de aprobación:** plan aprobado por el usuario · tests PASS · revisión PASS · documentación actualizada.

### Hotfix / debugging
1. Reproducir el fallo con evidencia (log, comando, input mínimo).
2. Snapshot en `LINEA-BASE.md` si el fix toca configuración o datos.
3. Fix mínimo + test de regresión.
4. `@revisar` confirma que el fallo no reaparece.

**Checklist de aprobación:** fallo reproducido · test de regresión agregado · revisión PASS.

### Optimización
1. Medir línea base (tiempo, tokens, costo).
2. Cambio acotado, una variable a la vez.
3. Volver a medir y comparar contra la línea base.

**Checklist de aprobación:** métrica antes/después con números reales.

## 7. Referencias y recursos

- **Docs externas:** <enlaces>
- **Comandos frecuentes (probados):**
  ```bash
  bash scripts/setup.sh
  bash scripts/run.sh
  python -m pytest tests/ -q
  ```
- **Troubleshooting:**

| Problema | Causa | Fix |
|----------|-------|-----|
| <problema> | <causa> | <fix> |

## 8. Evolución y mantenimiento

- **Changelog:** ver `MEMORIA.md`.
- **Responsable de este archivo:** <usuario/agente>.
- **Cadencia de revisión:** trimestral, o al cerrar cada fase mayor.
- **Regla:** el detalle de implementación va en `docs/modulos.md`, no aquí.
