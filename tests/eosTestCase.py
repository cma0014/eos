#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
#
# This file is part of Eos.
#
# Eos is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Eos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Eos. If not, see <http://www.gnu.org/licenses/>.
#===============================================================================


from logging import getLogger
from logging.handlers import BufferingHandler
from unittest import TestCase

from .environment import CacheHandler


class TestLogHandler(BufferingHandler):
    """
    Custom logging handler class which helps to
    check log output without unnecessary actual
    output.
    """
    def __init__(self):
        # Capacity is zero, as we won't rely on
        # it when deciding when to flush data
        BufferingHandler.__init__(self, 0)

    def shouldFlush(self):
        return False

    def emit(self, record):
        self.buffer.append(record)


class EosTestCase(TestCase):
    """
    Custom test case class, which incorporates several
    environment changes for ease of test process, namely:

    self.log -- access to output generated by logging
    facility during test.

    When overriding setUp and tearDown methods, make sure
    to call this class' original methods (before anything
    else is done for setUp, and after for tearDown).

    Also make sure to use eos_test logger as root for
    logging any data.
    """

    def setUp(self):
        # Save existing loggers for eos_test loggers
        self.__removedLogHandlers = []
        logger = getLogger('eos_test')
        for handler in logger.handlers:
            self.__removedLogHandlers.append(handler)
            logger.removeHandler(handler)
        # Place test logger instead of them
        self.__testLogHandler = TestLogHandler()
        logger.addHandler(self.__testLogHandler)
        # Add cache handler to each test case
        self.ch = CacheHandler()

    def tearDown(self):
        # Remove test logger and restore loggers which
        # were removed during setup
        logger = getLogger('eos_test')
        logger.removeHandler(self.__testLogHandler)
        self.__testLogHandler.close()
        for handler in self.__removedLogHandlers:
            logger.addHandler(handler)

    @property
    def log(self):
        return self.__testLogHandler.buffer
