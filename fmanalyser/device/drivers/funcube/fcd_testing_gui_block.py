#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: FCD FM Receiver
# Author: OZ9AEC
# Description: Simple FM receiver using the Funcube Dongle
# Generated: Thu Jun 14 15:57:20 2012
##################################################

from gnuradio import audio
from gnuradio import blks2
from gnuradio import eng_notation
from gnuradio import fcd
from gnuradio import gr
from gnuradio import window
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
from gnuradio.wxgui import fftsink2
from gnuradio.wxgui import forms
from gnuradio.wxgui import numbersink2
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import wx

class fcd_testing_gui_block(grc_wxgui.top_block_gui):

	def __init__(self):
		grc_wxgui.top_block_gui.__init__(self, title="FCD FM Receiver")
		_icon_path = "/usr/share/icons/hicolor/32x32/apps/gnuradio-grc.png"
		self.SetIcon(wx.Icon(_icon_path, wx.BITMAP_TYPE_ANY))

		##################################################
		# Variables
		##################################################
		self.samp_rate = samp_rate = 96000
		self.offset_fine = offset_fine = 0
		self.offset_coarse = offset_coarse = 0
		self.freq = freq = 91600000
		self.xlate_filter_taps = xlate_filter_taps = firdes.low_pass(1, samp_rate, 48000, 5000, firdes.WIN_HAMMING, 6.76)
		self.width = width = 60000
		self.trans = trans = 1500
		self.sql_lev = sql_lev = -100
		self.rx_freq = rx_freq = freq+(offset_coarse+offset_fine)
		self.rf_gain = rf_gain = 20
		self.mixer_gain = mixer_gain = 20
		self.display_selector = display_selector = 0
		self.af_gain = af_gain = 1

		##################################################
		# Blocks
		##################################################
		_width_sizer = wx.BoxSizer(wx.VERTICAL)
		self._width_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_width_sizer,
			value=self.width,
			callback=self.set_width,
			label="Filter",
			converter=forms.float_converter(),
			proportion=0,
		)
		self._width_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_width_sizer,
			value=self.width,
			callback=self.set_width,
			minimum=2000,
			maximum=90000,
			num_steps=760,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.GridAdd(_width_sizer, 7, 0, 1, 1)
		_trans_sizer = wx.BoxSizer(wx.VERTICAL)
		self._trans_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_trans_sizer,
			value=self.trans,
			callback=self.set_trans,
			label="Trans",
			converter=forms.float_converter(),
			proportion=0,
		)
		self._trans_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_trans_sizer,
			value=self.trans,
			callback=self.set_trans,
			minimum=500,
			maximum=5000,
			num_steps=900,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.GridAdd(_trans_sizer, 8, 0, 1, 1)
		_sql_lev_sizer = wx.BoxSizer(wx.VERTICAL)
		self._sql_lev_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_sql_lev_sizer,
			value=self.sql_lev,
			callback=self.set_sql_lev,
			label="SQL",
			converter=forms.float_converter(),
			proportion=0,
		)
		self._sql_lev_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_sql_lev_sizer,
			value=self.sql_lev,
			callback=self.set_sql_lev,
			minimum=-100,
			maximum=0,
			num_steps=500,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.GridAdd(_sql_lev_sizer, 7, 2, 1, 1)
		self._rx_freq_static_text = forms.static_text(
			parent=self.GetWin(),
			value=self.rx_freq,
			callback=self.set_rx_freq,
			label="Receive",
			converter=forms.float_converter(),
		)
		self.GridAdd(self._rx_freq_static_text, 5, 3, 1, 1)
		_offset_fine_sizer = wx.BoxSizer(wx.VERTICAL)
		self._offset_fine_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_offset_fine_sizer,
			value=self.offset_fine,
			callback=self.set_offset_fine,
			label="Fine tune",
			converter=forms.float_converter(),
			proportion=0,
		)
		self._offset_fine_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_offset_fine_sizer,
			value=self.offset_fine,
			callback=self.set_offset_fine,
			minimum=-1000,
			maximum=1000,
			num_steps=400,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.GridAdd(_offset_fine_sizer, 6, 0, 1, 2)
		_offset_coarse_sizer = wx.BoxSizer(wx.VERTICAL)
		self._offset_coarse_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_offset_coarse_sizer,
			value=self.offset_coarse,
			callback=self.set_offset_coarse,
			label="Coarse tune",
			converter=forms.float_converter(),
			proportion=0,
		)
		self._offset_coarse_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_offset_coarse_sizer,
			value=self.offset_coarse,
			callback=self.set_offset_coarse,
			minimum=-48000,
			maximum=48000,
			num_steps=960,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.GridAdd(_offset_coarse_sizer, 6, 2, 1, 2)
		_mixer_gain_sizer = wx.BoxSizer(wx.VERTICAL)
		self._mixer_gain_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_mixer_gain_sizer,
			value=self.mixer_gain,
			callback=self.set_mixer_gain,
			label="RF",
			converter=forms.float_converter(),
			proportion=0,
		)
		self._mixer_gain_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_mixer_gain_sizer,
			value=self.mixer_gain,
			callback=self.set_mixer_gain,
			minimum=-5,
			maximum=30,
			num_steps=35,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.GridAdd(_mixer_gain_sizer, 7, 3, 1, 1)
		self._freq_text_box = forms.text_box(
			parent=self.GetWin(),
			value=self.freq,
			callback=self.set_freq,
			label="FCD Freq",
			converter=forms.float_converter(),
		)
		self.GridAdd(self._freq_text_box, 5, 1, 1, 1)
		self._display_selector_chooser = forms.drop_down(
			parent=self.GetWin(),
			value=self.display_selector,
			callback=self.set_display_selector,
			label="Spectrum",
			choices=[0, 1],
			labels=['Baseband','RF'],
		)
		self.GridAdd(self._display_selector_chooser, 5, 0, 1, 1)
		_af_gain_sizer = wx.BoxSizer(wx.VERTICAL)
		self._af_gain_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_af_gain_sizer,
			value=self.af_gain,
			callback=self.set_af_gain,
			label="VOL",
			converter=forms.float_converter(),
			proportion=0,
		)
		self._af_gain_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_af_gain_sizer,
			value=self.af_gain,
			callback=self.set_af_gain,
			minimum=0,
			maximum=5,
			num_steps=50,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.GridAdd(_af_gain_sizer, 8, 1, 1, 1)
		self.xlating_fir_filter = gr.freq_xlating_fir_filter_ccc(1, (xlate_filter_taps), -(offset_coarse+offset_fine), samp_rate)
		_rf_gain_sizer = wx.BoxSizer(wx.VERTICAL)
		self._rf_gain_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_rf_gain_sizer,
			value=self.rf_gain,
			callback=self.set_rf_gain,
			label="RF",
			converter=forms.float_converter(),
			proportion=0,
		)
		self._rf_gain_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_rf_gain_sizer,
			value=self.rf_gain,
			callback=self.set_rf_gain,
			minimum=-5,
			maximum=30,
			num_steps=35,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.GridAdd(_rf_gain_sizer, 7, 1, 1, 1)
		self.power_sink = numbersink2.number_sink_f(
			self.GetWin(),
			unit="Units",
			minval=-100,
			maxval=0,
			factor=1.0,
			decimal_places=10,
			ref_level=0,
			sample_rate=samp_rate,
			number_rate=15,
			average=False,
			avg_alpha=None,
			label="Number Plot",
			peak_hold=False,
			show_gauge=True,
		)
		self.Add(self.power_sink.win)
		self.nbfm_normal = blks2.nbfm_rx(
			audio_rate=48000,
			quad_rate=96000,
			tau=75e-6,
			max_dev=5e3,
		)
		self.low_pass_filter = gr.fir_filter_ccf(1, firdes.low_pass(
			1, samp_rate, width/2, trans, firdes.WIN_HAMMING, 6.76))
		self.gr_simple_squelch_cc_0 = gr.simple_squelch_cc(sql_lev, 1)
		self.gr_nlog10_ff_0 = gr.nlog10_ff(10, 1, 0)
		self.gr_multiply_const_vxx_1 = gr.multiply_const_vff((af_gain, ))
		self.gr_dc_blocker_0 = gr.dc_blocker_cc(256, True)
		self.gr_complex_to_mag_squared_0 = gr.complex_to_mag_squared(1)
		self.fftsink = fftsink2.fft_sink_c(
			self.GetWin(),
			baseband_freq=rx_freq*display_selector,
			y_per_div=10,
			y_divs=12,
			ref_level=0,
			ref_scale=1.0,
			sample_rate=samp_rate,
			fft_size=2048,
			fft_rate=15,
			average=True,
			avg_alpha=0.5,
			title="",
			peak_hold=False,
			win=window.blackmanharris,
			size=(800,200),
		)
		self.GridAdd(self.fftsink.win, 0, 0, 5, 4)
		self.fcd_source_c_1 = fcd.source_c("hw:1")
		self.fcd_source_c_1.set_mixer_gain(mixer_gain)
		self.fcd_source_c_1.set_freq_corr(-120)
		self.fcd_source_c_1.set_freq(freq)
		    
		self.audio_sink = audio.sink(48000, "", True)

		##################################################
		# Connections
		##################################################
		self.connect((self.xlating_fir_filter, 0), (self.low_pass_filter, 0))
		self.connect((self.fcd_source_c_1, 0), (self.xlating_fir_filter, 0))
		self.connect((self.gr_complex_to_mag_squared_0, 0), (self.gr_nlog10_ff_0, 0))
		self.connect((self.gr_nlog10_ff_0, 0), (self.power_sink, 0))
		self.connect((self.gr_multiply_const_vxx_1, 0), (self.audio_sink, 1))
		self.connect((self.gr_multiply_const_vxx_1, 0), (self.audio_sink, 0))
		self.connect((self.gr_simple_squelch_cc_0, 0), (self.nbfm_normal, 0))
		self.connect((self.nbfm_normal, 0), (self.gr_multiply_const_vxx_1, 0))
		self.connect((self.low_pass_filter, 0), (self.gr_simple_squelch_cc_0, 0))
		self.connect((self.fcd_source_c_1, 0), (self.gr_dc_blocker_0, 0))
		self.connect((self.gr_dc_blocker_0, 0), (self.gr_complex_to_mag_squared_0, 0))
		self.connect((self.fcd_source_c_1, 0), (self.fftsink, 0))

	def get_samp_rate(self):
		return self.samp_rate

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate
		self.low_pass_filter.set_taps(firdes.low_pass(1, self.samp_rate, self.width/2, self.trans, firdes.WIN_HAMMING, 6.76))
		self.set_xlate_filter_taps(firdes.low_pass(1, self.samp_rate, 48000, 5000, firdes.WIN_HAMMING, 6.76))
		self.fftsink.set_sample_rate(self.samp_rate)

	def get_offset_fine(self):
		return self.offset_fine

	def set_offset_fine(self, offset_fine):
		self.offset_fine = offset_fine
		self._offset_fine_slider.set_value(self.offset_fine)
		self._offset_fine_text_box.set_value(self.offset_fine)
		self.set_rx_freq(self.freq+(self.offset_coarse+self.offset_fine))
		self.xlating_fir_filter.set_center_freq(-(self.offset_coarse+self.offset_fine))

	def get_offset_coarse(self):
		return self.offset_coarse

	def set_offset_coarse(self, offset_coarse):
		self.offset_coarse = offset_coarse
		self._offset_coarse_slider.set_value(self.offset_coarse)
		self._offset_coarse_text_box.set_value(self.offset_coarse)
		self.set_rx_freq(self.freq+(self.offset_coarse+self.offset_fine))
		self.xlating_fir_filter.set_center_freq(-(self.offset_coarse+self.offset_fine))

	def get_freq(self):
		return self.freq

	def set_freq(self, freq):
		self.freq = freq
		self.set_rx_freq(self.freq+(self.offset_coarse+self.offset_fine))
		self._freq_text_box.set_value(self.freq)
		self.fcd_source_c_1.set_freq(self.freq)

	def get_xlate_filter_taps(self):
		return self.xlate_filter_taps

	def set_xlate_filter_taps(self, xlate_filter_taps):
		self.xlate_filter_taps = xlate_filter_taps
		self.xlating_fir_filter.set_taps((self.xlate_filter_taps))

	def get_width(self):
		return self.width

	def set_width(self, width):
		self.width = width
		self._width_slider.set_value(self.width)
		self._width_text_box.set_value(self.width)
		self.low_pass_filter.set_taps(firdes.low_pass(1, self.samp_rate, self.width/2, self.trans, firdes.WIN_HAMMING, 6.76))

	def get_trans(self):
		return self.trans

	def set_trans(self, trans):
		self.trans = trans
		self._trans_slider.set_value(self.trans)
		self._trans_text_box.set_value(self.trans)
		self.low_pass_filter.set_taps(firdes.low_pass(1, self.samp_rate, self.width/2, self.trans, firdes.WIN_HAMMING, 6.76))

	def get_sql_lev(self):
		return self.sql_lev

	def set_sql_lev(self, sql_lev):
		self.sql_lev = sql_lev
		self.gr_simple_squelch_cc_0.set_threshold(self.sql_lev)
		self._sql_lev_slider.set_value(self.sql_lev)
		self._sql_lev_text_box.set_value(self.sql_lev)

	def get_rx_freq(self):
		return self.rx_freq

	def set_rx_freq(self, rx_freq):
		self.rx_freq = rx_freq
		self._rx_freq_static_text.set_value(self.rx_freq)
		self.fftsink.set_baseband_freq(self.rx_freq*self.display_selector)

	def get_rf_gain(self):
		return self.rf_gain

	def set_rf_gain(self, rf_gain):
		self.rf_gain = rf_gain
		self._rf_gain_slider.set_value(self.rf_gain)
		self._rf_gain_text_box.set_value(self.rf_gain)
		self.fcd_source_c_1.set_lna_gain(self.rf_gain)

	def get_mixer_gain(self):
		return self.mixer_gain

	def set_mixer_gain(self, mixer_gain):
		self.mixer_gain = mixer_gain
		self._mixer_gain_slider.set_value(self.mixer_gain)
		self._mixer_gain_text_box.set_value(self.mixer_gain)
		self.fcd_source_c_1.set_mixer_gain(self.mixer_gain)

	def get_display_selector(self):
		return self.display_selector

	def set_display_selector(self, display_selector):
		self.display_selector = display_selector
		self._display_selector_chooser.set_value(self.display_selector)
		self.fftsink.set_baseband_freq(self.rx_freq*self.display_selector)

	def get_af_gain(self):
		return self.af_gain

	def set_af_gain(self, af_gain):
		self.af_gain = af_gain
		self.gr_multiply_const_vxx_1.set_k((self.af_gain, ))
		self._af_gain_slider.set_value(self.af_gain)
		self._af_gain_text_box.set_value(self.af_gain)

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = fcd_testing_gui_block()
	tb.Run(True)

