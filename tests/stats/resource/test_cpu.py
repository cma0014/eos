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

from eos.const.eos import Domain, State
from eos.const.eve import Attribute
from eos.fit.holder.item import ModuleHigh, Ship, Implant
from tests.stats.stat_testcase import StatTestCase


class TestCpu(StatTestCase):
    """Check functionality of cpu stats"""

    def test_output(self):
        # Check that modified attribute of ship is used
        ship_item = self.ch.type_(type_id=1, attributes={Attribute.cpu_output: 10})
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        ship_holder.attributes = {Attribute.cpu_output: 50}
        self.set_ship(ship_holder)
        self.assertEqual(self.ss.cpu.output, 50)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_output_no_ship(self):
        # None for output when no ship
        self.assertIsNone(self.ss.cpu.output)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_output_no_attr(self):
        # None for output when no attribute on ship
        ship_item = self.ch.type_(type_id=1)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        ship_holder.attributes = {}
        self.set_ship(ship_holder)
        self.assertIsNone(self.ss.cpu.output)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_single_rounding_up(self):
        item = self.ch.type_(type_id=1, attributes={Attribute.cpu: 0})
        holder = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder.attributes = {Attribute.cpu: 55.5555555555}
        self.add_holder(holder)
        self.assertEqual(self.ss.cpu.used, 55.56)
        self.remove_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_single_rounding_down(self):
        item = self.ch.type_(type_id=1, attributes={Attribute.cpu: 0})
        holder = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder.attributes = {Attribute.cpu: 44.4444444444}
        self.add_holder(holder)
        self.assertEqual(self.ss.cpu.used, 44.44)
        self.remove_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_multiple(self):
        item = self.ch.type_(type_id=1, attributes={Attribute.cpu: 0})
        holder1 = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder1.attributes = {Attribute.cpu: 50}
        self.add_holder(holder1)
        holder2 = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder2.attributes = {Attribute.cpu: 30}
        self.add_holder(holder2)
        self.assertEqual(self.ss.cpu.used, 80)
        self.remove_holder(holder1)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_negative(self):
        item = self.ch.type_(type_id=1, attributes={Attribute.cpu: 0})
        holder1 = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder1.attributes = {Attribute.cpu: 50}
        self.add_holder(holder1)
        holder2 = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder2.attributes = {Attribute.cpu: -30}
        self.add_holder(holder2)
        self.assertEqual(self.ss.cpu.used, 20)
        self.remove_holder(holder1)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_none(self):
        self.assertEqual(self.ss.cpu.used, 0)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_state(self):
        item = self.ch.type_(type_id=1, attributes={Attribute.cpu: 0})
        holder1 = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder1.attributes = {Attribute.cpu: 50}
        self.add_holder(holder1)
        holder2 = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder2.attributes = {Attribute.cpu: 30}
        self.add_holder(holder2)
        self.assertEqual(self.ss.cpu.used, 50)
        self.remove_holder(holder1)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_other_class_domain(self):
        item = self.ch.type_(type_id=1, attributes={Attribute.cpu: 0})
        holder1 = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder1.attributes = {Attribute.cpu: 50}
        self.add_holder(holder1)
        holder2 = Mock(state=State.online, item=item, _domain=Domain.character, spec_set=Implant(1))
        holder2.attributes = {Attribute.cpu: 30}
        self.add_holder(holder2)
        self.assertEqual(self.ss.cpu.used, 80)
        self.remove_holder(holder1)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_cache(self):
        ship_item = self.ch.type_(type_id=1, attributes={Attribute.cpu_output: 10})
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        ship_holder.attributes = {Attribute.cpu_output: 50}
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=2, attributes={Attribute.cpu: 0})
        holder1 = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder1.attributes = {Attribute.cpu: 50}
        self.add_holder(holder1)
        holder2 = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder2.attributes = {Attribute.cpu: 30}
        self.add_holder(holder2)
        self.assertEqual(self.ss.cpu.used, 80)
        self.assertEqual(self.ss.cpu.output, 50)
        holder1.attributes[Attribute.cpu] = 10
        ship_holder.attributes[Attribute.cpu_output] = 60
        self.assertEqual(self.ss.cpu.used, 80)
        self.assertEqual(self.ss.cpu.output, 50)
        self.set_ship(None)
        self.remove_holder(holder1)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_volatility(self):
        ship_item = self.ch.type_(type_id=1, attributes={Attribute.cpu_output: 10})
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        ship_holder.attributes = {Attribute.cpu_output: 50}
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=2, attributes={Attribute.cpu: 0})
        holder1 = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder1.attributes = {Attribute.cpu: 50}
        self.add_holder(holder1)
        holder2 = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder2.attributes = {Attribute.cpu: 30}
        self.add_holder(holder2)
        self.assertEqual(self.ss.cpu.used, 80)
        self.assertEqual(self.ss.cpu.output, 50)
        holder1.attributes[Attribute.cpu] = 10
        ship_holder.attributes[Attribute.cpu_output] = 60
        self.ss._clear_volatile_attrs()
        self.assertEqual(self.ss.cpu.used, 40)
        self.assertEqual(self.ss.cpu.output, 60)
        self.set_ship(None)
        self.remove_holder(holder1)
        self.remove_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()
