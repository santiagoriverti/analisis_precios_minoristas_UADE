# Checklist para mañana — ICM-UADE

> Última actualización: 2026-05-22

## ✅ Estado actual del repositorio

- Código Python completo y sin bugs conocidos (`src/sepa/`)
- 5 notebooks funcionales (+ `MAPA_MES_COMPLETO.ipynb` para Colab)
- 4 GitHub Actions activos (CI, manifest, Pages, cron mensual)
- 10 skills instalados en `.claude/skills/` del proyecto
- Paper LaTeX en `overleaf/` con figuras de abril 2026
- **Todo pusheado y vigente en GitHub**

---

## 🔴 Prioridad 1 — Poblar el manifest (desbloquea el Colab autónomo)

```bash
# En el proyecto local:
python scripts/actualizar_manifest.py
git add data/drive_manifest.json
git commit -m "manifest: agregar todos los meses disponibles"
git push
```

Este paso hace que el notebook Colab funcione **sin ningún popup de autenticación**.  
Sin esto, pide login de Google cada vez.

---

## 🟡 Prioridad 2 — Activar GitHub Pages (publicar el mapa online)

1. Ir a: https://github.com/santiagoriverti/analisis_precios_minoristas_UADE/settings/pages
2. En "Source" → elegir **"GitHub Actions"**
3. La próxima vez que subas un HTML de mapa a `products/`, se publica en:  
   `https://santiagoriverti.github.io/analisis_precios_minoristas_UADE/`

---

## 🟡 Prioridad 3 — Configurar workflow mensual automático

Para que el manifest se actualice solo el 1° de cada mes:

1. Crear una cuenta de servicio de Google (ver `docs/configurar_github_actions.md`)
2. Ir a: https://github.com/santiagoriverti/analisis_precios_minoristas_UADE/settings/secrets/actions
3. Crear secret: `GOOGLE_SERVICE_ACCOUNT_KEY` (pegar el JSON completo)

---

## 🟢 Prioridad 4 — Correr el mapa de mayo 2026

Cuando salgan los datos de mayo:

```
# Opción 1: Colab (después de poblar el manifest)
https://colab.research.google.com/github/santiagoriverti/analisis_precios_minoristas_UADE/blob/main/notebooks/MAPA_MES_COMPLETO.ipynb

# Opción 2: Colab (antes del manifest, pide auth Google)
→ Mismo link, en la celda de config cambiar MES = '2026-05'
```

---

## 🟢 Prioridad 5 — Corregir el paper LaTeX

Ver `overleaf/README.md` para la lista de correcciones pendientes.  
Las 4 críticas son:
- Unificar período en Metodología → "marzo 2024 → abril 2026"
- Base 100 en gráficos → "marzo de 2024" (no 2023)
- Verificar variación interanual 25,7%
- Dispersión provincial → 12,1%

---

## Arranque rápido de cada sesión

```bash
# 1. Arrancar el worker de memoria persistente
npx claude-mem start
# → Dashboard: http://localhost:37777

# 2. (Primera vez) Ingestar el repo en claude-mem
/learn-codebase

# 3. Retomar donde dejamos
/gsd-resume-work
```

---

## Links útiles

| Recurso | URL |
|---------|-----|
| Repositorio | https://github.com/santiagoriverti/analisis_precios_minoristas_UADE |
| Colab (mapa) | https://colab.research.google.com/github/santiagoriverti/analisis_precios_minoristas_UADE/blob/main/notebooks/MAPA_MES_COMPLETO.ipynb |
| GitHub Actions | https://github.com/santiagoriverti/analisis_precios_minoristas_UADE/actions |
| GitHub Pages | https://santiagoriverti.github.io/analisis_precios_minoristas_UADE/ (activar primero) |
| Drive SEPA 2024+ | https://drive.google.com/drive/folders/1GNs9SrZ4BIoBsviBVWYYqRcsj4dwPF-I |
| Drive SEPA histórico | https://drive.google.com/drive/folders/13GONeBs5lQCSUdBioHYk-8GhfDtIyliD |
| Docs GitHub Actions | docs/configurar_github_actions.md |
