# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

# Copyright 2014 Florian Bruhin (The Compiler) <mail@qutebrowser.org>
#
# This file is part of qutebrowser.
#
# qutebrowser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# qutebrowser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with qutebrowser.  If not, see <http://www.gnu.org/licenses/>.

"""Command history for the status bar."""

from PyQt5.QtCore import pyqtSlot, QCoreApplication

from qutebrowser.utils.usertypes import NeighborList
from qutebrowser.utils.log import statusbar as logger


class HistoryEmptyError(Exception):

    """Raised when the history is empty."""

    pass


class HistoryEndReachedError(Exception):

    """Raised when the end of the history is reached."""

    pass


class History:

    """Command history.

    Attributes:
        browsing: If we're currently browsing the history (property).
        _history: A list of executed commands, with newer commands at the end.
        _tmphist: Temporary history for history browsing (as NeighborList)
    """

    def __init__(self):
        self._tmphist = None
        history = QCoreApplication.instance().cmd_history.data
        if history is None:
            self._history = []
        else:
            self._history = history

    def __getitem__(self, idx):
        return self._history[idx]

    @property
    def browsing(self):
        """Check _tmphist to see if we're browsing."""
        return self._tmphist is not None

    def start(self, text):
        """Start browsing to the history.

        Called when the user presses the up/down key and wasn't browsing the
        history already.

        Args:
            text: The preset text.
        """
        logger.debug("Preset text: '{}'".format(text))
        if text:
            items = [e for e in self._history if e.startswith(text)]
        else:
            items = self._history
        if not items:
            raise HistoryEmptyError
        self._tmphist = NeighborList(items)
        return self._tmphist.lastitem()

    @pyqtSlot()
    def stop(self):
        """Stop browsing the history."""
        self._tmphist = None

    def previtem(self):
        """Get the previous item in the temp history.

        start() needs to be called before calling this.

        Raise:
            ValueError if start() wasn't called.
            HistoryEndReachedError if the first item was reached.
        """
        if not self.browsing:
            raise ValueError("Currently not browsing history")
        try:
            return self._tmphist.previtem()
        except IndexError:
            raise HistoryEndReachedError

    def nextitem(self):
        """Get the next item in the temp history.

        start() needs to be called before calling this.

        Raise:
            ValueError if start() wasn't called.
            HistoryEndReachedError if the last item was reached.
        """
        if not self.browsing:
            raise ValueError("Currently not browsing history")
        try:
            return self._tmphist.nextitem()
        except IndexError:
            raise HistoryEndReachedError

    def append(self, text):
        """Append a new item to the history.

        Args:
            text: The text to append.
        """
        if not self._history or text != self._history[-1]:
            self._history.append(text)
