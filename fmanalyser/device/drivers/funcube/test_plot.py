import time
import numpy as np
import matplotlib.pyplot as plt
import random

def gen_random():
    for i in range(11):
        yield i, random.random()

def main():
    
    
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
#    ax.plot(gen_random())
    ax.plot([x for x in gen_random()])
    plt.show(block=False)

    for i in range(10):
        time.sleep(0.5)
        ax.plot([x for x in gen_random()])

    raw_input('Press Enter.')

    


#    plt.plot([1,2,3,4])
#    plt.ylabel('some numbers')
#    plt.show()


if __name__ == '__main__':
    main()