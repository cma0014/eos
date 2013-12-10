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


from collections import namedtuple
from itertools import chain

from eos.const.eve import Group
from eos.fit.holder.mixin.damage_dealer import DamageDealerMixin
from eos.fit.tuples import DamageTypesTotal
from .abc import StatRegister


DmgCats = namedtuple('DmgCats', ('turret', 'missile', 'drone', 'smartbomb',
                                 'bomb', 'doomsday', 'misc', 'all'))
DroneDmgCats = namedtuple('DroneDmgCats', ('mobile', 'sentry', 'all'))
InternalCats = namedtuple('InternalCats', ('turret', 'missile', 'drone_mobile',
                                           'drone_sentry', 'smartbomb', 'bomb',
                                           'doomsday', 'misc'))


class DamageDealerRegister(StatRegister):
    """
    Class which tracks all holders which can potentially
    deal damage, and provides functionality to fetch some
    useful data.
    """

    def __init__(self):
        self.__dealers = set()

    def register_holder(self, holder):
        if isinstance(holder, DamageDealerMixin):
            self.__dealers.add(holder)

    def unregister_holder(self, holder):
        self.__dealers.discard(holder)

    def get_nominal_volley(self, target_resistances):
        containers = InternalCats(turret={}, missile={}, drone_mobile={}, drone_sentry={},
                                  smartbomb={}, bomb={}, doomsday={}, misc={})
        drone_totals = {}
        totals = {}
        container_finder = {
            Group.projectile_weapon: lambda h: containers.turret,
            Group.energy_weapon: lambda h: containers.turret,
            Group.hydrid_weapon: lambda h: containers.turret
        }
        for holder in self.__dealers:
            volley = holder.get_nominal_volley(target_resistances=target_resistances)
            if volley is None:
                continue
            try:
                group = holder.item.group_id
            except AttributeError:
                group = None
            try:
                finder = container_finder[group]
            except KeyError:
                container = containers.misc
            else:
                container = finder(holder)
            for i in range(4):
                damage = volley[i]
                try:
                    container[i] += damage
                except KeyError:
                    container[i] = damage
        for container in (containers.drone_mobile, containers.drone_sentry):
            for k, v in container:
                try:
                    drone_totals[k] += v
                except KeyError:
                    drone_totals[k] = v
        for container in containers:
            for k, v in container.items():
                try:
                    totals[k] += v
                except KeyError:
                    totals[k] = v
        drone_dmg = DroneDmgCats(
            mobile=self.__dmg_container_to_ntuple(containers.drone_mobile),
            sentry=self.__dmg_container_to_ntuple(containers.drone_sentry),
            all=self.__dmg_container_to_ntuple(drone_totals)
        )
        dmg = DmgCats(
            turret=self.__dmg_container_to_ntuple(containers.turret),
            missile=self.__dmg_container_to_ntuple(containers.missile),
            drone=drone_dmg,
            smartbomb=self.__dmg_container_to_ntuple(containers.smartbomb),
            bomb=self.__dmg_container_to_ntuple(containers.bomb),
            doomsday=self.__dmg_container_to_ntuple(containers.doomsday),
            misc=self.__dmg_container_to_ntuple(containers.misc),
            all=totals
        )
        return dmg

    def __dmg_container_to_ntuple(self, container):
        total = sum(container.values())
        ntuple = DamageTypesTotal(*chain((container.get(k, 0) for k in range(4)), (total,)))
        return ntuple

    def get_nominal_dps(self, target_resistances, reload):
        em = 0
        therm = 0
        kin = 0
        expl = 0
        for holder in self.__dealers:
            dps = holder.get_nominal_dps(target_resistances=target_resistances, reload=reload)
            if dps is None:
                continue
            em += dps.em
            therm += dps.thermal
            kin += dps.kinetic
            expl += dps.explosive
        total = em + therm + kin + expl
        return DamageTypesTotal(em=em, thermal=therm, kinetic=kin, explosive=expl, total=total)