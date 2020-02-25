#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: UHD TX DPSK
# Generated: Tue Feb 25 17:18:12 2020
##################################################

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

from PyQt5 import Qt
from PyQt5 import Qt, QtCore
from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import qtgui
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.qtgui import Range, RangeWidget
from optparse import OptionParser
import numpy
import sip
import sys
import time
from gnuradio import qtgui


class uhd_tx_dpsk(gr.top_block, Qt.QWidget):

    def __init__(self, address='serial=307B618', freq=915e6, gain=0, samp_rate=2e6):
        gr.top_block.__init__(self, "UHD TX DPSK")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("UHD TX DPSK")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "uhd_tx_dpsk")

        if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
            self.restoreGeometry(self.settings.value("geometry").toByteArray())
        else:
            self.restoreGeometry(self.settings.value("geometry", type=QtCore.QByteArray))

        ##################################################
        # Parameters
        ##################################################
        self.address = address
        self.freq = freq
        self.gain = gain
        self.samp_rate = samp_rate

        ##################################################
        # Variables
        ##################################################
        self.tun_gain = tun_gain = 50
        self.tun_freq = tun_freq = 915.8e6
        self.samps_per_sym = samps_per_sym = 4
        self.ampl = ampl = 0.1

        ##################################################
        # Blocks
        ##################################################
        self._tun_gain_range = Range(40, 80, 1, 50, 200)
        self._tun_gain_win = RangeWidget(self._tun_gain_range, self.set_tun_gain, 'UHD Tx Gain', "counter_slider", float)
        self.top_layout.addWidget(self._tun_gain_win)
        self._tun_freq_range = Range(914.8e6, 916.8e6, 1, 915.8e6, 200)
        self._tun_freq_win = RangeWidget(self._tun_freq_range, self.set_tun_freq, 'UHD Freq (Hz)', "counter_slider", float)
        self.top_layout.addWidget(self._tun_freq_win)
        self._ampl_range = Range(0, 1, 0.01, 0.1, 200)
        self._ampl_win = RangeWidget(self._ampl_range, self.set_ampl, 'Amplitude', "counter_slider", float)
        self.top_layout.addWidget(self._ampl_win)
        self.uhd_usrp_sink_0 = uhd.usrp_sink(
        	",".join(('', "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_sink_0.set_samp_rate(samp_rate)
        self.uhd_usrp_sink_0.set_center_freq(tun_freq, 0)
        self.uhd_usrp_sink_0.set_gain(tun_gain, 0)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
        	1024, #size
        	firdes.WIN_BLACKMAN_hARRIS, #wintype
        	tun_freq, #fc
        	samp_rate, #bw
        	'Transmit Spectrum', #name
        	1 #number of inputs
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis(-140, 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(True)
        self.qtgui_freq_sink_x_0.enable_grid(False)
        self.qtgui_freq_sink_x_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)

        if not False:
          self.qtgui_freq_sink_x_0.disable_legend()

        if "complex" == "float" or "complex" == "msg_float":
          self.qtgui_freq_sink_x_0.set_plot_pos_half(not True)

        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
                  "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]
        for i in xrange(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_0_win)
        self.digital_dxpsk_mod_0 = digital.dqpsk_mod(
        	samples_per_symbol=samps_per_sym,
        	excess_bw=0.35,
        	mod_code="gray",
        	verbose=False,
        	log=False)

        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vcc((ampl, ))
        self.analog_random_source_x_0 = blocks.vector_source_b(map(int, numpy.random.randint(0, 2**8, 1000)), True)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_random_source_x_0, 0), (self.digital_dxpsk_mod_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.uhd_usrp_sink_0, 0))
        self.connect((self.digital_dxpsk_mod_0, 0), (self.blocks_multiply_const_vxx_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "uhd_tx_dpsk")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_address(self):
        return self.address

    def set_address(self, address):
        self.address = address

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_sink_0.set_samp_rate(self.samp_rate)
        self.qtgui_freq_sink_x_0.set_frequency_range(self.tun_freq, self.samp_rate)

    def get_tun_gain(self):
        return self.tun_gain

    def set_tun_gain(self, tun_gain):
        self.tun_gain = tun_gain
        self.uhd_usrp_sink_0.set_gain(self.tun_gain, 0)


    def get_tun_freq(self):
        return self.tun_freq

    def set_tun_freq(self, tun_freq):
        self.tun_freq = tun_freq
        self.uhd_usrp_sink_0.set_center_freq(self.tun_freq, 0)
        self.qtgui_freq_sink_x_0.set_frequency_range(self.tun_freq, self.samp_rate)

    def get_samps_per_sym(self):
        return self.samps_per_sym

    def set_samps_per_sym(self, samps_per_sym):
        self.samps_per_sym = samps_per_sym

    def get_ampl(self):
        return self.ampl

    def set_ampl(self, ampl):
        self.ampl = ampl
        self.blocks_multiply_const_vxx_0.set_k((self.ampl, ))


def argument_parser():
    parser = OptionParser(usage="%prog: [options]", option_class=eng_option)
    parser.add_option(
        "-a", "--address", dest="address", type="string", default='serial=307B618',
        help="Set serial [default=%default]")
    parser.add_option(
        "-f", "--freq", dest="freq", type="eng_float", default=eng_notation.num_to_str(915e6),
        help="Set Default Frequency [default=%default]")
    parser.add_option(
        "-g", "--gain", dest="gain", type="eng_float", default=eng_notation.num_to_str(0),
        help="Set Default Gain [default=%default]")
    parser.add_option(
        "-s", "--samp-rate", dest="samp_rate", type="eng_float", default=eng_notation.num_to_str(2e6),
        help="Set Sample Rate [default=%default]")
    return parser


def main(top_block_cls=uhd_tx_dpsk, options=None):
    if options is None:
        options, _ = argument_parser().parse_args()

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls(address=options.address, freq=options.freq, gain=options.gain, samp_rate=options.samp_rate)
    tb.start()
    tb.show()

    def quitting():
        tb.stop()
        tb.wait()
    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()
