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


from eos.const.eos import State, Location, Context, Operator
from eos.const.eve import EffectCategory
from eos.data.cache.object.modifier import Modifier
from eos.tests.attribute_calculator.attrcalc_testcase import AttrCalcTestCase
from eos.tests.attribute_calculator.environment import IndependentItem
from eos.tests.environment import Logger


class TestOperatorUnknown(AttrCalcTestCase):
    """Test unknown operator type"""

    def test_log_other(self):
        # Check how unknown operator value influences
        # attribute calculator
        tgt_attr = self.ch.attribute(attribute_id=1)
        src_attr = self.ch.attribute(attribute_id=2)
        invalid_modifier = Modifier()
        invalid_modifier.state = State.offline
        invalid_modifier.context = Context.local
        invalid_modifier.source_attribute_id = src_attr.id
        invalid_modifier.operator = 1008
        invalid_modifier.target_attribute_id = tgt_attr.id
        invalid_modifier.location = Location.self_
        invalid_modifier.filter_type = None
        invalid_modifier.filter_value = None
        effect = self.ch.effect(effect_id=1, category_id=EffectCategory.passive)
        effect.modifiers = (invalid_modifier,)
        holder = IndependentItem(self.ch.type_(type_id=83, effects=(effect,),
                                               attributes={src_attr.id: 1.2, tgt_attr.id: 100}))
        self.fit.items.add(holder)
        self.assertAlmostEqual(holder.attributes[tgt_attr.id], 100)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos_test.attribute_calculator')
        self.assertEqual(log_record.levelno, Logger.WARNING)
        self.assertEqual(log_record.msg, 'malformed modifier on item 83: unknown operator 1008')
        self.fit.items.remove(holder)
        self.assert_link_buffers_empty(self.fit)

    def test_log_unorderable_combination(self):
        # Check how non-orderable operator value influences
        # attribute calculator. Previously, bug in calculation
        # method made it to crash
        tgt_attr = self.ch.attribute(attribute_id=1)
        src_attr = self.ch.attribute(attribute_id=2)
        invalid_modifier = Modifier()
        invalid_modifier.state = State.offline
        invalid_modifier.context = Context.local
        invalid_modifier.source_attribute_id = src_attr.id
        invalid_modifier.operator = None
        invalid_modifier.target_attribute_id = tgt_attr.id
        invalid_modifier.location = Location.self_
        invalid_modifier.filter_type = None
        invalid_modifier.filter_value = None
        valid_modifier = Modifier()
        valid_modifier.state = State.offline
        valid_modifier.context = Context.local
        valid_modifier.source_attribute_id = src_attr.id
        valid_modifier.operator = Operator.post_mul
        valid_modifier.target_attribute_id = tgt_attr.id
        valid_modifier.location = Location.self_
        valid_modifier.filter_type = None
        valid_modifier.filter_value = None
        effect = self.ch.effect(effect_id=1, category_id=EffectCategory.passive)
        effect.modifiers = (invalid_modifier, valid_modifier)
        holder = IndependentItem(self.ch.type_(type_id=83, effects=(effect,),
                                               attributes={src_attr.id: 1.2, tgt_attr.id: 100}))
        self.fit.items.add(holder)
        self.assertAlmostEqual(holder.attributes[tgt_attr.id], 120)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos_test.attribute_calculator')
        self.assertEqual(log_record.levelno, Logger.WARNING)
        self.assertEqual(log_record.msg, 'malformed modifier on item 83: unknown operator None')
        self.fit.items.remove(holder)
        self.assert_link_buffers_empty(self.fit)

    def test_combination(self):
        tgt_attr = self.ch.attribute(attribute_id=1)
        src_attr = self.ch.attribute(attribute_id=2)
        invalid_modifier = Modifier()
        invalid_modifier.state = State.offline
        invalid_modifier.context = Context.local
        invalid_modifier.source_attribute_id = src_attr.id
        invalid_modifier.operator = 1008
        invalid_modifier.target_attribute_id = tgt_attr.id
        invalid_modifier.location = Location.self_
        invalid_modifier.filter_type = None
        invalid_modifier.filter_value = None
        valid_modifier = Modifier()
        valid_modifier.state = State.offline
        valid_modifier.context = Context.local
        valid_modifier.source_attribute_id = src_attr.id
        valid_modifier.operator = Operator.post_mul
        valid_modifier.target_attribute_id = tgt_attr.id
        valid_modifier.location = Location.self_
        valid_modifier.filter_type = None
        valid_modifier.filter_value = None
        effect = self.ch.effect(effect_id=1, category_id=EffectCategory.passive)
        effect.modifiers = (invalid_modifier, valid_modifier)
        holder = IndependentItem(self.ch.type_(type_id=1, effects=(effect,),
                                               attributes={src_attr.id: 1.5, tgt_attr.id: 100}))
        self.fit.items.add(holder)
        # Make sure presence of invalid operator doesn't prevent
        # from calculating value based on valid modifiers
        self.assertNotAlmostEqual(holder.attributes[tgt_attr.id], 100)
        self.fit.items.remove(holder)
        self.assertEqual(len(self.log), 1)
        self.assert_link_buffers_empty(self.fit)
