# Transportation Problem Solver

> Academic project developed for the **Operations Research** course  
> Faculty of Applied Sciences

----

## Table of Contents

1. [Overview](#overview)
2. [Authors](#authors)
3. [Methodology](#methodology)
4. [Validation System](#validation-system)
5. [Technologies & Architecture](#technologies--architecture)
6. [Usage Guide](#usage-guide)
7. [License](#license)

---

## Overview

An interactive application for solving the **classic Transportation Problem** using a step-by-step approach that mirrors the manual academic workflow. The application finds the minimum-cost transportation plan between suppliers and beneficiaries, displaying every intermediate tableau and computation.

🔗 **[Open Transportation Problem Application](https://transportation-problem-ildd.streamlit.app/)**

> **Note:** All in-code comments are written in **Romanian**.

---

## Authors

| Name | Group |
|------|-------|
| Dedu Anișoara-Nicoleta | 1333a |
| Dumitrescu Andreea Mihaela | 1333a |
| Iliescu Daria-Gabriela | 1333a |
| Lungu Ionela-Diana | 1333a |

---

## Methodology

The algorithm follows the canonical four-step procedure taught in the Operations Research course.

### Step 1 — Problem Equilibration

Checks whether the problem is **balanced** (`Σ Supply = Σ Demand`):

| Condition | Action |
|-----------|--------|
| `Σ Supply = Σ Demand` | Proceed as-is (balanced) |
| `Σ Supply > Σ Demand` | Introduce a **dummy beneficiary B\*** with zero transport costs |
| `Σ Supply < Σ Demand` | Introduce a **dummy supplier A\*** with zero transport costs |

### Step 2 — Initial Basic Feasible Solution (North-West Corner)

The **North-West Corner Method** is applied to construct the first allocation table `T₀`. After filling, the algorithm checks for degeneracy:

```
V = m + n - 1   (required number of basic variables)
NC = number of filled cells in T₀
```

- If `NC = V` → non-degenerate solution, proceed normally.
- If `NC < V` → degenerate solution, zero-value allocations (ε) are added for perturbation.

The initial transportation cost is computed as:

```
f₀ = Σ cᵢⱼ · Xᵢⱼ   (sum over all basic cells)
```

### Step 3 — Optimality Test (MODI Method / Potentials)

At each iteration `Iₖ`, the algorithm applies the **Modified Distribution (MODI) Method**:

**① Potential System** — solves for `uᵢ` and `vⱼ` using the basic cells:
```
uᵢ + vⱼ = cᵢⱼ    for all (i, j) in basis,   with u₁ = 0
```

**② Theoretical Cost Table** `C̃`:
```
C̃ᵢⱼ = uᵢ + vⱼ
```

**③ Reduced Cost Table** `Δ`:
```
δᵢⱼ = cᵢⱼ − C̃ᵢⱼ
```

**④ Optimality Check:**
- If `δᵢⱼ ≥ 0` for all non-basic cells → **optimal solution reached** (`STOP`).
- Otherwise → identify the most negative `δᵢⱼ` and perform a **pivot**.

**Pivoting procedure:**
1. Find the **circuit (loop)** through the current basis passing through the entering cell.
2. Compute `θ = min{ Xᵢⱼ at (−) positions }`.
3. Update allocations along the circuit (`+θ` and `−θ` alternately).
4. The cell reaching zero exits the basis; the entering cell joins.
5. Update cost: `fₖ₊₁ = fₖ + δ_entering · θ`

### Step 4 — Final Interpretation

Once the optimality condition is met, the application displays:
- The final allocation table with supply/demand totals.
- The **minimum total transportation cost**.
- A **managerial interpretation** listing each beneficiary's supply sources and quantities.

---

## Validation System

Optimality is confirmed when all reduced costs for non-basic cells are non-negative:

### ✅ Optimality Criterion
```
δᵢⱼ ≥ 0   for all (i, j) ∉ basis
```

### ✅ Supply & Demand Satisfaction
Every row and column constraint is met:
```
Σⱼ Xᵢⱼ = aᵢ   (supply)      Σᵢ Xᵢⱼ = bⱼ   (demand)
```

### ✅ Cost Consistency
The final cost is verified against the direct summation:
```
f* = Σ cᵢⱼ · Xᵢⱼ   (over all basic cells in the final tableau)
```

---

## Technologies & Architecture

| Component | Technology |
|-----------|------------|
| Core Engine | Python 3.x — NumPy (matrix operations), Pandas (table display) |
| Frontend | Streamlit — reactive interface with real-time editable cost matrix |
| Visual Design | Custom CSS — pink-themed UI with animated 🎀 falling ribbon effect on solve |
| Number Formatting | Custom `fmt()` utility — suppresses unnecessary decimals (e.g. `25.0` → `25`) |

---

## Usage Guide

**Step 1 — Configuration**  
Use the sidebar to set the number of suppliers (`Aᵢ`) and beneficiaries (`Bⱼ`), between 2 and 6 each.

**Step 2 — Data Input**  
Fill in the unit cost matrix `cᵢⱼ`, the supply vector `aᵢ`, and the demand vector `bⱼ` using the integrated data editor. A default example is preloaded.

**Step 3 — Solve**  
Click **"Rezolvă Problema Pas cu Pas"** to run the algorithm. Each step is displayed with full LaTeX-rendered formulas, intermediate tableaux, and highlighted basic cells.

**Step 4 — Interpret Results**  
Read the final allocation table and the managerial transportation plan at the bottom of the page.

---

## License

© 2026 — Iliescu D., Lungu D., Dedu A., Dumitrescu A.

Operations Research — Faculty of Applied Sciences.  
Developed for academic purposes. Use of the code for educational purposes is permitted with **proper attribution to the authors**.
