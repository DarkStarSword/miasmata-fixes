#!/usr/bin/env python2.7

from __future__ import print_function

from StringIO import StringIO
import collections
import random
import os

import rs5archive
import rs5file
import rs5mod
import environment
import inst_header
import inst_node
import cterr_hmap

# 1: Dumb random mode, all plants just selected at random. Way to easy to find goal items, while also not guaranteed that goal items will exist.
# 2: Shuffle kinds of plants (all instances of x will now be instances of y)
# 3: Unimplemented, planning to randomize groups of nearby plants together
SHUFFLE_MODE_NOTES  = 1 # FIXME: Guarantee all notes spawn at least one instance
SHUFFLE_MODE_PLANTS = 2

# "randomizer.rs5mod" is causing the game to crash on launch if the rs5mod
# is in the game directory, maybe that same issue with naming anything
# after "e"? I thought I tested the rs5mod extension avoiding that? Dangit
randomizer_filename = 'randomizer.dss5mod'

# Order used to make sure important plants on the spoiler map are drawn over
# less important ones
spoiler_plant_colours = collections.OrderedDict((
    # Useless Prickly Pear
    ('plant0', '001000'),
    # MEDS_5_AntiPhychosisTonic
    # Not in game, but the orange plants are. Fun fact, the non-toxic versions
    # of the Clarity + Herculean tonics can still by synthesized with these
    ('plant13', '301000'),
    ('plant15', '301000'),
    ('plant17', '301000'),
    # MEDS_1_BasicMedicine
    ('plant1',  '303030'),
    ('plant2',  '303030'),
    ('plant7',  '303030'),
    ('plant9',  '303030'),
    ('plant11', '303030'),
    ('plant14', '303030'),
    ('plant18', '303030'),
    ('plant22', '303030'),
    # MEDS_2_ExtraStrengthMedicine
    ('plant00', '180030'),
    ('plant12', '180030'),
    ('plant16', '180030'),
    ('plant33', '180030'),
    # MEDS_3_MentalStimulant
    ('plant4', '002030'),
    ('plant6', '002030'),
    # MEDS_4_AdrenalineStimulant
    ('plant20', '203000'),
    ('plant21', '203000'),
    ('plant28', '203000'),

    # MEDS_6_clarityTonic
    ('plant3',  '400000'), # Red Toadstool
    ('plant29', '600000'), # Fabacae
    # MEDS_7_herculeanTonic
    ('plant5',  '808000'), # Yellow Mushrooms

    # MEDS_8_EnduranceEmphasisDrug
    ('plant25', '8000b0'), # Giant Bloom
    ('plant19', '000080'), # Blue-Capped Toadstool
    # MEDS_9_MuscleEmphasisDrug
    ('plant32', '800080'), # Large Jungle Flower
    ('plant34', '400080'), # Fleshy Purple Fruit
    # MEDS_10_BrainEmphasisDrug
    ('plant8',  'c6b384'), # Sponge-Like Fungus
    ('plant10', '875400'), # Trumpet Mushroom

    # MEDS_14_AgentX
    ('plant26', 'ff8000'), # Bulbous, Fruit Plant
    ('plant31', '0000ff'), # Blue Scaly Tree Fungus
    # MEDS_15_AgentY
    ('plant23', 'bd69ad'), # Rainbow Orchard
    ('plant30', '00ff00'), # Bio-Luminescent Algae
    # MEDS_16_AgentZ
    ('plant24', 'ffff00'), # Titan Plant
    ('plant27', '8000ff'), # Carnivorous Pitcher Plant
))
# Convert hex strings to RGB tuples:
for k,v in spoiler_plant_colours.items():
    spoiler_plant_colours[k] = (int(v[:2],16), int(v[2:4],16), int(v[4:],16))

cure_plants = (
    'plant26', 'plant31', # Agent X
    'plant23', 'plant30', # Agent Y
    'plant24', 'plant27', # Agent Z
)
important_plants = cure_plants + (
    'plant25', 'plant19', # Endurance Emphasis
    'plant32', 'plant34', # Muscle Emphasis
    'plant8', 'plant10', # Brain Emphasis
    'plant3', 'plant29', # Clarity Tonic (Red)
    'plant5', # Herculean Tonic (Yellow)
)

# Blacklist corrupt / inaccessible instance nodes:
min_z_blacklist_whole_node = -1.0 # Detects orbital launch platform, now just explicitly blacklisting that
blacklist_inods = (
        64784, 64783, 16195, # Corrupt orbital launch site East of Rigel
        36614, 36616, # Developer area in river West of spawn with hidden(?) notes, coords 2720x3456 - 2752x3520. Unclear why these notes don't show in game, but we don't want to include them in the randomizer.
        19911) # Milo Island easter egg East of Desert. Coords 4852x6452 - 4940x6539
# TODO: Use cterr_hmap to verify nothing else underground / in air

# TODO: Eggplant model is in multiple parts - three takable fruit models +
# leaves that remain. Will need special handling to randomize this later:
ADDITIONAL_MODELS = {
    #'Eggplant_Leaves1': 'plant34'
}

# TODO: Blue scaly fungus appears to be attached to a tree? Might limit what
# we can safely swap it to. Needs testing.

def find_install_path():
    # FIXME: Query registry / prompt user / GUI like miaspatch
    if os.path.isfile('miasmata.exe'):
        return os.curdir

def load_main_rs5(install_path):
    print('Loading main.rs5...')
    path = os.path.join(install_path, 'main.rs5')
    return rs5archive.Rs5ArchiveDecoder(open(path, 'rb+'))

def load_environment_rs5(install_path):
    print('Loading environment.rs5...')
    path = os.path.join(install_path, 'environment.rs5')
    return environment.parse_from_archive(path)

def get_plants_notes_list(env_rs5, skip_non_removable=True):
    ret = ADDITIONAL_MODELS.copy()
    for modelset,game_object in env_rs5['player']['pick_objects'].iteritems():
        if not modelset.startswith('modelsets\\'):
            continue
        if not game_object.startswith('plant') and not game_object.startswith('note'):
            continue
        model_name = modelset.split('\\')[1]
        #print(game_object, model_name)

        # Filter out objects that don't get removed when picked up:
        game_objects_case_sensitive = { x.lower(): x for x in env_rs5['game_objects'] }
        game_object_cs = game_objects_case_sensitive[game_object.lower()]
        removal_mode = env_rs5['game_objects'][game_object_cs]['removal_mode']
        assert(removal_mode in (0,1,2))
        if skip_non_removable and removal_mode == 0:
            print('Skipping %s %s because removal mode is 0' % (game_object, model_name))
            continue

        ret[model_name] = game_object
    return ret

bad_nodes = []
def dump_bad_nodes():
    try:
        import miasmap
    except Exception as e:
        print('Error importing miasmap, no spoiler maps for you', str(e))
        return
    tmp = miasmap.image
    miasmap.image = tmp.copy()
    miasmap.pix = miasmap.image.load()
    plotted_instance_nodes = set()
    for node, altitude, inst_node_bounds in bad_nodes:
        node_name, node_name_idx, u1, x, y, z, u2, u3, u4, u5, u6 = node
        (node_idx, (x1, y1, z1, x2, y2, z2)) = inst_node_bounds
        if z < min_z_blacklist_whole_node: # Way too far below water, unreachable
            colour = (255,0,0)
        elif z <= 0: # Some legitimately below water level, but need to check
            colour = (0,255,0)
        elif altitude < -1:
            colour = (64 + int(-altitude), 0, 0)
        elif altitude < 0:
            #colour = (128,0,0)
            colour = (0, 1 + int(-altitude), 0)
        else:
            #colour = (0,0,128) #+int(z))
            colour = (0,0,32 + int(altitude))
        if True: # Items shown as big fat easy to see square
            miasmap.plot_square(int(x), int(y), 20, colour)
        else: # Items as tiny points
            miasmap.plot_point(int(x), int(y), (255,255,255), colour)
        if node_idx not in plotted_instance_nodes: # Also show the XY boundaries of the corresponding instance nodes
            plotted_instance_nodes.add(node_idx)
            miasmap.plot_rect(int(x1), int(y1), colour, int(x2), int(y2), colour)
    #miasmap.save_image('bad_nodes.png') # Slow, but helps when drawing the instance node bounds
    miasmap.save_image('bad_nodes.jpg')

class ShuffleBucket():
    def __init__(self, shuffle_mode, bucket):
        self.shuffle_mode = shuffle_mode
        self.bucket = bucket
        if shuffle_mode == 1:
            # Counter to ensure all items are given out at least once
            self.rr_counter = 0

def spoil(plants):
    import miasmap
    tmp = miasmap.image
    miasmap.image = tmp.copy()
    miasmap.pix = miasmap.image.load()

    install_path = find_install_path()

    env_rs5 = load_environment_rs5(install_path)
    models = get_plants_notes_list(env_rs5, skip_non_removable=False)

    if plants is None:
        plants = [ x for x in models.values() if x.startswith('plant') ]
    elif not isinstance(plants, (list, tuple)):
        plants = (plants,)

    m = { k:v for (k,v) in models.items() if v in plants }
    print('Searching for', ', '.join(m))

    main_rs5 = load_main_rs5(install_path)
    inst_header_fp = inst_header.open_inst_header_from_rs5(main_rs5)
    inst_node_names = inst_header.get_name_list(inst_header_fp)
    #search_inst_ids = { inst_node_names.index(k): spoiler_plant_colours[v] for k,v in m.iteritems() }
    search_inst_ids = { inst_node_names.index(k): v for k,v in m.iteritems() }

    points = {}

    for inod_fname,compressed_file in main_rs5.iteritems():
        if compressed_file.type != 'INOD':
            continue
        inod_index = int(inod_fname[9:]) # strip "inst_node" from filename
        assert(inod_fname == 'inst_node%i' % inod_index)
        #if inod_index in blacklist_inods:
        #    print('Skipping blacklisted %s' % inod_fname)
        #    continue
        decompressed = compressed_file.decompress()
        nodes = inst_node.parse_inod(StringIO(decompressed), inst_node_names)
        for node in nodes:
            node_name, node_name_idx, u1, x, y, z, u2, u3, u4, u5, u6 = node
            try:
                #colour = search_inst_ids[node_name_idx]
                plant = search_inst_ids[node_name_idx]
                #miasmap.plot_square(int(x), int(y), 20, colour, additive=False)
                points.setdefault(plant, []).append((int(x), int(y)))
            except KeyError:
                pass
    for plant, colour in spoiler_plant_colours.iteritems():
        for x,y in points.get(plant, []):
            miasmap.plot_square(int(x), int(y), 20, colour, additive=False)
    miasmap.save_image('spoiler.jpg')

def generate_and_install_randomizer():
    randomizer_mod_name = os.path.splitext(randomizer_filename)[0]
    print('Removing previous %s from main.rs5...' % randomizer_mod_name) # FIXME: may add seed numbers to fname?
    rs5mod.rm_mod('main.rs5', [randomizer_mod_name])
    if os.path.exists(randomizer_filename):
        print('Deleting old %s' % randomizer_filename)
        os.remove(randomizer_filename)

    install_path = find_install_path()
    env_rs5 = load_environment_rs5(install_path)
    models = get_plants_notes_list(env_rs5)
    #print(models)

    main_rs5 = load_main_rs5(install_path)
    inst_header_fp = inst_header.open_inst_header_from_rs5(main_rs5)
    inst_node_names = inst_header.get_name_list(inst_header_fp)
    #print(inst_node_names)

    # Reading the height map to find any potentially underground/floating
    # items. TODO: This height map is only approximate. Might want to read the
    # actual terrain vertex data for more accurate tests.
    height_map = cterr_hmap.open_cterr_hmap_from_rs5(main_rs5)

    search_inst_ids = {}
    notes_bucket = {}
    plants_bucket = {} # TODO: Smaller buckets that make sense to shuffle together, e.g. fungi separate from flowers
    shuffle_buckets = [
            ShuffleBucket(SHUFFLE_MODE_NOTES, notes_bucket),
            ShuffleBucket(SHUFFLE_MODE_PLANTS, plants_bucket)
    ]
    for model,game_object in models.iteritems():
        if model not in inst_node_names:
            print('NOTE: %s referenced in environment.rs5 not found in inst_header (no instances of this game_object in the map)' % model)
            continue
        inst_name_idx = inst_node_names.index(model)
        #print(inst_name_idx, game_object, model)
        #search_inst_ids.append(inst_name_idx)
        search_inst_ids[inst_name_idx] = game_object
        if game_object.lower().startswith('note'):
            shuffle_mode, bucket = SHUFFLE_MODE_NOTES, notes_bucket
        else:
            shuffle_mode, bucket = SHUFFLE_MODE_PLANTS, plants_bucket
        if shuffle_mode == 1:
            bucket[inst_name_idx] = 0
        elif shuffle_mode == 2:
            bucket.setdefault(game_object, []).append(inst_name_idx)

    #print('DEBUG: Original buckets:', shuffle_buckets)
    for bucket in shuffle_buckets:
        if bucket.shuffle_mode == 2:
            keys,vals = map(list, zip(*bucket.bucket.items()))
            random.shuffle(keys)
            bucket.bucket.update(dict(zip(keys,vals)))
            print('DEBUG / SPOILER: Shuffled bucket:', bucket.bucket)

    # Currently only using the bounds for debugging/insights. With
    # SHUFFLE_MODE_PLANTS=1 observed some plants in Draco changing types as
    # they are approached (FIXME), which I initially assumed was instance
    # nodes of different sizes being used as a type of LOD mechanism (and I
    # still think this is the case to some extent), but the bounds we are
    # outputting doesn't look right for that theory - rather, it looks like
    # these can be different sizes, and can overlap, and perhaps plants in two
    # overlapping instance nodes are the problem? In thoery other shuffle
    # modes should avoid this issue since nearby plants will be changed
    # together, including overlaps, but needs further thought & testing.
    inst_header_fp.seek(0)
    inst_node_bounds = list(inst_header.get_points(inst_header_fp))
    print('Total instance nodes in inst_header: %i' % len(inst_node_bounds))

    relevant_inodes = []
    for inod_fname,compressed_file in main_rs5.iteritems():
        if compressed_file.type != 'INOD':
            continue
        inod_index = int(inod_fname[9:]) # strip "inst_node" from filename
        assert(inod_fname == 'inst_node%i' % inod_index)
        if inod_index in blacklist_inods:
            print('Skipping blacklisted %s' % inod_fname)
            continue
        decompressed = compressed_file.decompress()
        nodes = inst_node.parse_inod(StringIO(decompressed), inst_node_names)
        relevant = False
        blacklist = False
        for node in nodes:
            node_name, node_name_idx, u1, x, y, z, u2, u3, u4, u5, u6 = node
            # u1 appears to be a unique object ID
            if node_name_idx not in search_inst_ids:
                continue
            relevant = True
            if z < 0:
                print('WARNING: %s located %f below Ocean level' % (node_name, z), search_inst_ids[node_name_idx], inod_fname, node)
                if z < min_z_blacklist_whole_node:
                    print('WARNING: Bad nodes detected in %s, blacklisting' % inod_fname)
                    blacklist = True
                    break
            #(n, (x1, y1, z1, x2, y2, z2)) = inst_node_bounds[inod_index]
            #print(x, y, z, inod_index, node_name, u1, x1, y1, z1, x2, y2, z2)
            altitude = z - height_map[int(x/2.0), int(y/2.0)]
            if altitude < 0 or altitude > 5:
                bad_nodes.append((node, altitude, inst_node_bounds[inod_index])) # TODO: Only add if actually bad, for now adding all for testing
        if relevant and not blacklist:
            #print('Relevant inst node %s' % inod_fname)
            relevant_inodes.append(inod_fname)

    dump_bad_nodes()

    # TODO: Seed from time or user input
    # TODO: Group nearby plants of same type
    # TODO: Shuffle groups with similar attachments (on ground / fungus on side of tree / algae)

    randomizer_rs5 = rs5archive.Rs5ArchiveEncoder(randomizer_filename)
    for inod_fname in relevant_inodes:
        decompressed = main_rs5[inod_fname].decompress()
        nodes = list(inst_node.parse_inod(StringIO(decompressed), inst_node_names))
        new_nodes = []
        for node in nodes:
            node_name, node_name_idx, u1, x, y, z, u2, u3, u4, u5, u6 = node
            if node_name_idx in search_inst_ids:
                for bucket in shuffle_buckets:
                    if bucket.shuffle_mode == 1:
                        if node_name_idx in bucket.bucket:
                            #node_name_idx = random.choice(bucket.keys())
                            rr_items = {}
                            while not rr_items:
                                rr_items = [ k for k,v in bucket.bucket.items() if v == bucket.rr_counter ]
                                if not rr_items:
                                    print('All items in bucket given out for round %i, moving to next round' % bucket.rr_counter)
                                    bucket.rr_counter += 1
                            #print('RR items round %i' % bucket.rr_counter, rr_items)
                            node_name_idx = random.choice(rr_items)
                            bucket.bucket[node_name_idx] += 1
                            print('SPOILER: Replaced %s with %s, round %i' % (node_name, inst_node_names[node_name_idx], bucket.rr_counter))
                            node_name = '_replaced' # Not used, just setting to avoid confusion
                            break
                    elif bucket.shuffle_mode == 2:
                        game_object = models[node_name]
                        if game_object in bucket.bucket:
                            node_name_idx = random.choice(bucket.bucket[game_object])
                            #print('SPOILER: Replaced %s with %s' % (node_name, inst_node_names[node_name_idx]))
                            #print('DEBUG: Replaced %s with %i' % (node_name, node_name_idx)) # Not printing replaced name to avoid spoilers. Even printing ID might be too much...
                            node_name = '_replaced' # Not used, just setting to avoid confusion
                            break
                    elif bucket.shuffle_mode == 3:
                        # TODO: Advanced randomizer that will shuffle groups of nearby
                        # plants. Should be the most challenging
                        pass
            new_nodes.append((node_name, node_name_idx, u1, x, y, z, u2, u3, u4, u5, u6))
        new_buf = inst_node.encode_inod(inod_fname, new_nodes)
        randomizer_rs5.add_from_buf(new_buf)
        #randomizer_rs5.add_from_buf(decompressed) # Test everything works without modifying the buffer
    randomizer_rs5.save()
    del randomizer_rs5 # Ensures file is closed

    print('Saved %s' % randomizer_filename)
    print('FIXME!!! miasmod has ascii error installing this!!!!')
    #print('rs5-extractor.py -f main.rs5 --add-mod %s' % randomizer_filename)
    print('Installing new randomizer to main.rs5...')
    rs5mod.add_mod('main.rs5', [randomizer_filename])

    #print('FIXME!!! miasmata is crashing if randomizer.rs5mod is in the game directory!!!!')
    #os.remove(randomizer_filename)

if __name__ == '__main__':
    generate_and_install_randomizer()
    # spoil('plant31')
    #spoil(cure_plants)
    #spoil(important_plants)
    spoil(None)
