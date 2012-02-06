#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2012 Anton Vorobyov
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


from unittest import TestCase

from eos.const import State, Location, Context, RunTime, Operator, SourceType
from eos.fit.attributeCalculator.info.info import Info
from eos.eve.attribute import Attribute
from eos.eve.const import EffectCategory
from eos.eve.effect import Effect
from eos.eve.type import Type
from eos.tests.attributeCalculator.environment import Fit, IndependentItem


class TestLocationDirectCharacterSwitch(TestCase):
    """Test direct modification of character when it's changed"""

    def testCharacter(self):
        tgtAttr = Attribute(1)
        srcAttr = Attribute(2)
        info = Info()
        info.state = State.offline
        info.context = Context.local
        info.runTime = RunTime.duration
        info.gang = False
        info.location = Location.character
        info.filterType = None
        info.filterValue = None
        info.operator = Operator.postPercent
        info.targetAttributeId = tgtAttr.id
        info.sourceType = SourceType.attribute
        info.sourceValue = srcAttr.id
        effect = Effect(1, EffectCategory.passive)
        effect._Effect__infos = {info}
        fit = Fit(lambda attrId: {tgtAttr.id: tgtAttr, srcAttr.id: srcAttr}[attrId])
        influenceSource = IndependentItem(Type(1, effects={effect}, attributes={srcAttr.id: 20}))
        fit._addHolder(influenceSource)
        influenceTarget1 = IndependentItem(Type(2, attributes={tgtAttr.id: 100}))
        fit.character = influenceTarget1
        fit._addHolder(influenceTarget1)
        notExpValue = 100
        self.assertNotAlmostEqual(influenceTarget1.attributes[tgtAttr.id], notExpValue, msg="value must be modified")
        fit._removeHolder(influenceTarget1)
        fit.character = None
        influenceTarget2 = IndependentItem(Type(3, attributes={tgtAttr.id: 100}))
        fit.character = influenceTarget2
        fit._addHolder(influenceTarget2)
        notExpValue = 100
        self.assertNotAlmostEqual(influenceTarget2.attributes[tgtAttr.id], notExpValue, msg="value must be modified")