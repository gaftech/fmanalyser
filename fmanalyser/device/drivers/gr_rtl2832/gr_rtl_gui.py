#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Gr Rtl Gui
# Generated: Mon May 21 16:34:48 2012
##################################################

from gnuradio import audio
from gnuradio import blks2
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import window
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
from gnuradio.wxgui import fftsink2
from gnuradio.wxgui import forms
from gnuradio.wxgui import numbersink2
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import baz
import wx

class gr_rtl_gui(grc_wxgui.top_block_gui):

	def __init__(self):
		grc_wxgui.top_block_gui.__init__(self, title="Gr Rtl Gui")
		_icon_path = "/usr/share/icons/hicolor/32x32/apps/gnuradio-grc.png"
		self.SetIcon(wx.Icon(_icon_path, wx.BITMAP_TYPE_ANY))

		##################################################
		# Variables
		##################################################
		self.freq = freq = 91600000
		self.samp_rate = samp_rate = 3200000
		self.rf_gain = rf_gain = 0
		self.freq_display = freq_display = freq
		self.filter_trans = filter_trans = 5000
		self.filter_decim = filter_decim = 8
		self.filter_cutoff = filter_cutoff = 50000
		self.fft_size = fft_size = 1024
		self.af_gain = af_gain = 1

		##################################################
		# Blocks
		##################################################
		_af_gain_sizer = wx.BoxSizer(wx.VERTICAL)
		self._af_gain_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_af_gain_sizer,
			value=self.af_gain,
			callback=self.set_af_gain,
			label='af_gain',
			converter=forms.float_converter(),
			proportion=0,
		)
		self._af_gain_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_af_gain_sizer,
			value=self.af_gain,
			callback=self.set_af_gain,
			minimum=1,
			maximum=10,
			num_steps=100,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.Add(_af_gain_sizer)
		self.source_fft_0 = fftsink2.fft_sink_c(
			self.GetWin(),
			baseband_freq=0,
			y_per_div=10,
			y_divs=10,
			ref_level=0,
			ref_scale=2.0,
			sample_rate=samp_rate/filter_decim,
			fft_size=fft_size,
			fft_rate=15,
			average=True,
			avg_alpha=None,
			title="FFT Plot",
			peak_hold=False,
		)
		self.GridAdd(self.source_fft_0.win, 0, 0, 1, 6)
		self.source = baz.rtl_source_c(defer_creation=True)
		self.source.set_verbose(True)
		self.source.set_vid(0x0)
		self.source.set_pid(0x0)
		self.source.set_tuner_name("")
		self.source.set_default_timeout(0)
		self.source.set_use_buffer(True)
		self.source.set_fir_coefficients(([]))
		
		
		
		
		
		if self.source.create() == False: raise Exception("Failed to create RTL2832 Source: source")
		
		
		self.source.set_sample_rate(samp_rate)
		
		self.source.set_frequency(freq)
		
		
		self.source.set_auto_gain_mode(False)
		self.source.set_relative_gain(True)
		self.source.set_gain(rf_gain)
		  
		self.power_probe = gr.probe_avg_mag_sqrd_c(0, 1)
		self.low_pass_filter_0_0 = gr.fir_filter_ccf(filter_decim, firdes.low_pass(
			2, samp_rate, filter_cutoff, filter_trans, firdes.WIN_HAMMING, 6.76))
		self.low_pass_filter_0 = gr.fir_filter_ccf(8, firdes.low_pass(
			2, samp_rate, 25000, 50000, firdes.WIN_HAMMING, 6.76))
		self.gr_nlog10_ff_0_0 = gr.nlog10_ff(10, 1, 0)
		self.gr_multiply_const_vxx_1 = gr.multiply_const_vff((af_gain, ))
		self.gr_complex_to_mag_squared_1 = gr.complex_to_mag_squared(1)
		self._freq_display_static_text = forms.static_text(
			parent=self.GetWin(),
			value=self.freq_display,
			callback=self.set_freq_display,
			label="Frequency",
			converter=forms.float_converter(),
		)
		self.Add(self._freq_display_static_text)
		self.filtered_power = numbersink2.number_sink_f(
			self.GetWin(),
			unit="dB",
			minval=-100,
			maxval=0,
			factor=1.0,
			decimal_places=1,
			ref_level=0,
			sample_rate=samp_rate/filter_decim,
			number_rate=10,
			average=True,
			avg_alpha=None,
			label="Number Plot",
			peak_hold=False,
			show_gauge=True,
		)
		self.GridAdd(self.filtered_power.win, 1, 0, 1, 6)
		self.blks2_wfm_rcv_0_0 = blks2.wfm_rcv(
			quad_rate=352800,
			audio_decimation=8,
		)
		self.audio_sink_0_0 = audio.sink(48000, "", True)

		##################################################
		# Connections
		##################################################
		self.connect((self.low_pass_filter_0_0, 0), (self.gr_complex_to_mag_squared_1, 0))
		self.connect((self.low_pass_filter_0_0, 0), (self.source_fft_0, 0))
		self.connect((self.gr_complex_to_mag_squared_1, 0), (self.gr_nlog10_ff_0_0, 0))
		self.connect((self.gr_nlog10_ff_0_0, 0), (self.filtered_power, 0))
		self.connect((self.source, 0), (self.low_pass_filter_0_0, 0))
		self.connect((self.low_pass_filter_0_0, 0), (self.power_probe, 0))
		self.connect((self.source, 0), (self.low_pass_filter_0, 0))
		self.connect((self.low_pass_filter_0, 0), (self.blks2_wfm_rcv_0_0, 0))
		self.connect((self.gr_multiply_const_vxx_1, 0), (self.audio_sink_0_0, 0))
		self.connect((self.blks2_wfm_rcv_0_0, 0), (self.gr_multiply_const_vxx_1, 0))

	def get_freq(self):
		return self.freq

	def set_freq(self, freq):
		self.freq = freq
		self.set_freq_display(self.freq)
		self.source.set_frequency(self.freq)

	def get_samp_rate(self):
		return self.samp_rate

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate
		self.low_pass_filter_0.set_taps(firdes.low_pass(2, self.samp_rate, 25000, 50000, firdes.WIN_HAMMING, 6.76))
		self.source.set_sample_rate(self.samp_rate)
		self.low_pass_filter_0_0.set_taps(firdes.low_pass(2, self.samp_rate, self.filter_cutoff, self.filter_trans, firdes.WIN_HAMMING, 6.76))
		self.source_fft_0.set_sample_rate(self.samp_rate/self.filter_decim)

	def get_rf_gain(self):
		return self.rf_gain

	def set_rf_gain(self, rf_gain):
		self.rf_gain = rf_gain
		self.source.set_gain(self.rf_gain)

	def get_freq_display(self):
		return self.freq_display

	def set_freq_display(self, freq_display):
		self.freq_display = freq_display
		self._freq_display_static_text.set_value(self.freq_display)

	def get_filter_trans(self):
		return self.filter_trans

	def set_filter_trans(self, filter_trans):
		self.filter_trans = filter_trans
		self.low_pass_filter_0_0.set_taps(firdes.low_pass(2, self.samp_rate, self.filter_cutoff, self.filter_trans, firdes.WIN_HAMMING, 6.76))

	def get_filter_decim(self):
		return self.filter_decim

	def set_filter_decim(self, filter_decim):
		self.filter_decim = filter_decim
		self.source_fft_0.set_sample_rate(self.samp_rate/self.filter_decim)

	def get_filter_cutoff(self):
		return self.filter_cutoff

	def set_filter_cutoff(self, filter_cutoff):
		self.filter_cutoff = filter_cutoff
		self.low_pass_filter_0_0.set_taps(firdes.low_pass(2, self.samp_rate, self.filter_cutoff, self.filter_trans, firdes.WIN_HAMMING, 6.76))

	def get_fft_size(self):
		return self.fft_size

	def set_fft_size(self, fft_size):
		self.fft_size = fft_size

	def get_af_gain(self):
		return self.af_gain

	def set_af_gain(self, af_gain):
		self.af_gain = af_gain
		self._af_gain_slider.set_value(self.af_gain)
		self._af_gain_text_box.set_value(self.af_gain)
		self.gr_multiply_const_vxx_1.set_k((self.af_gain, ))

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = gr_rtl_gui()
	tb.Run(True)

