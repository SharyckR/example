# Imports, sorted alphabetically.

# Python packages
from time import time

# Third-party packages
# Nothing for now...

# Modules from this project
import globals as G
from nature import *
from world import *


class Model(World):
    def __init__(self, initialize=True):
        super(Model, self).__init__()
        if initialize:
            print('Building terrain...')
            print('using Perlin...')
            return

            #skip all of this, using perlin now.
            start = time()
            self.initialize()
            print('Terrain successfully built in %f seconds.' % (time() - start))

            print('Preparing game...')
            self.post_initialize()

    def initialize(self):
        world_size = G.config.getint('World', 'size')
        world_type = G.TERRAIN_CHOICE  # FIXME: Unify names!
        hill_height = G.TERRAIN['hill_height']
        self.max_trees = G.TERRAIN['max_trees']
        tree_chance = self.max_trees / float(world_size *
                                             (G.SECTOR_SIZE ** 3))
        n = world_size / 2  # 80
        s = 1
        y = 0

        worldtypes_grounds = {
            'plains': dirt_block,
            'desert': (sand_block,) * 15 + (sandstone_block,) * 4,
            'island': (water_block,) * 30 + (clay_block,) * 4,
            'mountains': (dirt_block,) * 15 + (dirt_block,) * 3 + (stone_block,),
            'snow': (snowgrass_block,) * 10 + (snow_block,) * 4 + (ice_block,) * 8,
        }

        world_type_trees = {
            'plains': (OakTree, BirchTree, WaterMelon, Pumpkin, YFlowers, Potato, Carrot, Rose),
            'desert': (Cactus, TallCactus, Rose),
            'island': (OakTree, JungleTree, BirchTree, Cactus, TallCactus, WaterMelon, YFlowers, Reed, Rose),
            'mountains': (OakTree, BirchTree, Pumpkin, YFlowers, Potato, Carrot),
            'snow': (OakTree, BirchTree, WaterMelon, YFlowers, Potato, Rose),
        }

        # ores avaliable on the lowest level, closet to bedrock
        lowlevel_ores = ((stone_block,) * 75 + (diamondore_block,) * 2 + (sapphireore_block,) * 2)
        #  ores in the 'mid-level' .. also, the common ore blockes
        midlevel_ores = ((stone_block,) * 80 + (rubyore_block,) * 2 +
                         (coalore_block,) * 4 + (gravel_block,) * 5 +
                         (ironore_block,) * 5 + (lapisore_block,) * 2)
        # ores closest to the top level dirt and ground
        highlevel_ores = ((stone_block,) * 85 + (gravel_block,) * 5 + (coalore_block,) * 3 + (quartz_block,) * 5)

        for x in xrange(-n, n + 1, s):
            for z in xrange(-n, n + 1, s):

                # Generation of the outside wall
                if x in (-n, n) or z in (-n, n):
                    for dy in xrange(-16, 10):  # was -2 ,6
                        self.init_block((x, y + dy, z), stone_block)
                    continue

                # Generation of the ground

                block = worldtypes_grounds[world_type]
                levelcount=0


                if isinstance(block, (tuple, list)):
                    block = random.choice(block)
                self.init_block((x, y - 2, z), block)
                for yy in xrange(-16, -2):
                    # ores and filler...
                    #oblock = random.choice(ore_type_blocks)
                    levelcount = levelcount +1
                    if levelcount < 4:
                        blockset = lowlevel_ores
                    if levelcount >= 5 and levelcount <= 13:
                        blockset = midlevel_ores
                    if levelcount >= 14:
                        blockset = highlevel_ores
                    oblock = random.choice(blockset)
                    self.init_block((x, yy, z), oblock)

                for yy in xrange(-18, -16):
                    self.init_block((x, yy , z), bed_block)

                # Perhaps a tree
                if self.max_trees > 0:
                    showtree = random.random()
                    if showtree <= tree_chance:
                        tree_class = world_type_trees[world_type]
                        if isinstance(tree_class, (tuple, list)):
                            tree_class = random.choice(tree_class)
                        self.generate_vegetation((x, y - 2, z), tree_class)

        if G.FLAT_MODE:
            return

        o = n - 10 + hill_height - 6

        world_type_blocks = {
            'plains': dirt_block,
            'desert': sand_block,
            'island': (dirt_block, sand_block),
            'mountains': stone_block,
            'snow': snowgrass_block,
        }

        # Hills generation
        # FIXME: This generation in two phases (ground then hills), leads to
        # hills overlaying trees.
        for _ in xrange(world_size / 2 + 40):  # (120):
            a = random.randint(-o, o)
            b = random.randint(-o, o)
            c = -1
            h = random.randint(1, hill_height)
            s = random.randint(4, hill_height + 2)
            d = 1
            block = world_type_blocks[world_type]
            if isinstance(block, (tuple, list)):
                block = random.choice(block)
            for y in xrange(c, c + h):
                for x in xrange(a - s, a + s + 1):
                    for z in xrange(b - s, b + s + 1):
                        if (x - a) ** 2 + (z - b) ** 2 > (s + 1) ** 2:
                            continue
                        if (x - 0) ** 2 + (z - 0) ** 2 < 5 ** 2:
                            continue
                        if (x, y, z) in self:
                            continue
                        self.init_block((x, y, z), block)

                        # Perhaps a tree
                        if self.max_trees > 0:
                            showtree = random.random()
                            if showtree <= tree_chance:
                                tree_class = world_type_trees[world_type]
                                if isinstance(tree_class, (tuple, list)):
                                    tree_class = random.choice(tree_class)
                                self.generate_vegetation((x, y, z), tree_class)

                s -= d

    def generate_vegetation(self, position, vegetation_class):
        if position in self:
            return

        # Avoids a tree from touching another.
        if vegetation_class in TREES \
            and self.has_neighbors(position, is_in=TREE_BLOCKS,
                                   diagonals=True):
            return

        x, y, z = position

        # Vegetation can't grow on anything.
        if self[(x, y - 1, z)] not in vegetation_class.grows_on:
            return

        vegetation_class.add_to_world(self, position)

    def init_block(self, position, block):
        self.add_block(position, block, sync=False, force=False)

    def post_initialize(self):
        # Convert dirt to grass if no block or a transparent one is above.
        for position, block in ((p, b) for p, b in self.items()
                                if b is dirt_block):
            x, y, z = position
            above_position = x, y + 1, z
            if above_position not in self or self[above_position].transparent:
                self[position] = grass_block
