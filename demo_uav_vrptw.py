"""
Autonomous UAV Cold-Chain Pharmaceutical Routing (Synthetic Demo)
Independent Solo Implementation: Tabu Search vs. Simulated Annealing
Author: Sinem Ozturk
"""

import math
import random
import time

# --- 1. Synthetic 6-Pharmacy Test Instance (Safe Public Demo Data) ---
NUM_UAV = 3
Q_CAP = 2.7          # Max payload (kg)
V_ORT = 61.2         # Cruise speed (km/h)
T_SETUP = 5.0        # Depot setup time (min)
T_MAX = 55.0         # Max airborne time (min)
T_SAFE = 120.0       # Cold-chain thermal limit (min)
D_MAX = 15.0         # Max flight range (km)
E_MAX = 548.0        # Battery capacity (Wh)
E0 = 40.0            # Empty power coeff (Wh/h)
EP = 15.0            # Payload power coeff (Wh/(kg*h))

# Synthetic (x, y) coordinates in km from depot (0, 0)
COORDS = {
    0: (0.0, 0.0),
    1: (2.1, 1.8),
    2: (-1.9, 2.4),
    3: (-2.5, -1.2),
    4: (1.6, -2.2),
    5: (3.0, 0.4),
    6: (-0.8, -2.9),
}
DEMAND = {1: 0.8, 2: 1.4, 3: 1.1, 4: 1.2, 5: 0.9, 6: 1.5}
A_TW = {1: 5, 2: 10, 3: 10, 4: 15, 5: 5, 6: 15}
B_TW = {1: 60, 2: 70, 3: 75, 4: 80, 5: 65, 6: 85}
SERVICE = {i: 3.0 for i in range(1, 7)}
SERVICE[0] = 0.0
CUSTOMERS = sorted(DEMAND.keys())

DIST = {
    (i, j): math.hypot(COORDS[i][0] - COORDS[j][0], COORDS[i][1] - COORDS[j][1])
    for i in COORDS for j in COORDS
}
TIME = {(i, j): (DIST[(i, j)] / V_ORT) * 60.0 for i in COORDS for j in COORDS}


def evaluate_route(route):
    if not route:
        return 0.0, 0.0
    path = [0] + route + [0]
    arcs = list(zip(path[:-1], path[1:]))

    flight_time = sum(TIME[a] for a in arcs)
    service_time = sum(SERVICE[c] for c in route)
    z_val = flight_time + service_time + T_SETUP

    total_load = sum(DEMAND[c] for c in route)
    total_dist = sum(DIST[a] for a in arcs)

    # Payload-dependent energy consumption along each arc
    remaining_load = total_load
    energy = 0.0
    for u, v in arcs:
        arc_hours = (TIME[(u, v)] + SERVICE[u]) / 60.0
        energy += (E0 + EP * remaining_load) * arc_hours
        if v != 0:
            remaining_load -= DEMAND[v]

    arrival = 0.0
    prev = 0
    tw_viol = 0.0
    cold_viol = 0.0
    for c in route:
        arrival = max(arrival + SERVICE[prev] + TIME[(prev, c)], A_TW[c])
        if arrival > B_TW[c]:
            tw_viol += arrival - B_TW[c]
        if arrival > T_SAFE:
            cold_viol += arrival - T_SAFE
        prev = c

    penalty = (
        1000.0 * max(0.0, total_load - Q_CAP)
        + 1000.0 * (tw_viol + cold_viol)
        + 1000.0 * max(0.0, total_dist - D_MAX)
        + 1000.0 * max(0.0, z_val - T_MAX)
        + 1000.0 * max(0.0, energy - E_MAX)
    )
    return z_val, penalty


def evaluate_solution(sol):
    total_z, total_pen = 0.0, 0.0
    for r in sol:
        z_r, p_r = evaluate_route(r)
        total_z += z_r
        total_pen += p_r
    return total_z + total_pen, total_z, total_pen


def random_initial_solution():
    sol = [[] for _ in range(NUM_UAV)]
    for c in CUSTOMERS:
        sol[random.randrange(NUM_UAV)].append(c)
    return sol


def generate_neighbors(sol, max_moves=200):
    moves = []
    for u in range(NUM_UAV):
        for idx, c in enumerate(sol[u]):
            for u2 in range(NUM_UAV):
                for pos in range(len(sol[u2]) + (0 if u2 == u else 1)):
                    if u2 == u and pos == idx:
                        continue
                    ns = [list(r) for r in sol]
                    ns[u].pop(idx)
                    ns[u2].insert(pos, c)
                    moves.append((ns, ("rel", c, u2)))
    if len(moves) > max_moves:
        moves = random.sample(moves, max_moves)
    return moves


def solve_tabu_search(iterations=400, tenure=12):
    curr = random_initial_solution()
    best = [list(r) for r in curr]
    best_cost, _, _ = evaluate_solution(best)
    tabu = {}
    for it in range(iterations):
        cand_best, cand_cost, cand_move = None, float("inf"), None
        for ns, move in generate_neighbors(curr):
            cost, _, _ = evaluate_solution(ns)
            if tabu.get(move, -1) > it and cost >= best_cost:
                continue
            if cost < cand_cost:
                cand_best, cand_cost, cand_move = ns, cost, move
        if cand_best is None:
            break
        curr = cand_best
        tabu[cand_move] = it + tenure
        if cand_cost < best_cost:
            best_cost, best = cand_cost, [list(r) for r in curr]
    return best, evaluate_solution(best)


def solve_simulated_annealing(iterations=800, t_start=50.0, alpha=0.99):
    curr = random_initial_solution()
    curr_cost, _, _ = evaluate_solution(curr)
    best = [list(r) for r in curr]
    best_cost = curr_cost
    temp = t_start
    for _ in range(iterations):
        neighbors = generate_neighbors(curr, max_moves=30)
        if not neighbors:
            break
        ns, _ = random.choice(neighbors)
        cost, _, _ = evaluate_solution(ns)
        delta = cost - curr_cost
        if delta < 0 or random.random() < math.exp(-delta / max(temp, 1e-6)):
            curr, curr_cost = ns, cost
            if cost < best_cost:
                best_cost, best = cost, [list(r) for r in curr]
        temp *= alpha
    return best, evaluate_solution(best)


if __name__ == "__main__":
    random.seed(42)
    t0 = time.time()
    ts_sol, (ts_tot, ts_z, ts_pen) = solve_tabu_search()
    ts_time = time.time() - t0

    random.seed(42)
    t0 = time.time()
    sa_sol, (sa_tot, sa_z, sa_pen) = solve_simulated_annealing()
    sa_time = time.time() - t0

    print("=== Synthetic 6-Pharmacy UAV Cold-Chain Benchmark ===")
    print(f"Tabu Search         -> Z = {ts_z:.3f} min | Penalty = {ts_pen:.1f} | Time = {ts_time:.3f}s")
    print(f"Simulated Annealing -> Z = {sa_z:.3f} min | Penalty = {sa_pen:.1f} | Time = {sa_time:.3f}s")
    for idx, r in enumerate(ts_sol, 1):
        if r:
            load = sum(DEMAND[c] for c in r)
            print(f"  UAV {idx}: 0 -> {' -> '.join(map(str, r))} -> 0 (Load: {load:.1f}/{Q_CAP} kg)")
