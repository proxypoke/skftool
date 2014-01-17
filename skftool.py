#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# skftool - may the weeaboo be with you
#
# Author: slowpoke <mail+git@slowpoke.io>
#
# This program is Free Software under the non-terms
# of the Anti-License. Do whatever the fuck you want.
#
# Github: https://www.github.com/proxypoke/skftool

"""skftool - the sophisticated weeaboo's random anime selector."""

import os
import re
import sys

from subprocess import Popen
from collections import namedtuple
from random import choice

from PyQt4 import uic, QtGui, QtCore

# for now, we use a canonical name for the info image
IMAGE_NAME = "info.png"

# the default maximum amount of columns for series entries
MAX_COLS = 3

# regex to find the first episode
first_episode = re.compile("0+1").search

Series = namedtuple("Series",
                    ["name",
                     "directory",
                     "image"])


def play(video):
    """Play a file with mpv."""
    Popen(["mpv", video])


def load_series_from_directory(directory):
    """Create a new Series object from a directory name."""
    directory = directory.rstrip("/")
    name = os.path.basename(directory)
    image = os.path.join(
        directory,
        IMAGE_NAME)
    return Series(name, directory, image)


def load_season(directory):
    """Load an entire directory of series."""
    return [load_series_from_directory(os.path.join(directory, s))
            for s in os.listdir(directory)]


def get_first_episode(series):
    """Return the filepath of the first episode for the given series."""
    return os.path.join(
        series.directory,
        next(filter(first_episode, os.listdir(series.directory)), None))


def main():
    progr = QtGui.QApplication(sys.argv)

    main_window = uic.loadUi("ui/skftool.ui")
    main_window.setWindowTitle("Season Kickoff Frenzy!")

    series_area = main_window.findChild(object, "series_area")

    series_list = dict()

    animu_counter = main_window.findChild(object, "animu_counter")

    column_setting = main_window.findChild(object, "column_setting")
    column_setting.setValue(MAX_COLS)

    class SeriesWidget(QtGui.QLabel):

        clicked = QtCore.pyqtSignal()
        series = None

        def __init__(self, series):
            super(SeriesWidget, self).__init__()
            self.series = series
            self.clicked.connect(self.play_and_remove)

        def mouseReleaseEvent(self, ev):
            if ev.button() == QtCore.Qt.LeftButton:
                self.clicked.emit()
            else:
                self.remove()

        def play_and_remove(self):
            # TODO: Error reporting
            play(get_first_episode(self.series))
            self.remove()

        def remove(self):
            self.setParent(None)
            del series_list[self.series]
            animu_counter.display(animu_counter.intValue() - 1)
            reorder()

    def add_series():
        dir_ = str(QtGui.QFileDialog.getExistingDirectory(
            main_window,
            "Choose a series directory",
            "/home/slowpoke/animu"))
        if dir_ == "":
            # no file has been chosen, do nothing
            return
        if not os.path.isdir(dir_):
            QtGui.QErrorMessage(main_window).showMessage(
                " ".join([
                    "The given file does not exist or is not a directory:",
                    dir_]))
            return
        s = load_series_from_directory(dir_)
        add_series_widget(s)

    def add_season():
        dir_ = str(QtGui.QFileDialog.getExistingDirectory(
            main_window,
            "Choose a season directory",
            "/home/slowpoke/animu"))
        if dir_ == "":
            # no file has been chosen, do nothing
            return
        if not os.path.isdir(dir_):
            QtGui.QErrorMessage(main_window).showMessage(
                " ".join([
                    "The given file does not exist or is not a directory:",
                    dir_]))
            return
        for series in load_season(dir_):
            add_series_widget(series)

    def add_series_widget(series):

        if series in series_list:
            # duplicate series
            return

        series_widget = SeriesWidget(series)
        series_list[series] = series_widget
        series_area.addWidget(
            series_widget,
            series_area.count() // MAX_COLS,
            series_area.count() % MAX_COLS)

        animu_counter.display(animu_counter.intValue() + 1)

        # TODO: Placeholder image
        if not os.path.isfile(series.image):
            series_widget.setText(series.name)
            return

        image = QtGui.QPixmap(series.image)
        series_widget.setPixmap(image)

        # prevent the widget from getting resized
        series_widget.setMinimumSize(image.size())

    def reorder(cols=MAX_COLS):
        widgets = [series_area.takeAt(0).widget()
                   for _ in range(series_area.count())]
        for w in widgets:
            series_area.addWidget(
                w,
                series_area.count() // cols,
                series_area.count() % cols)

    def frenzy():
        series_widget = choice(list(series_list.values()))

        w = uic.loadUi("ui/random_result.ui")
        w.setWindowTitle("Zufallsgeneratustra")

        image_label = w.findChild(object, "image")
        image = QtGui.QPixmap(series_widget.series.image)
        image_label.setPixmap(image)

        w.adjustSize()

        text_label = w.findChild(object, "text")
        # this must be set from code for some reason...
        text_label.setAlignment(QtCore.Qt.AlignCenter)

        if w.exec_():
            series_widget.play_and_remove()

    add_series_button = main_window.findChild(object, "add_series_button")
    add_series_button.clicked.connect(add_series)

    add_season_button = main_window.findChild(object, "add_season_button")
    add_season_button.clicked.connect(add_season)

    frenzy_button = main_window.findChild(object, "frenzy_button")
    frenzy_button.clicked.connect(frenzy)

    column_setting.valueChanged.connect(reorder)

    main_window.show()

    sys.exit(progr.exec_())


if __name__ == "__main__":
    main()
