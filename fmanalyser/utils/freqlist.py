# -*- coding: utf-8 -*-

def get_frequencies(start=87500, stop=108000, step=100):
    return range(start, stop+step, step)
    
frequencies = get_frequencies() 
fine_tune_frequencies = get_frequencies(step=50)