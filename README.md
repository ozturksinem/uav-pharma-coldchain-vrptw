# Autonomous UAV Cold-Chain Pharmaceutical Routing (Solo Python Implementation)

> **Independent Python Optimization & Metaheuristic Framework for Time-Critical Medical Drone Delivery**

*Note: Inspired by my 2026 B.Sc. graduation project at Ankara Yıldırım Beyazıt University (AYBÜ), this repository contains my **independent, solo-authored Python implementation** and algorithmic extensions. To preserve ongoing peer-reviewed manuscript confidentiality, full real-world datasets and unpublished extensions are maintained privately and available to academic reviewers or prospective supervisors upon request.*

---

## Problem Scope

This project models an autonomous **Pure UAV Delivery Network** for temperature-sensitive pharmaceuticals (vaccines, biologics, blood products), minimizing **Total Operational Delivery Time** subject to:
* **Cold-Chain Thermal Limit ($T_{\text{safe}}$):** Strict upper bound on depot-to-patient transit duration.
* **Payload-Dependent Energy Model:** Battery consumption incorporating both empty flight power and carried payload mass.
* **Delivery Time Windows ($[a_i, b_i]$) & Fleet Capacity ($Q_k$):** Hard operational constraints without truck–UAV synchronization delays.

[Code_Generated_Image.png]

---

## Repository Structure

```text
uav-pharma-coldchain-vrptw/
├── README.md
├── demo_uav_vrptw.py             # Self-contained synthetic 6-node demo (Tabu Search vs. SA)
└── Code_Generated_Image.png      # Route & convergence benchmark plot
```

---

## Quick Start (Synthetic Demo)

Run the standalone 6-node synthetic benchmark comparing **Tabu Search** and **Simulated Annealing**:

```bash
python demo_uav_vrptw.py
```

---

## Ongoing Research Extensions
* Multi-seed statistical benchmarking (Tabu Search vs. Simulated Annealing / ALNS).
* Stochastic wind and emergency demand uncertainty modeling for future graduate research.
