import numpy as np

def stitch_contours(contours,snap_dist=20.0):

    remaining = list(contours)


    lengths = [len(c) for c in remaining]
    idx = int(np.argmax(lengths))
    current = remaining.pop(idx)
    
    stitched = current.tolist()
    current_end = stitched[-1]
    
    while remaining:
        best_idx = None
        best_dist = float("inf")
        best_reverse = False
        for i,c in enumerate(remaining):
            d_start = np.linalg.norm(current_end-c[0])
            d_end = np.linalg.norm(current_end-c[-1])

            if d_start<best_dist:
                best_idx = i
                best_dist=d_start
                best_reverse=False

            if d_end<best_dist:
                best_idx=i
                best_dist=d_end
                best_reverse=True

        chosen = remaining.pop(best_idx)
        #reverse contour if req
        if(best_reverse):
            chosen = chosen[::-1]
        
        #staight connector
        stitched.append(chosen[0].tolist())
        #append contour
        stitched.extend(chosen[1:].tolist())
        current_end=stitched[-1]
    return np.array(stitched)

