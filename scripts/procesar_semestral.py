#!/usr/bin/env python3
"""CLI: Procesar un semestre del SEPA y generar serie temporal de canasta.

Uso:
    python scripts/procesar_semestral.py 2026A
    python scripts/procesar_semestral.py 2025B --source /ruta/al/zip
    python scripts/procesar_semestral.py --todos    # procesa todos los ZIPs en data/input/semestrales/
"""
import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from sepa.agents.orchestrator import _run_semester
from sepa.agents.memory import MemoryManager
from sepa.config.settings import INPUT_DIR


def main():
    parser = argparse.ArgumentParser(description="Procesa un semestre SEPA")
    parser.add_argument("semestre", nargs="?", help="Ej: 2026A, 2025B")
    parser.add_argument("--source", help="Ruta al ZIP o directorio (opcional)")
    parser.add_argument("--todos", action="store_true", help="Procesar todos los ZIPs semestrales disponibles")
    args = parser.parse_args()

    mem = MemoryManager()

    if args.todos:
        zips = sorted((INPUT_DIR / "semestrales").glob("*.zip"))
        if not zips:
            print(f"No hay ZIPs en {INPUT_DIR / 'semestrales'}")
            sys.exit(1)
        for z in zips:
            sem = z.stem
            print(f"\n{'='*50}\nProcesando semestre: {sem}")
            result = _run_semester(sem, str(z))
            if result.get("status") == "ok":
                print(f"✓ {sem}: {result['n_sucursales']:,} sucursales, meses: {result['meses']}")
            else:
                print(f"✗ Error en {sem}: {result.get('error')}")
    elif args.semestre:
        print(f"Procesando semestre: {args.semestre}")
        result = _run_semester(args.semestre, args.source)
        if result.get("status") == "ok":
            print(f"✓ Completado: {result}")
        else:
            print(f"✗ Error: {result.get('error')}")
            sys.exit(1)
    else:
        # Mostrar semestres ya procesados
        completados = mem.list_completed_periods("semester")
        pendientes_zips = sorted((INPUT_DIR / "semestrales").glob("*.zip")) if (INPUT_DIR / "semestrales").exists() else []
        print(f"Semestres procesados: {completados or 'ninguno'}")
        print(f"ZIPs disponibles: {[z.stem for z in pendientes_zips] or 'ninguno'}")
        print("\nUso: python scripts/procesar_semestral.py 2026A")


if __name__ == "__main__":
    main()
