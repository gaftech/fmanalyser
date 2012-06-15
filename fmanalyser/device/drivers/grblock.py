# -*- coding: utf-8 -*-
from gnuradio import gr, blks2

class TopBlock(gr.top_block):
    
    def __init__(self,
                 samp_rate,
                 source,
                 fft_size=1024,
                 dc_blocker=True,
                 dc_blocker_length=32,
                 dc_blocker_long_form=True,
    ):
        super(TopBlock, self).__init__()
        
        self.source = source
        self.samp_rate = samp_rate
        self.fft_size = fft_size        
        
        chain = [self.source]

        if dc_blocker:
            self._dc_blocker = gr.dc_blocker_cc(dc_blocker_length, dc_blocker_long_form)
            chain.append(self._dc_blocker)
        else:
            self._dc_blocker = None
        
        self.lp_fft = blks2.logpwrfft_c( #@UndefinedVariable
            sample_rate=samp_rate,
            fft_size=fft_size,
            ref_scale=2,
            frame_rate=30,
            avg_alpha=1.0,
            average=False,
        )
        chain.append(self.lp_fft)

        self.msg_q = gr.msg_queue(16)
        self.msg_sink = gr.message_sink(gr.sizeof_float*fft_size, self.msg_q, False)
        chain.append(self.msg_sink)
        
        self.connect(*chain)
        
    def set_freq(self, f):
        try:
            # gr-fcd case
            return self.source.set_freq(f)
        except AttributeError:
            pass
        try:
            # osmo source block case
            return self.source.set_center_freq(f,0)
        except AttributeError:
            pass
        
        return self.source.set_frequency(f)
        
