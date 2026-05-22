"""Gráficos de barras, series temporales y rankings de cadenas."""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
import numpy as np

log = logging.getLogger(__name__)

try:
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


def _require_mpl():
    if not HAS_MPL:
        raise ImportError("Instalar matplotlib: pip install matplotlib")


# ── Rankings ───────────────────────────────────────────────────────────────

def plot_chain_ranking(
    df_ranking: pd.DataFrame,
    output_path: Path,
    title: str = "Ranking de cadenas — Canasta ICM-UADE",
    highlight_n: int = 3,
) -> Path:
    """Gráfico horizontal de barras con ranking de cadenas por precio de canasta."""
    _require_mpl()
    df = df_ranking.sort_values("canasta_promedio", ascending=True).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(10, max(5, len(df) * 0.55)))
    colors = ["#2ecc71" if i < highlight_n else "#3498db" for i in range(len(df))]

    bars = ax.barh(df["cadena"], df["canasta_promedio"] / 1000, color=colors, edgecolor="white")

    for bar, val, n_suc in zip(bars, df["canasta_promedio"], df["n_sucursales"]):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                f"${val/1000:.0f}k  ({int(n_suc)} suc.)",
                va="center", fontsize=8.5, color="#333")

    if "vs_promedio_pct" in df.columns:
        avg_val = df["canasta_promedio"].mean() / 1000
        ax.axvline(avg_val, color="#e74c3c", linestyle="--", linewidth=1.2, label=f"Promedio: ${avg_val:.0f}k")
        ax.legend(fontsize=9)

    ax.set_xlabel("Canasta mensual (miles de ARS)", fontsize=10)
    ax.set_title(title, fontsize=13, fontweight="bold", pad=10)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}k"))
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    log.info("Ranking guardado: %s", output_path)
    return output_path


# ── Series temporales ──────────────────────────────────────────────────────

def plot_index_series(
    df_comparative: pd.DataFrame,
    output_path: Path,
    title: str = "Índices base 100 — Canasta SEPA vs. IPC INDEC",
    from_month: str | None = None,
) -> Path:
    """Gráfico de líneas: índice canasta vs. IPC general vs. IPC alimentos."""
    _require_mpl()
    df = df_comparative.copy()
    if from_month:
        df = df[df["mes"] >= from_month]

    fig, ax = plt.subplots(figsize=(14, 6))
    x = range(len(df))
    labels = df["mes"].tolist()

    if "indice" in df.columns:
        ax.plot(x, df["indice"], "b-o", markersize=3, linewidth=2, label="Canasta ICM-UADE")
        ax.annotate(f"{df['indice'].iloc[-1]:.1f}", xy=(x[-1], df["indice"].iloc[-1]),
                    xytext=(4, 0), textcoords="offset points", color="blue", fontsize=9)

    if "indice_ipc" in df.columns:
        ax.plot(x, df["indice_ipc"], "r--o", markersize=3, linewidth=1.5, label="IPC INDEC General")
        ax.annotate(f"{df['indice_ipc'].iloc[-1]:.1f}", xy=(x[-1], df["indice_ipc"].iloc[-1]),
                    xytext=(4, 0), textcoords="offset points", color="red", fontsize=9)

    if "indice_alimentos" in df.columns:
        ax.plot(x, df["indice_alimentos"], color="orange", linestyle=":", marker="o",
                markersize=3, linewidth=1.5, label="IPC INDEC Alimentos")

    step = max(1, len(labels) // 12)
    ax.set_xticks(x[::step])
    ax.set_xticklabels(labels[::step], rotation=45, ha="right", fontsize=8)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}"))
    ax.set_ylabel("Índice (base 100)", fontsize=10)
    ax.set_title(title, fontsize=13, fontweight="bold", pad=10)
    ax.legend(fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    return output_path


def plot_monthly_variations(
    df_comparative: pd.DataFrame,
    output_path: Path,
    title: str = "Variaciones mensuales — Canasta SEPA vs. IPC INDEC",
    from_month: str | None = None,
) -> Path:
    """Gráfico de barras agrupadas: variación mensual canasta vs. IPC."""
    _require_mpl()
    df = df_comparative.dropna(subset=["variacion_pct"]).copy()
    if from_month:
        df = df[df["mes"] >= from_month]

    x = np.arange(len(df))
    width = 0.35
    fig, ax = plt.subplots(figsize=(14, 6))

    bars1 = ax.bar(x - width / 2, df["variacion_pct"], width, label="Canasta ICM-UADE", color="#3498db")

    if "ipc_general_var" in df.columns:
        bars2 = ax.bar(x + width / 2, df["ipc_general_var"], width, label="IPC INDEC General", color="#e74c3c", alpha=0.8)

    for bar in bars1:
        h = bar.get_height()
        if not np.isnan(h):
            ax.text(bar.get_x() + bar.get_width() / 2, h + 0.3, f"{h:.1f}%",
                    ha="center", va="bottom", fontsize=7, color="#333")

    ax.set_xticks(x)
    ax.set_xticklabels(df["mes"].tolist(), rotation=45, ha="right", fontsize=8)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.set_ylabel("Variación mensual (%)", fontsize=10)
    ax.set_title(title, fontsize=13, fontweight="bold", pad=10)
    ax.legend(fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    ax.axhline(0, color="black", linewidth=0.5)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    return output_path


def plot_province_ranking(
    df_province: pd.DataFrame,
    output_path: Path,
    mes: str | None = None,
    title: str = "Canasta por provincia",
) -> Path:
    """Barras horizontales con valor de canasta por provincia."""
    _require_mpl()
    if mes is None:
        mes = df_province["mes"].max()
    df = df_province[df_province["mes"] == mes].sort_values("canasta_provincia").reset_index(drop=True)

    avg = df["canasta_provincia"].mean()
    colors = ["#2ecc71" if v <= avg else "#e74c3c" for v in df["canasta_provincia"]]

    fig, ax = plt.subplots(figsize=(10, max(6, len(df) * 0.5)))
    bars = ax.barh(df["provincia"], df["canasta_provincia"] / 1000, color=colors, edgecolor="white")

    for bar, val in zip(bars, df["canasta_provincia"]):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"${val/1000:.0f}k", va="center", fontsize=9)

    ax.axvline(avg / 1000, color="#333", linestyle="--", linewidth=1,
               label=f"Promedio: ${avg/1000:.0f}k")
    ax.legend(fontsize=9)
    ax.set_xlabel("Canasta mensual (miles ARS)", fontsize=10)
    ax.set_title(f"{title} — {mes}", fontsize=13, fontweight="bold", pad=10)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    return output_path
