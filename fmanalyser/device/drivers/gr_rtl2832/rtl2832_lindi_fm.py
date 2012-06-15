#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: lindi fm
# Author: lindi
# Generated: Fri Jun 15 08:22:58 2012
##################################################

from datetime import datetime
from gnuradio import audio
from gnuradio import blks2
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import window
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
from gnuradio.wxgui import fftsink2
from gnuradio.wxgui import forms
from gnuradio.wxgui import scopesink2
from gnuradio.wxgui import waterfallsink2
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import math
import osmosdr
import threading
import time
import wx

class rtl2832_lindi_fm(grc_wxgui.top_block_gui):

	def __init__(self, ftune=0, mute=-25.0):
		grc_wxgui.top_block_gui.__init__(self, title="lindi fm")
		_icon_path = "/usr/share/icons/hicolor/32x32/apps/gnuradio-grc.png"
		self.SetIcon(wx.Icon(_icon_path, wx.BITMAP_TYPE_ANY))

		##################################################
		# Parameters
		##################################################
		self.ftune = ftune
		self.mute = mute

		##################################################
		# Variables
		##################################################
		self.prefix = prefix = "/tmp/"
		self.frequency = frequency = 91.6e6
		self.finer = finer = ftune
		self.fine = fine = ftune
		self.rf_pwr_lvl = rf_pwr_lvl = 0
		self.recfile = recfile = prefix + datetime.now().strftime("%Y.%m.%d.%H.%M.%S") + ".wav"
		self.cur_freq = cur_freq = frequency+fine+finer
		self.volume = volume = 1.0
		self.variable_static_text_0 = variable_static_text_0 = 10.0*math.log(rf_pwr_lvl+1.0e-11)/math.log(10)
		self.squelch_probe = squelch_probe = 0
		self.sq_thresh = sq_thresh = mute
		self.samp_rate = samp_rate = 3.2e6
		self.record = record = False
		self.gain = gain = 35
		self.freq_txt = freq_txt = cur_freq
		self.freq_offset = freq_offset = 200e3
		self.decim2 = decim2 = 14
		self.decim1 = decim1 = 4
		self.capture_file = capture_file = recfile

		##################################################
		# Blocks
		##################################################
		_sq_thresh_sizer = wx.BoxSizer(wx.VERTICAL)
		self._sq_thresh_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_sq_thresh_sizer,
			value=self.sq_thresh,
			callback=self.set_sq_thresh,
			label="Mute",
			converter=forms.float_converter(),
			proportion=0,
		)
		self._sq_thresh_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_sq_thresh_sizer,
			value=self.sq_thresh,
			callback=self.set_sq_thresh,
			minimum=-50.0,
			maximum=-5.0,
			num_steps=40,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.GridAdd(_sq_thresh_sizer, 0, 1, 1, 1)
		self.input_power = gr.probe_avg_mag_sqrd_c(sq_thresh, 1.0/(samp_rate/10))
		_volume_sizer = wx.BoxSizer(wx.VERTICAL)
		self._volume_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_volume_sizer,
			value=self.volume,
			callback=self.set_volume,
			label="Volume",
			converter=forms.float_converter(),
			proportion=0,
		)
		self._volume_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_volume_sizer,
			value=self.volume,
			callback=self.set_volume,
			minimum=0.0,
			maximum=11.0,
			num_steps=110,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.GridAdd(_volume_sizer, 0, 0, 1, 1)
		def _squelch_probe_probe():
			while True:
				val = self.input_power.unmuted()
				try: self.set_squelch_probe(val)
				except AttributeError, e: pass
				time.sleep(1.0/(10))
		_squelch_probe_thread = threading.Thread(target=_squelch_probe_probe)
		_squelch_probe_thread.daemon = True
		_squelch_probe_thread.start()
		_gain_sizer = wx.BoxSizer(wx.VERTICAL)
		self._gain_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_gain_sizer,
			value=self.gain,
			callback=self.set_gain,
			label='gain',
			converter=forms.int_converter(),
			proportion=0,
		)
		self._gain_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_gain_sizer,
			value=self.gain,
			callback=self.set_gain,
			minimum=0,
			maximum=40,
			num_steps=100,
			style=wx.SL_HORIZONTAL,
			cast=int,
			proportion=1,
		)
		self.GridAdd(_gain_sizer, 1, 10, 1, 1)
		_frequency_sizer = wx.BoxSizer(wx.VERTICAL)
		self._frequency_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_frequency_sizer,
			value=self.frequency,
			callback=self.set_frequency,
			label="Frequency",
			converter=forms.float_converter(),
			proportion=0,
		)
		self._frequency_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_frequency_sizer,
			value=self.frequency,
			callback=self.set_frequency,
			minimum=60e6,
			maximum=1.8e9,
			num_steps=1000,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.GridAdd(_frequency_sizer, 1, 2, 1, 8)
		_finer_sizer = wx.BoxSizer(wx.VERTICAL)
		self._finer_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_finer_sizer,
			value=self.finer,
			callback=self.set_finer,
			label="Fine",
			converter=forms.float_converter(),
			proportion=0,
		)
		self._finer_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_finer_sizer,
			value=self.finer,
			callback=self.set_finer,
			minimum=-100.0e3,
			maximum=100.0e03,
			num_steps=1000,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.GridAdd(_finer_sizer, 1, 1, 1, 1)
		_fine_sizer = wx.BoxSizer(wx.VERTICAL)
		self._fine_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_fine_sizer,
			value=self.fine,
			callback=self.set_fine,
			label="Tune",
			converter=forms.float_converter(),
			proportion=0,
		)
		self._fine_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_fine_sizer,
			value=self.fine,
			callback=self.set_fine,
			minimum=-900.0e3,
			maximum=900.0e03,
			num_steps=1000,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.GridAdd(_fine_sizer, 1, 0, 1, 1)
		self.Main = self.Main = wx.Notebook(self.GetWin(), style=wx.NB_TOP)
		self.Main.AddPage(grc_wxgui.Panel(self.Main), "FFT")
		self.Main.AddPage(grc_wxgui.Panel(self.Main), "Waterfall")
		self.Main.AddPage(grc_wxgui.Panel(self.Main), "Audio")
		self.Add(self.Main)
		self.wxgui_waterfallsink2_1 = waterfallsink2.waterfall_sink_c(
			self.Main.GetPage(1).GetWin(),
			baseband_freq=0,
			dynamic_range=100,
			ref_level=0,
			ref_scale=2.0,
			sample_rate=samp_rate/decim1,
			fft_size=512,
			fft_rate=15,
			average=False,
			avg_alpha=None,
			title="Frequency Xlating FIR Filter",
		)
		self.Main.GetPage(1).Add(self.wxgui_waterfallsink2_1.win)
		self.wxgui_waterfallsink2_0 = waterfallsink2.waterfall_sink_c(
			self.Main.GetPage(1).GetWin(),
			baseband_freq=0,
			dynamic_range=100,
			ref_level=0,
			ref_scale=2.0,
			sample_rate=samp_rate,
			fft_size=512,
			fft_rate=15,
			average=False,
			avg_alpha=None,
			title="Input",
		)
		self.Main.GetPage(1).Add(self.wxgui_waterfallsink2_0.win)
		self.wxgui_scopesink2_0 = scopesink2.scope_sink_f(
			self.Main.GetPage(2).GetWin(),
			title="WBFM Demodulated",
			sample_rate=int(samp_rate/decim1/decim2),
			v_scale=0,
			v_offset=0,
			t_scale=0,
			ac_couple=False,
			xy_mode=False,
			num_inputs=1,
			trig_mode=gr.gr_TRIG_MODE_AUTO,
			y_axis_label="Counts",
		)
		self.Main.GetPage(2).Add(self.wxgui_scopesink2_0.win)
		self.wxgui_fftsink2_1 = fftsink2.fft_sink_c(
			self.Main.GetPage(0).GetWin(),
			baseband_freq=0,
			y_per_div=10,
			y_divs=10,
			ref_level=0,
			ref_scale=2.0,
			sample_rate=samp_rate/decim1,
			fft_size=1024,
			fft_rate=15,
			average=False,
			avg_alpha=None,
			title="Frequency Xlating FIR Filter",
			peak_hold=False,
		)
		self.Main.GetPage(0).Add(self.wxgui_fftsink2_1.win)
		self.wxgui_fftsink2_0 = fftsink2.fft_sink_c(
			self.Main.GetPage(0).GetWin(),
			baseband_freq=0,
			y_per_div=10,
			y_divs=10,
			ref_level=0,
			ref_scale=2.0,
			sample_rate=samp_rate,
			fft_size=1024,
			fft_rate=15,
			average=False,
			avg_alpha=None,
			title="Input",
			peak_hold=False,
		)
		self.Main.GetPage(0).Add(self.wxgui_fftsink2_0.win)
		self._variable_static_text_0_static_text = forms.static_text(
			parent=self.GetWin(),
			value=self.variable_static_text_0,
			callback=self.set_variable_static_text_0,
			label="RF Power ",
			converter=forms.float_converter(formatter=lambda x: "%4.1f" % x),
		)
		self.GridAdd(self._variable_static_text_0_static_text, 0, 4, 1, 1)
		def _rf_pwr_lvl_probe():
			while True:
				val = self.input_power.level()
				try: self.set_rf_pwr_lvl(val)
				except AttributeError, e: pass
				time.sleep(1.0/(2))
		_rf_pwr_lvl_thread = threading.Thread(target=_rf_pwr_lvl_probe)
		_rf_pwr_lvl_thread.daemon = True
		_rf_pwr_lvl_thread.start()
		self._record_check_box = forms.check_box(
			parent=self.GetWin(),
			value=self.record,
			callback=self.set_record,
			label="Record",
			true=True,
			false=False,
		)
		self.GridAdd(self._record_check_box, 0, 5, 1, 1)
		self.osmosdr_source_c_0 = osmosdr.source_c( args="nchan=" + str(1) + " " + ""  )
		self.osmosdr_source_c_0.set_sample_rate(samp_rate)
		self.osmosdr_source_c_0.set_center_freq(frequency+fine+finer, 0)
		self.osmosdr_source_c_0.set_freq_corr(0, 0)
		self.osmosdr_source_c_0.set_gain_mode(0, 0)
		self.osmosdr_source_c_0.set_gain(gain, 0)
		self.gr_wavfile_sink_0_0 = gr.wavfile_sink(recfile, 1, int(samp_rate/decim1/decim2), 8)
		self.gr_multiply_const_vxx_1 = gr.multiply_const_vff((0 if squelch_probe == 0 else 1.0, ))
		self.gr_multiply_const_vxx_0_0 = gr.multiply_const_vff((volume, ))
		self.gr_freq_xlating_fir_filter_xxx_0_0 = gr.freq_xlating_fir_filter_ccc(decim1, (firdes.low_pass(1, samp_rate, 115000, 30000)), 0, samp_rate)
		self._freq_txt_text_box = forms.text_box(
			parent=self.GetWin(),
			value=self.freq_txt,
			callback=self.set_freq_txt,
			label="current",
			converter=forms.float_converter(),
		)
		self.GridAdd(self._freq_txt_text_box, 0, 3, 1, 1)
		self._capture_file_text_box = forms.text_box(
			parent=self.GetWin(),
			value=self.capture_file,
			callback=self.set_capture_file,
			label=" ",
			converter=forms.str_converter(),
		)
		self.GridAdd(self._capture_file_text_box, 0, 6, 1, 6)
		self.blks2_wfm_rcv_0 = blks2.wfm_rcv(
			quad_rate=samp_rate/decim1,
			audio_decimation=decim2,
		)
		self.audio_sink_0 = audio.sink(48000, "", True)

		##################################################
		# Connections
		##################################################
		self.connect((self.gr_multiply_const_vxx_0_0, 0), (self.gr_wavfile_sink_0_0, 0))
		self.connect((self.blks2_wfm_rcv_0, 0), (self.gr_multiply_const_vxx_0_0, 0))
		self.connect((self.osmosdr_source_c_0, 0), (self.gr_freq_xlating_fir_filter_xxx_0_0, 0))
		self.connect((self.osmosdr_source_c_0, 0), (self.wxgui_fftsink2_0, 0))
		self.connect((self.gr_freq_xlating_fir_filter_xxx_0_0, 0), (self.wxgui_fftsink2_1, 0))
		self.connect((self.osmosdr_source_c_0, 0), (self.wxgui_waterfallsink2_0, 0))
		self.connect((self.gr_freq_xlating_fir_filter_xxx_0_0, 0), (self.wxgui_waterfallsink2_1, 0))
		self.connect((self.gr_freq_xlating_fir_filter_xxx_0_0, 0), (self.blks2_wfm_rcv_0, 0))
		self.connect((self.gr_freq_xlating_fir_filter_xxx_0_0, 0), (self.input_power, 0))
		self.connect((self.gr_multiply_const_vxx_0_0, 0), (self.gr_multiply_const_vxx_1, 0))
		self.connect((self.gr_multiply_const_vxx_1, 0), (self.audio_sink_0, 0))
		self.connect((self.blks2_wfm_rcv_0, 0), (self.wxgui_scopesink2_0, 0))

	def get_ftune(self):
		return self.ftune

	def set_ftune(self, ftune):
		self.ftune = ftune
		self.set_fine(self.ftune)
		self.set_finer(self.ftune)

	def get_mute(self):
		return self.mute

	def set_mute(self, mute):
		self.mute = mute
		self.set_sq_thresh(self.mute)

	def get_prefix(self):
		return self.prefix

	def set_prefix(self, prefix):
		self.prefix = prefix
		self.set_recfile(self.prefix + datetime.now().strftime("%Y.%m.%d.%H.%M.%S") + ".wav")

	def get_frequency(self):
		return self.frequency

	def set_frequency(self, frequency):
		self.frequency = frequency
		self.set_cur_freq(self.frequency+self.fine+self.finer)
		self._frequency_slider.set_value(self.frequency)
		self._frequency_text_box.set_value(self.frequency)
		self.osmosdr_source_c_0.set_center_freq(self.frequency+self.fine+self.finer, 0)

	def get_finer(self):
		return self.finer

	def set_finer(self, finer):
		self.finer = finer
		self._finer_slider.set_value(self.finer)
		self._finer_text_box.set_value(self.finer)
		self.set_cur_freq(self.frequency+self.fine+self.finer)
		self.osmosdr_source_c_0.set_center_freq(self.frequency+self.fine+self.finer, 0)

	def get_fine(self):
		return self.fine

	def set_fine(self, fine):
		self.fine = fine
		self._fine_slider.set_value(self.fine)
		self._fine_text_box.set_value(self.fine)
		self.set_cur_freq(self.frequency+self.fine+self.finer)
		self.osmosdr_source_c_0.set_center_freq(self.frequency+self.fine+self.finer, 0)

	def get_rf_pwr_lvl(self):
		return self.rf_pwr_lvl

	def set_rf_pwr_lvl(self, rf_pwr_lvl):
		self.rf_pwr_lvl = rf_pwr_lvl
		self.set_variable_static_text_0(10.0*math.log(self.rf_pwr_lvl+1.0e-11)/math.log(10))

	def get_recfile(self):
		return self.recfile

	def set_recfile(self, recfile):
		self.recfile = recfile
		self.set_capture_file(self.recfile)
		self.gr_wavfile_sink_0_0.open(self.recfile)

	def get_cur_freq(self):
		return self.cur_freq

	def set_cur_freq(self, cur_freq):
		self.cur_freq = cur_freq
		self.set_freq_txt(self.cur_freq)

	def get_volume(self):
		return self.volume

	def set_volume(self, volume):
		self.volume = volume
		self._volume_slider.set_value(self.volume)
		self._volume_text_box.set_value(self.volume)
		self.gr_multiply_const_vxx_0_0.set_k((self.volume, ))

	def get_variable_static_text_0(self):
		return self.variable_static_text_0

	def set_variable_static_text_0(self, variable_static_text_0):
		self.variable_static_text_0 = variable_static_text_0
		self._variable_static_text_0_static_text.set_value(self.variable_static_text_0)

	def get_squelch_probe(self):
		return self.squelch_probe

	def set_squelch_probe(self, squelch_probe):
		self.squelch_probe = squelch_probe
		self.gr_multiply_const_vxx_1.set_k((0 if self.squelch_probe == 0 else 1.0, ))

	def get_sq_thresh(self):
		return self.sq_thresh

	def set_sq_thresh(self, sq_thresh):
		self.sq_thresh = sq_thresh
		self._sq_thresh_slider.set_value(self.sq_thresh)
		self._sq_thresh_text_box.set_value(self.sq_thresh)
		self.input_power.set_threshold(self.sq_thresh)

	def get_samp_rate(self):
		return self.samp_rate

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate
		self.wxgui_fftsink2_0.set_sample_rate(self.samp_rate)
		self.wxgui_waterfallsink2_0.set_sample_rate(self.samp_rate)
		self.gr_freq_xlating_fir_filter_xxx_0_0.set_taps((firdes.low_pass(1, self.samp_rate, 115000, 30000)))
		self.wxgui_waterfallsink2_1.set_sample_rate(self.samp_rate/self.decim1)
		self.wxgui_fftsink2_1.set_sample_rate(self.samp_rate/self.decim1)
		self.input_power.set_alpha(1.0/(self.samp_rate/10))
		self.wxgui_scopesink2_0.set_sample_rate(int(self.samp_rate/self.decim1/self.decim2))
		self.osmosdr_source_c_0.set_sample_rate(self.samp_rate)

	def get_record(self):
		return self.record

	def set_record(self, record):
		self.record = record
		self._record_check_box.set_value(self.record)

	def get_gain(self):
		return self.gain

	def set_gain(self, gain):
		self.gain = gain
		self._gain_slider.set_value(self.gain)
		self._gain_text_box.set_value(self.gain)
		self.osmosdr_source_c_0.set_gain(self.gain, 0)

	def get_freq_txt(self):
		return self.freq_txt

	def set_freq_txt(self, freq_txt):
		self.freq_txt = freq_txt
		self._freq_txt_text_box.set_value(self.freq_txt)

	def get_freq_offset(self):
		return self.freq_offset

	def set_freq_offset(self, freq_offset):
		self.freq_offset = freq_offset

	def get_decim2(self):
		return self.decim2

	def set_decim2(self, decim2):
		self.decim2 = decim2
		self.wxgui_scopesink2_0.set_sample_rate(int(self.samp_rate/self.decim1/self.decim2))

	def get_decim1(self):
		return self.decim1

	def set_decim1(self, decim1):
		self.decim1 = decim1
		self.wxgui_waterfallsink2_1.set_sample_rate(self.samp_rate/self.decim1)
		self.wxgui_fftsink2_1.set_sample_rate(self.samp_rate/self.decim1)
		self.wxgui_scopesink2_0.set_sample_rate(int(self.samp_rate/self.decim1/self.decim2))

	def get_capture_file(self):
		return self.capture_file

	def set_capture_file(self, capture_file):
		self.capture_file = capture_file
		self._capture_file_text_box.set_value(self.capture_file)

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	parser.add_option("", "--ftune", dest="ftune", type="eng_float", default=eng_notation.num_to_str(0),
		help="Set Fine Tuning [default=%default]")
	parser.add_option("", "--mute", dest="mute", type="eng_float", default=eng_notation.num_to_str(-25.0),
		help="Set Mute Level [default=%default]")
	(options, args) = parser.parse_args()
	tb = rtl2832_lindi_fm(ftune=options.ftune, mute=options.mute)
	tb.Run(True)

