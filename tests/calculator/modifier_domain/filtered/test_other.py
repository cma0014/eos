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


import logging

from eos.const.eos import State, Domain, Scope, FilterType, Operator
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import Modifier
from tests.calculator.calculator_testcase import CalculatorTestCase
from tests.calculator.environment import IndependentItem


class TestDomainFilterOther(CalculatorTestCase):
    """Test domain.other for filtered modifications"""

    def test_error(self):
        tgt_attr = self.ch.attribute(attribute_id=1)
        src_attr = self.ch.attribute(attribute_id=2)
        modifier = Modifier()
        modifier.state = State.offline
        modifier.scope = Scope.local
        modifier.src_attr = src_attr.id
        modifier.operator = Operator.post_percent
        modifier.tgt_attr = tgt_attr.id
        modifier.domain = Domain.other
        modifier.filter_type = FilterType.all_
        modifier.filter_value = None
        effect = self.ch.effect(effect_id=1, category=EffectCategory.passive)
        effect.modifiers = (modifier,)
        influence_source = IndependentItem(self.ch.type_(
            type_id=90, effects=(effect,), attributes={src_attr.id: 20}))
        # Charge's container or module's charge can't be 'owner'
        # of other holders, thus such modification type is unsupported
        self.fit.items.add(influence_source)
        self.assertEqual(len(self.log), 2)
        for log_record in self.log:
            self.assertEqual(log_record.name, 'eos.fit.calculator.register')
            self.assertEqual(log_record.levelno, logging.WARNING)
            self.assertEqual(
                log_record.msg,
                'malformed modifier on item 90: unsupported target domain '
                '{} for filtered modification'.format(Domain.other)
            )
        self.fit.items.remove(influence_source)
        self.assert_calculator_buffers_empty(self.fit)
