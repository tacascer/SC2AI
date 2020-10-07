import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.ids.unit_typeid import UnitTypeId
from sc2.constants import *
from sc2.data import race_townhalls

import random


class MacroBot(sc2.BotAI):
    async def on_step(self, iteration):
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.expand()
        await self.build_assimilator()
        await self.offensive_force_buildings()
        await self.build_offensive_force()
        await self.attack()

    async def build_workers(self):
        for nexus in self.townhalls.ready.idle:
            if self.can_afford(UnitTypeId.PROBE):
                await self.do(nexus.train(UnitTypeId.PROBE))

    async def build_pylons(self):
        if self.supply_left < 5 and not self.already_pending(UnitTypeId.PYLON):
            nexi = self.units(UnitTypeId.NEXUS).ready
            if nexi.exists:
                if self.can_afford(UnitTypeId.PYLON):
                    await self.build(UnitTypeId.PYLON, near=nexi.first)

    async def expand(self):
        if self.units(UnitTypeId.NEXUS).amount < 3 and self.can_afford(UnitTypeId.NEXUS):
            await self.expand_now()

    async def build_assimilator(self):
        for nexus in self.units(UnitTypeId.NEXUS).ready:
            vespenes = self.state.vespene_geyser.closer_than(15.0, nexus)
            for vespene in vespenes:
                if not self.can_afford(UnitTypeId.ASSIMILATOR):
                    break
                worker = self.select_build_worker(vespene.position)
                if worker is None:
                    break
                if not self.units(UnitTypeId.ASSIMILATOR).closer_than(1.0, vespene).exists:
                    await self.do(worker.build(UnitTypeId.ASSIMILATOR, vespene))

    async def offensive_force_buildings(self):
        if self.units(UnitTypeId.PYLON).ready.exists:
            pylon = self.units(UnitTypeId.PYLON).ready.random

            if self.units(UnitTypeId.GATEWAY).ready.exists and not self.units(UnitTypeId.CYBERNETICSCORE):
                if self.can_afford(UnitTypeId.CYBERNETICSCORE) and not self.already_pending(UnitTypeId.CYBERNETICSCORE):
                    await self.build(UnitTypeId.CYBERNETICSCORE, near=pylon)

            elif len(self.units(UnitTypeId.GATEWAY)) < 3:
                if self.can_afford(UnitTypeId.GATEWAY) and not self.already_pending(UnitTypeId.GATEWAY):
                    await self.build(UnitTypeId.GATEWAY, near=pylon)

    async def build_offensive_force(self):
        for gw in self.units(UnitTypeId.GATEWAY).ready.idle:
            if self.can_afford(UnitTypeId.STALKER) and self.supply_left > 0:
                await self.do(gw.train(UnitTypeId.STALKER))

    def find_target(self, state):
        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]

    async def attack(self):
        if self.units(UnitTypeId.STALKER).amount > 15:
            for s in (self.units(UnitTypeId.STALKER)).idle:
                await self.do(s.attack(self.find_target(self.state)))

        if self.units(UnitTypeId.STALKER).amount > 3:
            if len(self.known_enemy_units) > 0:
                for s in (self.units(UnitTypeId.STALKER)).idle:
                    await self.do(s.attack(random.choice(self.known_enemy_units)))


run_game(maps.get("TritonLE"), [
    Bot(Race.Protoss, MacroBot()),
    Computer(Race.Terran, Difficulty.Easy)
], realtime=False)
