#!/usr/bin/env python3
"""Aggregate Sod log values into per-M markdown tables.

Each log file in output/sod/sod_logs is named

    sod_log_<mu>_<M>_400_21_<lambda>_<scheme>_<F>.log

and contains a single number. For each M in {2, 4, 6} this script writes a
markdown table (output/sod/sod_table_M<M>.md) with one column per (mu, F)
combination and one row per lambda value. Each cell holds the mean +/- the
standard deviation of the log values across all available <scheme> values.
"""

import re
import statistics
from collections import defaultdict
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent.parent / "output" / "sod" / "sod_logs"
OUT_DIR = LOG_DIR.parent
MIDDLE = "_400_21_"
NAME_RE = re.compile(r"^sod_log_(?P<mu>[^_]+)_(?P<M>[^_]+)" + MIDDLE +
                     r"(?P<lambda>[^_]+)_(?P<scheme>.+)_(?P<F>[^_]+)\.log$")


def to_float(s):
    return float(s)


def collect():
    # data[M][(mu, F)][lam] -> {scheme: value}
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    for path in sorted(LOG_DIR.glob("*.log")):
        m = NAME_RE.match(path.name)
        if not m:
            print(f"skipping unparseable name: {path.name}")
            continue
        mu, M, lam, scheme, F = (m["mu"], m["M"], m["lambda"],
                                 m["scheme"], m["F"])
        value = float(path.read_text().strip())
        data[M][(mu, F)][lam][scheme] = value
    return data


def fmt_cell(values):
    if not values:
        return "—"
    if len(values) == 1:
        return f"{values[0]:.4g}"
    mean = statistics.mean(values)
    std = statistics.pstdev(values)
    return f"{mean:.4g} ± {std:.2g}"


def write_table(M, cols_data):
    col_keys = sorted(cols_data, key=lambda k: (to_float(k[0]), to_float(k[1])))
    lam_keys = sorted(
        {lam for col in cols_data.values() for lam in col},
        key=to_float,
    )

    header = ["lambda"] + [f"mu={mu}, F={F}" for mu, F in col_keys]
    lines = [
        f"# Sod log values, M = {M}",
        "",
        "Mean ± population standard deviation across schemes "
        "(upwind, upwind_lw).",
        "",
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for lam in lam_keys:
        row = [lam]
        for key in col_keys:
            schemes = cols_data[key].get(lam, {})
            row.append(fmt_cell(list(schemes.values())))
        lines.append("| " + " | ".join(row) + " |")

    out = OUT_DIR / f"sod_table_M{M}.md"
    out.write_text("\n".join(lines) + "\n")
    print(f"wrote {out}")


def main():
    data = collect()
    for M in ("2", "4", "6"):
        if M not in data:
            print(f"no data for M={M}")
            continue
        write_table(M, data[M])


if __name__ == "__main__":
    main()
