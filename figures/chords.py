TRIADS_DICT = {
    
    # C - E - G 
    "Major Triad": [ 
        [0, 4, 7],   # Root position
        [0, 3, 8],   # First inversion
        [0, 5, 9]    # Second inversion
    ],
    
    # C - Eb - G 
    "Minor Triad": [ 
        [0, 3, 7],   
        [0, 4, 9],   
        [0, 5, 8]    
    ],

    # C - Eb - Gb
    "Diminished Triad": [ 
        [0, 3, 6],   
        [0, 3, 9],   
        [0, 6, 9]    
    ],
    
    # C - E - G# (inversions are identical due to symmetry)
    "Augmented Triad": [ 
        [0, 4, 8],   
        [0, 4, 8],   
        [0, 4, 8]    
    ],
    
    # C - F - G (suspended second or suspended fourth)
    "Suspended": [ 
        [0, 5, 7],   
        [0, 2, 7],   
        [0, 5, 10]   
    ]
}


SEVENTH_CHORDS_DICT = {
    
    "Major Seventh": [
        [0, 4, 7, 11],   
        [0, 3, 7, 8],     
        [0, 4, 5, 9],     
        [0, 1, 5, 8]     
    ],
    
    "Dominant Seventh": [
        [0, 4, 7, 10],   
        [0, 3, 6, 8],    
        [0, 3, 5, 9],    
        [0, 2, 5, 8]    
    ],
    
    "Minor Seventh": [
        [0, 3, 7, 10],   
        [0, 4, 7, 9],    
        [0, 3, 5, 8],    
        [0, 2, 5, 9]    
    ],
    
    "Diminished Seventh": [  # (inversions are identical due to symmetry)
        [0, 3, 6, 9],    
        [0, 3, 6, 9],     
        [0, 3, 6, 9],    
        [0, 3, 6, 9]
    ],
        
    "Half-Diminished Seventh": [
        [0, 3, 6, 10],   
        [0, 3, 7, 9],    
        [0, 4, 6, 9],    
        [0, 2, 5, 8]    
    ],

    "Minor-Major Seventh": [
        [0, 3, 7, 11],   
        [0, 4, 8, 9],    
        [0, 4, 5, 8],    
        [0, 1, 5, 9]    
    ]
}