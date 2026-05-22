#!/usr/bin/env python3
"""CLI: Consolida todos los semestres procesados y genera comparativa IPC + gráficos.

Uso:
    python scripts/consolidar_series.py
    python scripts/consolidar_series.py --desde 2024-01
"""
import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from sepa.agents.orchestrator import _run_consolidation


def main():
    parser = argparse.ArgumentParser(description="Consolida series semestrales")
    parser.add_argument("--desde", default="2023-05", help="Mes de inicio (YYYY-MM, default: 2023-05)")
    args = parser.parse_args()

    print(f"Consolidando series desde {args.desde}...")
    result = _run_consolidation(from_month=args.desde)

    if result.get("status") == "ok":
        print(f"\n✓ Consolidación exitosa:")
        print(f"  Semestres: {result['semestres_procesados']}")
        print(f"  Meses válidos: {result['meses_validos']}")
        print(f"  Excel: {result['output_excel']}")
        for g in result.get("graficos", []):
            print(f"  Gráfico: {g}")
    else:
        print(f"✗ Error: {result.get('error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
