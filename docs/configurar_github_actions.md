# Configurar GitHub Actions — ICM-UADE

## Workflows disponibles

| Workflow | Cuándo corre | Para qué |
|----------|-------------|----------|
| `validar_manifest.yml` | Cada push a `drive_manifest.json` | Valida estructura y avisa meses sin IDs |
| `validar_codigo.yml` | Cada push a `src/` | Verifica imports y lógica crítica (EANs, barrios, cadenas) |
| `actualizar_manifest.yml` | El 1º de cada mes a las 9 AM | Actualiza automáticamente el manifest con el nuevo mes |
| `publicar_mapa.yml` | Cada push de HTML en `products/` | Publica el mapa en GitHub Pages |

---

## Setup: GitHub Pages (publicar el mapa online)

1. Ir a **Settings → Pages** en el repo de GitHub
2. En "Source", elegir **"GitHub Actions"**
3. La próxima vez que subas un HTML de mapa a `products/`, se publica automáticamente en:
   ```
   https://santiagoriverti.github.io/analisis_precios_minoristas_UADE/
   ```

---

## Setup: Actualización automática del manifest

Para que el workflow `actualizar_manifest.yml` pueda acceder a Google Drive sin intervención, necesitás una **cuenta de servicio de Google** (service account).

### Paso 1 — Crear la cuenta de servicio

1. Ir a [console.cloud.google.com](https://console.cloud.google.com)
2. Crear proyecto (o usar uno existente)
3. Habilitar la **Google Drive API**
4. Ir a **IAM → Cuentas de servicio → Crear**
5. Descargar el JSON de credenciales

### Paso 2 — Dar acceso a las carpetas de Drive

1. Abrir la carpeta de Drive de SEPA
2. Click en "Compartir"
3. Agregar el email de la cuenta de servicio (termina en `@*.iam.gserviceaccount.com`)
4. Dar permiso de **Solo lectura**

### Paso 3 — Agregar el secret a GitHub

1. Ir al repo → **Settings → Secrets and variables → Actions**
2. Crear secret llamado **`GOOGLE_SERVICE_ACCOUNT_KEY`**
3. Pegar el contenido completo del JSON de credenciales

### Paso 4 — Probar

Ir a **Actions → Actualizar manifest mensualmente → Run workflow** y verificar que funciona.

---

## Disparar manualmente la actualización del manifest

Desde GitHub → **Actions → "Actualizar manifest mensualmente" → Run workflow**:

- Sin parámetros: busca y agrega todos los meses nuevos
- Con `mes = 2026-05`: agrega solo ese mes

---

## Sin cuenta de servicio (alternativa manual)

Seguir el flujo descripto en el README:
```bash
python scripts/actualizar_manifest.py
git add data/drive_manifest.json
git commit -m "manifest: 2026-05"
git push
```

El workflow de validación (`validar_manifest.yml`) sigue funcionando sin la service account.
