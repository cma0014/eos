#===============================================================================
# Copyright (C) 2011 Diego Duclos
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

from eos import const

class Register():
    """
    Register class. Keeps track of fit specific
    """
    def __init__(self, fit):
        self.__fit = fit
        """The fit we're keeping track of things for"""

        self.__affectorSpecificLocation = {}
        """
        Stores all (sourceHolder, info) tuples that directly affect a certain location.
        Key: locationId
        Value: set of (sourceHolder, info) tuples
        """

        self.__affectorAllLocation = {}
        """
        Stores all (sourceHolder, info) tuples that affect all holders in a certain location
        Key: locationId
        Value: set of (sourceHolder, info) tuples
        """

        self.__affectorGroupLocation = {}
        """
        Stores all (sourceHolder, info) tuples that affect everything in a certain location using a certain group-based filter
        Key: (locationId, groupId)
        Value: set of (sourceHolder, info) tuples
        """

        self.__affectorSkillLocation = {}
        """
        Stores all (sourceHolder, info) tuples that affect everything in a certain location using a certain skill-based filter
        Key: (locationId, skillId)
        Value: set of (sourceHolder, info) tuples
        """

        self.__affecteeLocation = {}
        """
        Stores all affectees in a certain location
        Key: locationId:
        Value: set of holders
        """

        self.__affecteeGroupLocation = {}
        """
        Stores all holders per location, per group
        Key: (locationId, groupId)
        Value: set of holders
        """

        self.__affecteeSkillLocation = {}
        """
        Stores all holders per location, per skill
        Key: (locationId, skillId)
        Value: set of holders
        """

    def __getMaps(self, holder):
        location = holder.location

        # Keep all maps we need to add all info tuples to here to do it as efficiently as possible
        # These are basicly fillup maps and are iterated through afterwards to fill up the registers
        affecteeMaps = [(location, self.__affecteeLocation), # Location only register
                        ((location, holder.type.groupId), self.__affecteeGroupLocation)] # Location group register

        affectorMaps = [(location, self.__affectorSpecificLocation), # Specific location register
                        (location, self.__affectorAllLocation), # all location register
                        ((location, holder.type.groupId), self.__affectorGroupLocation)] #group location register

        # Location skill register mapkeys
        affecteeSkillLocation = self.__affecteeSkillLocation
        affectorSkillLocation = self.__affectorSkillLocation

        # Add the skills to the affectee/affector fillup maps
        for skillId in holder.type.requiredSkills():
            key = (location, skillId)

            affecteeMaps.append((key, affecteeSkillLocation))
            affectorMaps.append((key, affectorSkillLocation))

        return (affecteeMaps, affectorMaps)

    def register(self, holder):
        affecteeMaps, affectorMaps = self.__getMaps(holder)

        # Add to affectee registers first
        for key, map in affecteeMaps:
            s = map.get(key)
            if s is None:
                s = map[key] = set()

            s.add(holder)

        # Now add to affector register the same way, except we also loop through infos to compose the values
        for info in holder.type.getInfos():
            value = (holder, info)
            for key, map in affectorMaps:
                s = map.get(key)
                if s is None:
                    s = map[key] = set()

                s.add(value)

    def unregister(self, holder):
        if holder is None:
            return

        affecteeMaps, affectorMaps = self.__getMaps(holder)

        for key, map in affecteeMaps:
            map[key].remove(holder)

        for info in holder.type.getInfos():
            value = (holder, info)
            for key, map in affectorMaps:
                map[key].remove(value)

    def getAffectors(self, holder):
        """
        Get a set of (sourceHolder, info) tuples affecting the passed holder
        """
        location = holder.location

        s = set()
        if holder.specific:
            specific = self.__affectorSpecificLocation.get(location)
            if specific is not None:
                s.update(specific)
        else:
            affectorMaps = [(location, self.__affectorSpecificLocation), # Specific location register
                            ((location, holder.type.groupId), self.__affectorGroupLocation)] #group location register

            affectorSkillLocation = self.__affectorSkillLocation

            # Add the skills to the affectee/affector fillup maps
            for skillId in holder.type.requiredSkills():
                key = (location, skillId)
                affectorMaps.append((key, affectorSkillLocation))

            for key, map in affectorMaps:
                affectors = map.get(key)
                if affectors is not None:
                    s.update(affectors)

        return s;

    def getAffectees(self, registrationInfo):
        """
        Get the holders that the passed (sourceHolder, info) tuple affects
        """
        _, info = registrationInfo
        location = info.location

        s = set()

        # No filterType ==> The location is specificly targetted
        if info.filterType == None:
            if location == const.locShip:
                s.add(self.__fit.ship)
            elif location == const.locChar:
                s.add(self.__fit.character)
            elif location == const.locSpace:
                raise NotImplementedError("Not implemented until we keep track of drones & missiles")

        elif info.filterType == const.filterAll:
            s.update(self.__affecteeLocation.get((location, info.filterValue)) or ())

        elif info.filterType == const.filterSkill:
            s.update(self.__affecteeSkillLocation.get((location, info.filterValue)) or ())

        elif info.filterType == const.filterGroup:
            s.update(self.__affecteeGroupLocation.get((location, info.filterValue)) or ())

        return s;