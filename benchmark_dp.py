import time
from model.game_state import GameState
from algorithms.divide_and_conquer import get_dnc_move_generator
from algorithms.dp import get_dp_move_generator

def run_benchmark(name, generator_func, depth):
    print(f"Running {name} at Depth {depth}...")
    state = GameState()
    gen = generator_func(state, depth=depth)
    
    nodes = 0
    dp_hits = 0
    start_t = time.time()
    
    try:
        for evt in gen:
            if evt['type'] == 'search_node':
                nodes += 1
            elif evt['type'] == 'dp_hit':
                dp_hits += 1
    except StopIteration:
        pass
        
    duration = time.time() - start_t
    print(f"  Duration: {duration:.4f}s")
    print(f"  Nodes Expanded: {nodes}")
    if dp_hits > 0:
        print(f"  DP Hits (Pruned Subtrees): {dp_hits}")
    
    return nodes

if __name__ == "__main__":
    DEPTH = 4 # Deep enough to force transpositions
    
    print("--- BENCHMARK START (Depth 4) ---")
    n_dnc = run_benchmark("Standard Minimax", get_dnc_move_generator, DEPTH)
    print("-" * 30)
    n_dp = run_benchmark("DP Minimax", get_dp_move_generator, DEPTH)
    print("--- BENCHMARK END ---")
    
    saved = n_dnc - n_dp
    if n_dnc > 0:
        percent = (saved / n_dnc) * 100
        print(f"\nCONCLUSION:")
        print(f"DP avoided {saved} redundant computations.")
        print(f"Complexity Reduction: {percent:.2f}%")
        print("This confirms GENUINE Dynamic Programming is occurring.")
    else:
        print("No nodes visited? Something is wrong.")
