#!/usr/bin/env python3
"""Actualiza el manifest de IDs de archivos Drive — correr una vez por mes.

Autentica con Google Drive, lista los archivos en las carpetas de SEPA,
y actualiza data/drive_manifest.json con los IDs de los nuevos meses.

Uso:
    python scripts/actualizar_manifest.py
    python scripts/actualizar_manifest.py --mes 2026-05   # solo ese mes

Después de correrlo, hacer commit del manifest actualizado:
    git add data/drive_manifest.json
    git commit -m "manifest: agregar YYYY-MM"
    git push

Requerimientos:
    pip install google-auth google-auth-oauthlib google-api-python-client
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = PROJECT_ROOT / "data" / "drive_manifest.json"

FOLDER_IDS = {
    "historico_2018_2023": "13GONeBs5lQCSUdBioHYk-8GhfDtIyliD",
    "reciente_2024_hoy":   "1GNs9SrZ4BIoBsviBVWYYqRcsj4dwPF-I",
}

# Patrón de nombre de archivo SEPA
# Ejemplo: 042026_pais_parte1COMPLETO.csv.gz
PATRON_SEPA = re.compile(r"^(\d{2})(\d{4})_pais_parte(\d)COMPLETO\.csv\.gz$")


def autenticar_drive():
    """Autentica con Google Drive y retorna el servicio."""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        # Intentar autenticación por defecto (útil en Colab o con gcloud)
        import google.auth
        credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/drive.readonly"]
        )
        return build("drive", "v3", credentials=credentials, cache_discovery=False)
    except Exception:
        pass

    try:
        # Autenticación interactiva (entorno local)
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
        flow = InstalledAppFlow.from_client_secrets_file(
            PROJECT_ROOT / "credentials_drive.json", SCOPES
        )
        creds = flow.run_local_server(port=0)
        return build("drive", "v3", credentials=creds, cache_discovery=False)
    except FileNotFoundError:
        print("ERROR: No se encontró credentials_drive.json")
        print("  1. Ir a console.cloud.google.com")
        print("  2. Crear credenciales OAuth 2.0 (tipo Desktop)")
        print("  3. Descargar y guardar como credentials_drive.json en la raíz del repo")
        sys.exit(1)


def listar_archivos_en_carpeta(drive, folder_id):
    """Lista todos los archivos en una carpeta (incluyendo subcarpetas)."""
    archivos = []
    page_token = None
    while True:
        resp = drive.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            fields="nextPageToken, files(id, name, size)",
            pageSize=1000,
            pageToken=page_token,
        ).execute()
        archivos.extend(resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return archivos


def parsear_mes_de_nombre(nombre: str) -> tuple[str, str] | None:
    """Extrae (mes_fmt, parte) de un nombre de archivo SEPA.

    Ejemplo: '042026_pais_parte1COMPLETO.csv.gz' → ('2026-04', '1')
    """
    m = PATRON_SEPA.match(nombre)
    if not m:
        return None
    mm, aaaa, parte = m.group(1), m.group(2), m.group(3)
    return f"{aaaa}-{mm}", parte


def main():
    parser = argparse.ArgumentParser(description="Actualiza drive_manifest.json")
    parser.add_argument("--mes", help="Actualizar solo este mes (YYYY-MM). Si omitís, actualiza todos.")
    parser.add_argument("--forzar", action="store_true", help="Sobreescribe IDs existentes")
    args = parser.parse_args()

    # Cargar manifest actual
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    meses = manifest.setdefault("meses", {})
    maestros = manifest.setdefault("maestros", {})

    print("Autenticando con Google Drive...")
    drive = autenticar_drive()
    print("✓ Autenticado\n")

    # Listar archivos de ambas carpetas
    todos_los_archivos = {}
    for nombre_folder, folder_id in FOLDER_IDS.items():
        print(f"Listando {nombre_folder}...")
        archivos = listar_archivos_en_carpeta(drive, folder_id)
        print(f"  {len(archivos)} archivos encontrados")
        for a in archivos:
            todos_los_archivos[a["name"]] = a

    # Buscar maestros
    nombres_maestros = {
        "Maestro de Productos Interno.xlsx": "productos_id",
        "maestro_sucursales_completo.xlsx":  "sucursales_id",
    }
    print("\nBuscando maestros...")
    for nombre, clave in nombres_maestros.items():
        if nombre in todos_los_archivos:
            file_id = todos_los_archivos[nombre]["id"]
            if maestros.get(clave, "COMPLETAR") == "COMPLETAR" or args.forzar:
                maestros[clave] = file_id
                print(f"  ✓ {nombre}: {file_id}")
            else:
                print(f"  (sin cambios) {nombre}")
        else:
            print(f"  ✗ No encontrado: {nombre}")

    # Procesar archivos SEPA
    print("\nBuscando archivos SEPA por mes...")
    meses_encontrados = {}
    for nombre, info in todos_los_archivos.items():
        resultado = parsear_mes_de_nombre(nombre)
        if resultado is None:
            continue
        mes_fmt, parte = resultado
        if args.mes and mes_fmt != args.mes:
            continue
        if mes_fmt not in meses_encontrados:
            meses_encontrados[mes_fmt] = {}
        meses_encontrados[mes_fmt][f"parte{parte}_id"] = info["id"]

    # Actualizar manifest
    nuevos = 0
    for mes_fmt in sorted(meses_encontrados.keys()):
        datos = meses_encontrados[mes_fmt]
        if mes_fmt not in meses:
            meses[mes_fmt] = {}

        actualizado = False
        for clave, file_id in datos.items():
            if meses[mes_fmt].get(clave, "COMPLETAR") == "COMPLETAR" or args.forzar:
                meses[mes_fmt][clave] = file_id
                actualizado = True

        if actualizado:
            nuevos += 1
            partes = list(datos.keys())
            print(f"  ✓ {mes_fmt}: {', '.join(partes)}")
        else:
            print(f"  (sin cambios) {mes_fmt}")

    # Guardar manifest actualizado
    manifest["_actualizado"] = datetime.now().strftime("%Y-%m-%d")
    manifest["meses"] = dict(sorted(meses.items()))

    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"\n✓ Manifest actualizado: {nuevos} meses nuevos/modificados")
    print(f"  Guardado en: {MANIFEST_PATH}")
    print("\nPróximo paso:")
    print("  git add data/drive_manifest.json")
    print(f"  git commit -m 'manifest: agregar {args.mes or 'todos los meses'}'")
    print("  git push")


if __name__ == "__main__":
    main()
