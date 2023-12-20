from simulation_classes import Role, Recipe

# Recipes
farm_strong =\
    Recipe("Strong Farm",
           {"tools": .1, },
           {"food": 4, })
farm_medium =\
    Recipe("Medium Farm",
           {"wood": 1},
           {"food": 2})
farm_weak =\
    Recipe("Weak Farm",
           {"wood": 0.5},
           {"food": 1})
chop_wood_strong =\
    Recipe("Strong Chop Wood",
           {"tools": .1},
           {"wood": 3, })
chop_wood_weak =\
    Recipe("Weak Chop Wood",
           {},
           {"wood": 1})
craft_tools_strong =\
    Recipe("Strong Craft Tools",
           {"iron": 2},
           {"tools": 4})
craft_tools_weak =\
    Recipe("Weak Craft Tools",
           {"wood": 1},
           {"tools": 1})
mine_ore_strong =\
    Recipe("Strong Mine Ore",
           {"tools": .1},
           {"iron": 3, })
mine_ore_weak =\
    Recipe("Weak Mine Ore",
           {},
           {"iron": 1})
# smelt_ore_strong =\
#     Recipe("Strong Smelt Ore",
#            {"ore": 3, "tools": .1},
#            {"iron": 3, })
# smelt_ore_weak =\
#     Recipe("Weak Smelt Ore",
#            {"ore": 2},
#            {"iron": 2})


# Roles
farmer =\
    Role("Farmer",
         [farm_strong, farm_medium],
         {"food": 3, "tools": 2, "wood": 3})
lumberjack =\
    Role("Lumberjack",
         [chop_wood_strong, chop_wood_weak],
         {"tools": 2})
smith =\
    Role("Smith",
         [craft_tools_strong, craft_tools_weak],
         {"iron": 5})
miner =\
    Role("Miner",
         [mine_ore_strong, mine_ore_weak],
         {"tools": 2})
# smelter =\
#     Role("Smelter",
#          [smelt_ore_strong, smelt_ore_weak],
#          {"ore": 5, "tools": 2})


roles = [farmer,
         lumberjack,
         smith,
         miner,
         #  smelter
         ]

# quickly makes all recpeies require food to operate, with the exception of food recipes
for role in roles:
    for recipe in role.recipes:
        if 'food' not in recipe.produces:
            recipe.requires['food'] = 1


def resource_finder():
    potential_resources = set()
    for role in roles:
        creates = role.get_created_resources()
        potential_resources.update(creates.keys())
    return potential_resources
