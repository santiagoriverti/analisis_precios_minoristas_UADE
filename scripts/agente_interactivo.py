#!/usr/bin/env python3
"""Interfaz de chat interactiva con el orquestador multi-agente ICM-UADE.

Requiere: ANTHROPIC_API_KEY en variables de entorno.

Uso:
    python scripts/agente_interactivo.py
    python scripts/agente_interactivo.py --tarea "Procesá el semestre 2026A y generá el mapa"
"""
import argparse
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


def main():
    parser = argparse.ArgumentParser(description="Agente interactivo ICM-UADE")
    parser.add_argument("--tarea", help="Tarea a ejecutar (modo no interactivo)")
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("⚠ Configurar ANTHROPIC_API_KEY en el entorno:")
        print("  Windows: $env:ANTHROPIC_API_KEY = 'sk-ant-...'")
        print("  Linux/Mac: export ANTHROPIC_API_KEY='sk-ant-...'")
        sys.exit(1)

    try:
        from sepa.agents.orchestrator import SEPAOrchestrator
    except ImportError as e:
        print(f"Error importando: {e}")
        print("Asegurarse de instalar: pip install anthropic")
        sys.exit(1)

    agent = SEPAOrchestrator()
    print("=" * 60)
    print("  Agente ICM-UADE — Sistema de Análisis de Precios SEPA")
    print("  INECO — Universidad Argentina de la Empresa")
    print("=" * 60)
    print("Escribí 'salir' para terminar | 'reset' para limpiar historial\n")

    if args.tarea:
        print(f"Tarea: {args.tarea}\n")
        response = agent.chat(args.tarea)
        print(f"\nRespuesta:\n{response}")
        return

    # Modo interactivo
    while True:
        try:
            user_input = input("\nVos: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nChau!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("salir", "exit", "quit"):
            print("Chau!")
            break
        if user_input.lower() == "reset":
            agent.reset()
            print("Historial limpiado.")
            continue
        if user_input.lower() == "estado":
            summary = agent.memory.summary()
            import json
            print(json.dumps(summary, indent=2, ensure_ascii=False))
            continue

        print("\nAgente: ", end="", flush=True)
        response = agent.chat(user_input)
        print(response)


if __name__ == "__main__":
    main()
