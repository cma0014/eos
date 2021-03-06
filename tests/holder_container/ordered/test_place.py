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


from unittest.mock import Mock

from eos.const.eos import State
from eos.fit.holder.container import HolderList, SlotTakenError
from eos.fit.messages import HolderAdded, HolderRemoved
from tests.holder_container.environment import Fit, Holder, OtherHolder
from tests.holder_container.container_testcase import ContainerTestCase


class TestContainerOrderedPlace(ContainerTestCase):

    def make_fit(self):
        assertions = {
            HolderAdded: lambda f, m: self.assertIn(m.holder, f.container),
            HolderRemoved: lambda f, m: self.assertIn(m.holder, f.container)
        }
        fit = Fit(self, message_assertions=assertions)
        fit.container = HolderList(fit, Holder)
        return fit

    def test_holder_outside(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=Holder(1))
        holder2 = Mock(_fit=None, state=State.active, spec_set=Holder(1))
        fit.container.append(holder1)
        # Action
        with self.fit_assertions(fit):
            fit.container.place(3, holder2)
        # Checks
        self.assertIs(len(fit.container), 4)
        self.assertIs(fit.container[0], holder1)
        self.assertIsNone(fit.container[1])
        self.assertIsNone(fit.container[2])
        self.assertIs(fit.container[3], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_none_outside(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, state=State.active, spec_set=Holder(1))
        fit.container.append(holder)
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(TypeError, fit.container.place, 3, None)
        # Checks
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], holder)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.container.remove(holder)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_holder_onto_none(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=Holder(1))
        holder2 = Mock(_fit=None, state=State.overload, spec_set=Holder(1))
        holder3 = Mock(_fit=None, state=State.overload, spec_set=Holder(1))
        fit.container.append(holder1)
        fit.container.insert(3, holder2)
        # Action
        with self.fit_assertions(fit):
            fit.container.place(1, holder3)
        # Checks
        self.assertIs(len(fit.container), 4)
        self.assertIs(fit.container[0], holder1)
        self.assertIs(fit.container[1], holder3)
        self.assertIsNone(fit.container[2])
        self.assertIs(fit.container[3], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        self.assertIs(holder3._fit, fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        fit.container.remove(holder3)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_none_onto_none(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=Holder(1))
        holder2 = Mock(_fit=None, state=State.offline, spec_set=Holder(1))
        fit.container.append(holder1)
        fit.container.insert(3, holder2)
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(TypeError, fit.container.place, 1, None)
        # Checks
        self.assertIs(len(fit.container), 4)
        self.assertIs(fit.container[0], holder1)
        self.assertIsNone(fit.container[1])
        self.assertIsNone(fit.container[2])
        self.assertIs(fit.container[3], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_holder_onto_holder(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.overload, spec_set=Holder(1))
        holder2 = Mock(_fit=None, state=State.active, spec_set=Holder(1))
        fit.container.append(holder1)
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(SlotTakenError, fit.container.place, 0, holder2)
        # Checks
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        # Misc
        fit.container.remove(holder1)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_none_onto_holder(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, state=State.offline, spec_set=Holder(1))
        fit.container.append(holder)
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(TypeError, fit.container.place, 0, None)
        # Checks
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], holder)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.container.remove(holder)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_holder_outside_type_failure(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, state=State.overload, spec_set=OtherHolder(1))
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(TypeError, fit.container.place, 2, holder)
        # Checks
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_holder_outside_value_failure(self):
        fit = self.make_fit()
        fit_other = self.make_fit()
        holder = Mock(_fit=None, state=State.overload, spec_set=Holder(1))
        fit_other.container.append(holder)
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(ValueError, fit.container.place, 2, holder)
        # Checks
        self.assertIs(len(fit.container), 0)
        self.assertIs(len(fit_other.container), 1)
        self.assertIs(fit_other.container[0], holder)
        self.assertIs(holder._fit, fit_other)
        # Misc
        fit_other.container.remove(holder)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)
        self.assert_fit_buffers_empty(fit_other)
        self.assert_object_buffers_empty(fit_other.container)

    def test_holder_onto_none_type_failure(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=Holder(1))
        holder2 = Mock(_fit=None, state=State.online, spec_set=OtherHolder(1))
        fit.container.insert(1, holder1)
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(TypeError, fit.container.place, 0, holder2)
        # Checks
        self.assertIs(len(fit.container), 2)
        self.assertIsNone(fit.container[0])
        self.assertIs(fit.container[1], holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        # Misc
        fit.container.remove(holder1)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_holder_onto_none_value_failure(self):
        fit = self.make_fit()
        fit_other = self.make_fit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=Holder(1))
        holder2 = Mock(_fit=None, state=State.online, spec_set=Holder(1))
        fit.container.insert(1, holder1)
        fit_other.container.append(holder2)
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(ValueError, fit.container.place, 0, holder2)
        # Checks
        self.assertIs(len(fit.container), 2)
        self.assertIsNone(fit.container[0])
        self.assertIs(fit.container[1], holder1)
        self.assertIs(len(fit_other.container), 1)
        self.assertIs(fit_other.container[0], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit_other)
        # Misc
        fit.container.remove(holder1)
        fit_other.container.remove(holder2)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)
        self.assert_fit_buffers_empty(fit_other)
        self.assert_object_buffers_empty(fit_other.container)
