import numpy as np
from collections import deque

def stitch_contours(contours, snap_dist=20.0):
    """
    Connects contours using a Double-Ended Nearest Neighbor approach.
    It can attach new lines to the START or END of the path, minimizing travel.
    """
    if not contours:
        return np.array([])
    
    remaining = [c for c in contours if hasattr(c, 'shape') and c.shape[0] > 1]
    if not remaining:
        return np.array([])
    
    # Sort: Largest first to anchor the drawing
    remaining.sort(key=lambda x: len(x), reverse=True)
    
    # Start with largest piece
    first_piece = remaining.pop(0)
    
    # We use a Deque (Double Ended Queue) to grow in both directions
    # Convert numpy array to list of points
    dq = deque(first_piece.tolist())

    while remaining:
        # Current endpoints
        head_pos = np.array(dq[0])
        tail_pos = np.array(dq[-1])
        
        best_idx = -1
        best_dist = float("inf")
        
        # Mode: 0 = Attach to Tail, 1 = Attach to Head
        best_mode = 0 
        should_reverse = False
        
        # Search all remaining contours
        for i, c in enumerate(remaining):
            start_node = c[0]
            end_node = c[-1]
            
            # 1. Check distance to TAIL
            d_tail_start = np.sum((tail_pos - start_node)**2)
            d_tail_end   = np.sum((tail_pos - end_node)**2)
            
            # 2. Check distance to HEAD
            d_head_start = np.sum((head_pos - start_node)**2)
            d_head_end   = np.sum((head_pos - end_node)**2)

            # Check Tail-Start
            if d_tail_start < best_dist:
                best_dist = d_tail_start
                best_idx = i
                best_mode = 0 # Tail
                should_reverse = False # Order is correct (Tail -> Start)

            # Check Tail-End
            if d_tail_end < best_dist:
                best_dist = d_tail_end
                best_idx = i
                best_mode = 0 # Tail
                should_reverse = True # Reverse to fit (Tail -> End)

            # Check Head-End (Prepend)
            if d_head_end < best_dist:
                best_dist = d_head_end
                best_idx = i
                best_mode = 1 # Head
                should_reverse = False # Order is correct (End -> Head)
            
            # Check Head-Start (Prepend)
            if d_head_start < best_dist:
                best_dist = d_head_start
                best_idx = i
                best_mode = 1 # Head
                should_reverse = True # Reverse to fit (Start -> Head)

            # Optimization
            if best_dist < snap_dist**2:
                break
        
        # Extract best candidate
        chosen = remaining.pop(best_idx)
        
        # Convert to list
        if isinstance(chosen, np.ndarray):
            chosen = chosen.tolist()

        if best_mode == 0:
            # ATTACH TO TAIL
            if should_reverse: chosen = chosen[::-1]
            dq.extend(chosen)
        else:
            # ATTACH TO HEAD (Prepend)
            if should_reverse: chosen = chosen[::-1]
            # Since we are prepending, we extendleft in reverse order of the segment
            # to maintain segment continuity
            dq.extendleft(chosen[::-1])

    return np.array(list(dq))