
from electrum.i18n import _
from electrum.bitcoin import FEE_TARGETS

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QSlider, QToolTip

import threading

class FeeSlider(QSlider):

    def __init__(self, window, config, callback):
        QSlider.__init__(self, Qt.Horizontal)
        self.config = config
        self.window = window
        self.callback = callback
        self.dyn = False
        self.lock = threading.RLock()
        self.update()
        self.valueChanged.connect(self.moved)

    def moved(self, pos):
        with self.lock:
            fee_rate = self.config.dynfee(pos) if self.dyn else self.config.static_fee(pos)
            tooltip = self.get_tooltip(pos, fee_rate)
            QToolTip.showText(QCursor.pos(), tooltip, self)
            self.setToolTip(tooltip)
            self.callback(self.dyn, pos, fee_rate)

    def get_tooltip(self, pos, fee_rate):
        rate_str = self.window.format_fee_rate(fee_rate) if fee_rate else _('unknown')
        if self.dyn:
            depth = self.config.depth_target(pos)
            tooltip = self.config.fee_tooltip(depth) + '\n' + rate_str
        else:
            tooltip = 'Fixed rate: ' + rate_str
            if self.config.has_fee_estimates():
                i = self.config.reverse_dynfee(fee_rate)
                tooltip += '\n' + self.config.fee_tooltip(i)
        return tooltip

    def update(self):
        with self.lock:
            self.dyn = self.config.is_dynfee()
            if self.dyn:
                pos = self.config.get('fee_level', 2)
                fee_rate = self.config.dynfee(pos)
                self.setRange(0, len(FEE_TARGETS)-1)
                self.setValue(pos)
            else:
                fee_rate = self.config.fee_per_kb()
                pos = self.config.static_fee_index(fee_rate)
                self.setRange(0, 9)
                self.setValue(pos)
            tooltip = self.get_tooltip(pos, fee_rate)
            self.setToolTip(tooltip)
