#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Fcd Block
# Generated: Fri Jun  1 14:34:14 2012
##################################################

from gnuradio import audio
from gnuradio import blks2
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
from optparse import OptionParser
import osmosdr

class fcd_block(gr.top_block):

	def __init__(self, freq=91600000):
		gr.top_block.__init__(self, "Fcd Block")

		##################################################
		# Parameters
		##################################################
		self.freq = freq

		##################################################
		# Variables
		##################################################
		self.samp_rate = samp_rate = 192000
		self.xlate_filter_taps = xlate_filter_taps = firdes.low_pass(1, samp_rate, 48000, 5000, firdes.WIN_HAMMING, 6.76)

		##################################################
		# Blocks
		##################################################
		self.xlating_fir_filter = gr.freq_xlating_fir_filter_ccc(1, (xlate_filter_taps), 0, samp_rate)
		self.power_probe = gr.probe_signal_f()
		self.osmosdr_source_c_0 = osmosdr.source_c( args="nchan=" + str(1) + " " + ""  )
		self.osmosdr_source_c_0.set_sample_rate(samp_rate)
		self.osmosdr_source_c_0.set_center_freq(0, 0)
		self.osmosdr_source_c_0.set_freq_corr(0, 0)
		self.osmosdr_source_c_0.set_gain_mode(0, 0)
		self.osmosdr_source_c_0.set_gain(0, 0)
		self.nbfm_normal = blks2.nbfm_rx(
			audio_rate=48000,
			quad_rate=96000,
			tau=75e-6,
			max_dev=5e3,
		)
		self.low_pass_filter = gr.fir_filter_ccf(1, firdes.low_pass(
			1, samp_rate, 20000, 1500, firdes.WIN_HAMMING, 6.76))
		self.gr_simple_squelch_cc_0 = gr.simple_squelch_cc(-100, 1)
		self.gr_nlog10_ff_0 = gr.nlog10_ff(10, 1, 0)
		self.gr_multiply_const_vxx_1 = gr.multiply_const_vff((1, ))
		self.gr_complex_to_mag_squared_0 = gr.complex_to_mag_squared(1)
		self.audio_sink = audio.sink(48000, "", True)

		##################################################
		# Connections
		##################################################
		self.connect((self.gr_multiply_const_vxx_1, 0), (self.audio_sink, 0))
		self.connect((self.xlating_fir_filter, 0), (self.low_pass_filter, 0))
		self.connect((self.gr_multiply_const_vxx_1, 0), (self.audio_sink, 1))
		self.connect((self.nbfm_normal, 0), (self.gr_multiply_const_vxx_1, 0))
		self.connect((self.low_pass_filter, 0), (self.gr_simple_squelch_cc_0, 0))
		self.connect((self.gr_simple_squelch_cc_0, 0), (self.nbfm_normal, 0))
		self.connect((self.gr_complex_to_mag_squared_0, 0), (self.gr_nlog10_ff_0, 0))
		self.connect((self.gr_nlog10_ff_0, 0), (self.power_probe, 0))
		self.connect((self.osmosdr_source_c_0, 0), (self.xlating_fir_filter, 0))
		self.connect((self.osmosdr_source_c_0, 0), (self.gr_complex_to_mag_squared_0, 0))

	def get_freq(self):
		return self.freq

	def set_freq(self, freq):
		self.freq = freq

	def get_samp_rate(self):
		return self.samp_rate

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate
		self.set_xlate_filter_taps(firdes.low_pass(1, self.samp_rate, 48000, 5000, firdes.WIN_HAMMING, 6.76))
		self.low_pass_filter.set_taps(firdes.low_pass(1, self.samp_rate, 20000, 1500, firdes.WIN_HAMMING, 6.76))
		self.osmosdr_source_c_0.set_sample_rate(self.samp_rate)

	def get_xlate_filter_taps(self):
		return self.xlate_filter_taps

	def set_xlate_filter_taps(self, xlate_filter_taps):
		self.xlate_filter_taps = xlate_filter_taps
		self.xlating_fir_filter.set_taps((self.xlate_filter_taps))

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	parser.add_option("-f", "--freq", dest="freq", type="eng_float", default=eng_notation.num_to_str(91600000),
		help="Set freq [default=%default]")
	(options, args) = parser.parse_args()
	tb = fcd_block(freq=options.freq)
	tb.start()
	raw_input('Press Enter to quit: ')
	tb.stop()

