#!/usr/bin/env python3
"""Aggregate Couette log values into per-M markdown tables.

Each log file in output/couette/couette_logs is named

    couette_log_0.3_<M>_<nx>_16_<lambda>_<scheme>.log

and contains a single number. For each M in {2, 4, 6} (M=8 is omitted) this
script writes a markdown table (output/couette/couette_table_M<M>.md) with
one column per nx value and one row per lambda value. Each cell holds the mean
+/- the standard deviation of the log values across all available <scheme>
values.
"""

import re
import statistics
from collections import defaultdict
from pathlib import Path

LOG_DIR = (Path(__file__).resolve().parent.parent.parent /
           "output" / "couette" / "couette_logs")
OUT_DIR = LOG_DIR.parent
NAME_RE = re.compile(
    r"^couette_log_0\.3_(?P<M>[^_]+)_(?P<nx>[^_]+)_16_"
    r"(?P<lambda>[^_]+)_(?P<scheme>.+)\.log$"
)
KEEP_M = ("2", "4", "6")


def collect():
    # data[M][nx][lam] -> {scheme: value}
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    for path in sorted(LOG_DIR.glob("*.log")):
        m = NAME_RE.match(path.name)
        if not m:
            print(f"skipping unparseable name: {path.name}")
            continue
        M, nx, lam, scheme = m["M"], m["nx"], m["lambda"], m["scheme"]
        data[M][nx][lam][scheme] = float(path.read_text().strip())
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
    nx_keys = sorted(cols_data, key=float)
    lam_keys = sorted(
        {lam for col in cols_data.values() for lam in col},
        key=float,
    )

    header = ["lambda"] + [f"nx={nx}" for nx in nx_keys]
    lines = [
        f"# Couette log values, M = {M}",
        "",
        "Mean ± population standard deviation across schemes "
        "(lf, upwind, upwind_lw).",
        "",
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for lam in lam_keys:
        row = [lam]
        for nx in nx_keys:
            schemes = cols_data[nx].get(lam, {})
            row.append(fmt_cell(list(schemes.values())))
        lines.append("| " + " | ".join(row) + " |")

    out = OUT_DIR / f"couette_table_M{M}.md"
    out.write_text("\n".join(lines) + "\n")
    print(f"wrote {out}")


def main():
    data = collect()
    for M in KEEP_M:
        if M not in data:
            print(f"no data for M={M}")
            continue
        write_table(M, data[M])


if __name__ == "__main__":
    main()
