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


from eos.const import Location
from eos.fit.holder import MutableAttributeHolder


class Skill(MutableAttributeHolder):
    """
    Represents skill with all its special properties.

    Positional arguments:
    type_ -- type (item), on which skill is based
    """

    __slots__ = ("__level",)

    def __init__(self, type_):
        MutableAttributeHolder.__init__(self, type_)
        self.__level = 0

    @property
    def _location(self):
        return Location.character

    @property
    def level(self):
        return self.__level

    @level.setter
    def level(self, value):
        self.__level = value
