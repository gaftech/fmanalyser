from fmanalyser.device.drivers.funcube import Funcube
import time
import tempfile
import subprocess
import shutil
import math

def main():
    
    outfile = tempfile.NamedTemporaryFile()
    d = Funcube()

#    freq = 88000
#    
#    for i in range(200):
#        d.tune(freq)
#        time.sleep(0.5)
##        time.sleep(10)
#        
#        for j in range(10):
#            l = d.get_rf()
#            l = 10 * math.log10(l)
#            print '%s %s' % (freq+j*10, l)
#            outfile.write('%s %s\n' % (freq+j*10, l))
#            time.sleep(0.1)
#        freq += 100
#    d.close()
    
    gp = subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE)
    
    f = 107700
    d.tune(f)
    time.sleep(0.5)
    i = 0
    
    time.sleep(1)
    
    while True:
        
#        print ' '.join(str(fn.level()) for fn in [
#            d._block.sig_re,
#            d._block.sig_m,
#            d._block.sig_mag2,
#        ])

        

        l = d._block.level_out.level()
        l = 10 * math.log10(l)

#        l1 = d._block.test1.level()
#        l2 = 20 * math.log10(d._block.test2.level())
        
#        outfile.write('%s %s %s %s\n' % (i, l, l1, l2))
        outfile.write('%s %s\n' % (i, l))
        outfile.flush()
#        gp.stdin.write("plot '%s' using 1:2 with lines, '%s' using 1:4 with lines\n" % (outfile.name,outfile.name,))
        gp.stdin.write("set yrange [-100:0]\n")
        gp.stdin.write("plot '%s' using 1:2 with lines\n" % (outfile.name,))
        time.sleep(0.1)
        i += 1
    
    outfile.flush()
    
    print '%s written' % outfile.name
    
    
    gp.stdin.write("plot '%s' with lines\n" % (outfile.name,))
    
    shutil.copy2(outfile.name, './test.data')
    
    raw_input('Press Enter to exit')
    
if __name__ == '__main__':
    main()