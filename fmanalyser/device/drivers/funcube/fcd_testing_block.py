#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Fcd Testing Block
# Generated: Wed Jun 13 11:35:19 2012
##################################################

from gnuradio import audio
from gnuradio import blks2
from gnuradio import eng_notation
from gnuradio import fcd
from gnuradio import fft
from gnuradio import gr
from gnuradio import window
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
from optparse import OptionParser

class fcd_testing_block(gr.top_block):

	def __init__(self, freq=91600000):
		gr.top_block.__init__(self, "Fcd Testing Block")

		##################################################
		# Parameters
		##################################################
		self.freq = freq

		##################################################
		# Variables
		##################################################
		self.samp_rate = samp_rate = 96000
		self.xlate_filter_taps = xlate_filter_taps = firdes.low_pass(1, samp_rate, 48000, 5000, firdes.WIN_HAMMING, 6.76)
		self.fft_size = fft_size = 1024

		##################################################
		# Message Queues
		##################################################
		gr_message_sink_0_msgq_out = gr_message_source_0_msgq_in = gr.msg_queue(2)

		##################################################
		# Blocks
		##################################################
		self.xlating_fir_filter = gr.freq_xlating_fir_filter_ccc(1, (xlate_filter_taps), 0, samp_rate)
		self.q_sink = gr.vector_sink_f(fft_size)
		self.power_probe = gr.probe_signal_f()
		self.nbfm_normal = blks2.nbfm_rx(
			audio_rate=48000,
			quad_rate=96000,
			tau=75e-6,
			max_dev=5e3,
		)
		self.lp_fft_sink = gr.vector_sink_f(fft_size)
		self.lp_fft = blks2.logpwrfft_c(
			sample_rate=samp_rate,
			fft_size=fft_size,
			ref_scale=2,
			frame_rate=30,
			avg_alpha=1.0,
			average=False,
		)
		self.low_pass_filter = gr.fir_filter_ccf(1, firdes.low_pass(
			1, samp_rate, 20000, 1500, firdes.WIN_HAMMING, 6.76))
		self.gr_stream_to_vector_0 = gr.stream_to_vector(gr.sizeof_gr_complex*1, fft_size)
		self.gr_simple_squelch_cc_0 = gr.simple_squelch_cc(-100, 1)
		self.gr_nlog10_ff_0_0 = gr.nlog10_ff(10, 1024, 0)
		self.gr_nlog10_ff_0 = gr.nlog10_ff(10, 1, 0)
		self.gr_multiply_const_vxx_1 = gr.multiply_const_vff((1, ))
		self.gr_message_source_0 = gr.message_source(gr.sizeof_float*fft_size, gr_message_source_0_msgq_in)
		self.gr_message_sink_0 = gr.message_sink(gr.sizeof_float*fft_size, gr_message_sink_0_msgq_out, False)
		self.gr_dc_blocker_0 = gr.dc_blocker_cc(256, True)
		self.gr_complex_to_mag_squared_1 = gr.complex_to_mag_squared(fft_size)
		self.gr_complex_to_mag_squared_0 = gr.complex_to_mag_squared(1)
		self.fft_vxx_0 = fft.fft_vcc(fft_size, True, (window.blackmanharris(1024)), True, 1)
		self.fft_sink = gr.vector_sink_f(fft_size)
		self.fcd_source_c_0 = fcd.source_c("hw:1")
		self.fcd_source_c_0.set_freq_corr(-120)
		self.fcd_source_c_0.set_freq(freq)
		    
		self.audio_sink = audio.sink(48000, "", True)

		##################################################
		# Connections
		##################################################
		self.connect((self.gr_multiply_const_vxx_1, 0), (self.audio_sink, 0))
		self.connect((self.fcd_source_c_0, 0), (self.xlating_fir_filter, 0))
		self.connect((self.xlating_fir_filter, 0), (self.low_pass_filter, 0))
		self.connect((self.gr_multiply_const_vxx_1, 0), (self.audio_sink, 1))
		self.connect((self.nbfm_normal, 0), (self.gr_multiply_const_vxx_1, 0))
		self.connect((self.low_pass_filter, 0), (self.gr_simple_squelch_cc_0, 0))
		self.connect((self.gr_simple_squelch_cc_0, 0), (self.nbfm_normal, 0))
		self.connect((self.lp_fft, 0), (self.lp_fft_sink, 0))
		self.connect((self.gr_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
		self.connect((self.fft_vxx_0, 0), (self.gr_complex_to_mag_squared_1, 0))
		self.connect((self.fcd_source_c_0, 0), (self.gr_dc_blocker_0, 0))
		self.connect((self.gr_dc_blocker_0, 0), (self.gr_complex_to_mag_squared_0, 0))
		self.connect((self.gr_complex_to_mag_squared_1, 0), (self.gr_nlog10_ff_0_0, 0))
		self.connect((self.gr_nlog10_ff_0_0, 0), (self.fft_sink, 0))
		self.connect((self.fcd_source_c_0, 0), (self.lp_fft, 0))
		self.connect((self.fcd_source_c_0, 0), (self.gr_stream_to_vector_0, 0))
		self.connect((self.gr_complex_to_mag_squared_0, 0), (self.gr_nlog10_ff_0, 0))
		self.connect((self.gr_nlog10_ff_0, 0), (self.power_probe, 0))
		self.connect((self.lp_fft, 0), (self.gr_message_sink_0, 0))
		self.connect((self.gr_message_source_0, 0), (self.q_sink, 0))

	def get_freq(self):
		return self.freq

	def set_freq(self, freq):
		self.freq = freq
		self.fcd_source_c_0.set_freq(self.freq)

	def get_samp_rate(self):
		return self.samp_rate

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate
		self.low_pass_filter.set_taps(firdes.low_pass(1, self.samp_rate, 20000, 1500, firdes.WIN_HAMMING, 6.76))
		self.set_xlate_filter_taps(firdes.low_pass(1, self.samp_rate, 48000, 5000, firdes.WIN_HAMMING, 6.76))
		self.lp_fft.set_sample_rate(self.samp_rate)

	def get_xlate_filter_taps(self):
		return self.xlate_filter_taps

	def set_xlate_filter_taps(self, xlate_filter_taps):
		self.xlate_filter_taps = xlate_filter_taps
		self.xlating_fir_filter.set_taps((self.xlate_filter_taps))

	def get_fft_size(self):
		return self.fft_size

	def set_fft_size(self, fft_size):
		self.fft_size = fft_size

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	parser.add_option("-f", "--freq", dest="freq", type="eng_float", default=eng_notation.num_to_str(91600000),
		help="Set freq [default=%default]")
	(options, args) = parser.parse_args()
	tb = fcd_testing_block(freq=options.freq)
	tb.start()
	raw_input('Press Enter to quit: ')
	tb.stop()

