# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2017 Anton Vorobyov
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
# ===============================================================================


from tests.eos_testcase import EosTestCase
from .environment import FitAssertion


class ContainerTestCase(EosTestCase):
    """
    Additional functionality provided:

    self.assert_fit_buffers_empty -- checks if fit has any
    holders assigned to it
    self.fit_assertions -- returns context manager which
    turns on on-fit per-message type assertions
    """

    def assert_fit_buffers_empty(self, fit):
        holder_num = self._get_object_buffer_entry_amount(fit, ignore=('_message_assertions',))
        if holder_num > 0:
            plu = 'y' if holder_num == 1 else 'ies'
            msg = '{} entr{} in buffers: buffers must be empty'.format(holder_num, plu)
            self.fail(msg=msg)

    def fit_assertions(self, fit):
        return FitAssertion(fit)
