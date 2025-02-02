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

# 1: Dumb round robin random mode, all items just selected at random.
#    Way to easy to find goal items, so not recommended for plants.
# 2: Shuffle kinds of plants (all instances of x will now be instances of y)
#    If you got the achievement for finding all the plants, this should be easy
# 3: Shuffles clusters of plants around for a real challenge! In this mode the
#    cure could be virtually anywhere, and you may have to thoroughly explore
#    the island to find it! Areas that were previously insignificant that you
#    have never bothered exploring or always just walked past may now hold the
#    key - do you know where all the random fields of wild flowers or rare
#    yellow mushrooms are?
SHUFFLE_MODE_NOTES  = 1
SHUFFLE_MODE_PLANTS = 3
CLUSTER_DISTANCE = 100 # TODO: Experiment with this number

# Keep these plants in a separate shuffle bucket to the others. This avoids the
# Blue fungus being placed where the Rainbow Orchard was, which would otherwise
# have ended up with it being just below the ground (TODO: Look for other cases
# like this, we may need additional safeguards against it). It also hopefully
# keeps fungi that grow out of trees separate from plants that grow out of the
# ground
FUNGI_BUCKET = (
    # Grows out of upright trees:
    'plant31', # Blue Scaly Tree Fungus
    'plant10', # Trumpet Mushroom
    'plant5',  # Yellow Mushrooms
    'plant6',  # Grey Shelf Fungus
    'plant9',  # Wood Gill Fungus
    'plant20',  # Red-Green Tree Fungus
    # Found on fallen logs, test if these need a separate bucket:
    'plant4',  # Pearl-Blue Shelf Fungus
    'plant7',  # Brown Shelf Fungus
)

# "randomizer.rs5mod" is causing the game to crash on launch if the rs5mod
# is in the game directory, maybe that same issue with naming anything
# after "e"? I thought I tested the rs5mod extension avoiding that? Dangit
randomizer_filename = 'randomizer.dss5mod'

# Order used to make sure important plants on the spoiler map are drawn over
# less important ones
spoiler_plant_colours = collections.OrderedDict((
    ('plant0',  '001000'), # Prickly Pear
    # MEDS_5_AntiPhychosisTonic
    # Not in game, but the orange plants are. Fun fact, the non-toxic versions
    # of the Clarity + Herculean tonics can still by synthesized with these
    ('plant13', '301000'), # Orange Prairie Flower
    ('plant15', '301000'), # Sunflower
    ('plant17', '301000'), # Red and Yellow Hibiscus
    # MEDS_1_BasicMedicine
    ('plant1',  '303030'), # Common White Mushroom
    ('plant2',  '303030'), # Pawn Shaped Mushroom
    ('plant7',  '303030'), # Brown Shelf Fungus
    ('plant9',  '303030'), # Wood Gill Fungus
    ('plant11', '303030'), # White Spiked Prairie Flower
    ('plant14', '303030'), # White Bundle Prairie Flower
    ('plant18', '303030'), # White/Pink Viola
    ('plant22', '303030'), # Pink Spotted Lilly
    # MEDS_2_ExtraStrengthMedicine
    ('plant00', '180030'), # Violet Cactus
    ('plant12', '180030'), # Pink-White Prairie Flower
    ('plant16', '180030'), # Indigo Asteraceae
    ('plant33', '180030'), # Tropical Buttercup
    # MEDS_3_MentalStimulant
    ('plant4',  '002030'), # Pearl-Blue Shelf Fungus
    ('plant6',  '002030'), # Grey Shelf Fungus
    # MEDS_4_AdrenalineStimulant
    ('plant20', '203000'), # Red-Green Tree Fungus
    ('plant21', '203000'), # Fleshy Rooted Plant
    ('plant28', '203000'), # Carnivorous Trap Plant

    # MEDS_6_clarityTonic
    ('plant3',  '400000'), # Red Toadstool
    ('plant29', '600000'), # Fabacae
    # MEDS_7_herculeanTonic
    ('plant5',  '808000'), # Yellow Mushrooms

    # MEDS_8_EnduranceEmphasisDrug
    ('plant25', '8000b0'), # Giant Bloom (TEST IF THIS IS ACCESSIBLE ON AGENT Y ISLAND)
    ('plant19', '000080'), # Blue-Capped Toadstool
    # MEDS_9_MuscleEmphasisDrug
    ('plant32', '800080'), # Large Jungle Flower
    ('plant34', '400080'), # Fleshy Purple Fruit
    # MEDS_10_BrainEmphasisDrug
    ('plant8',  '867344'), # Sponge-Like Fungus
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
    'plant8',  'plant10', # Brain Emphasis
    'plant3',  'plant29', # Clarity Tonic (Red)
    'plant5',             # Herculean Tonic (Yellow)
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
    miasmap.image = tmp

class ShuffleBucket(object):
    def __init__(self, shuffle_mode, seed):
        self.shuffle_mode = shuffle_mode
        self.bucket = {}
        self.random = random.Random(seed)
        if shuffle_mode == 1:
            # Counter to ensure all items are given out at least once
            self.rr_counter = 0

class PlantCluster(object):
    def __init__(self, idx, x, y):
        self.contents = []
        self.x1 = self.x2 = x
        self.y1 = self.y2 = y
        self.add(idx, x, y)
    def add(self, idx, x, y):
        self.x1 = min(self.x1, x - CLUSTER_DISTANCE)
        self.x2 = max(self.x2, x + CLUSTER_DISTANCE)
        self.y1 = min(self.y1, y - CLUSTER_DISTANCE)
        self.y2 = max(self.y2, y + CLUSTER_DISTANCE)
        self.contents.append(idx)
    def intersects(self, other):
        return ((self.x1 >= other.x1 and self.x1 <= other.x2)  \
             or (self.x2 >= other.x1 and self.x2 <= other.x2)  \
             or (self.x1 <= other.x1 and self.x2 >= other.x2)) \
           and ((self.y1 >= other.y1 and self.y1 <= other.y2)  \
             or (self.y2 >= other.y1 and self.y2 <= other.y2)  \
             or (self.y1 <= other.y1 and self.y2 >= other.y2))
    def merge(self, other):
        self.x1 = min(self.x1, other.x1)
        self.x2 = max(self.x2, other.x2)
        self.y1 = min(self.y1, other.y1)
        self.y2 = max(self.y2, other.y2)
        self.contents.extend(other.contents)


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
    search_inst_ids = { inst_node_names.index(k): v for k,v in m.iteritems() if k in inst_node_names }

    points = {}

    for inod_fname,compressed_file in main_rs5.iteritems():
        if compressed_file.type != 'INOD':
            continue
        inod_index = int(inod_fname[9:]) # strip "inst_node" from filename
        assert(inod_fname == 'inst_node%i' % inod_index)
        decompressed = compressed_file.decompress()
        nodes = inst_node.parse_inod(StringIO(decompressed), inst_node_names)
        for node in nodes:
            node_name, node_name_idx, u1, x, y, z, u2, u3, u4, u5, u6 = node
            try:
                plant = search_inst_ids[node_name_idx]
                points.setdefault(plant, []).append((int(x), int(y)))
            except KeyError:
                pass
    for plant, colour in spoiler_plant_colours.iteritems():
        for x,y in points.get(plant, []):
            miasmap.plot_square(int(x), int(y), 20, colour, additive=False)
    # Anything requested without a colour:
    for plant in set(points).difference(spoiler_plant_colours):
        for x,y in points[plant]:
            miasmap.plot_square(int(x), int(y), 20, (255, 255, 255), additive=False)
    miasmap.save_image('spoiler.jpg')

def generate_and_install_randomizer(seed=None):
    randomizer_mod_name = os.path.splitext(randomizer_filename)[0]
    print('Removing previous %s from main.rs5...' % randomizer_mod_name) # FIXME: may add seed numbers to fname?
    rs5mod.rm_mod('main.rs5', [randomizer_mod_name])
    if os.path.exists(randomizer_filename):
        print('Deleting old %s' % randomizer_filename)
        os.remove(randomizer_filename)

    install_path = find_install_path()
    env_rs5 = load_environment_rs5(install_path)
    models = get_plants_notes_list(env_rs5)

    main_rs5 = load_main_rs5(install_path)
    inst_header_fp = inst_header.open_inst_header_from_rs5(main_rs5)
    inst_node_names = inst_header.get_name_list(inst_header_fp)

    # Reading the height map to find any potentially underground/floating
    # items. TODO: This height map is only approximate. Might want to read the
    # actual terrain vertex data for more accurate tests.
    height_map = cterr_hmap.open_cterr_hmap_from_rs5(main_rs5)

    if seed is None:
        seed = random.randrange(0, 2**32)
    print('Using seed %u' % seed)
    notes_bucket = ShuffleBucket(SHUFFLE_MODE_NOTES, seed)
    plants_bucket = ShuffleBucket(SHUFFLE_MODE_PLANTS, seed+1)
    fungi_bucket = ShuffleBucket(SHUFFLE_MODE_PLANTS, seed+2)
    shuffle_buckets = [
            notes_bucket,
            plants_bucket,
            fungi_bucket
    ]
    search_inst_ids = {}
    for model,game_object in models.iteritems():
        if model not in inst_node_names:
            print('NOTE: %s referenced in environment.rs5 not found in inst_header (no instances of this game_object in the map)' % model)
            continue
        inst_name_idx = inst_node_names.index(model)
        search_inst_ids[inst_name_idx] = game_object
        if game_object.lower().startswith('note'):
            bucket = notes_bucket
        elif game_object in FUNGI_BUCKET:
            bucket = fungi_bucket
        else:
            bucket = plants_bucket
        bucket.bucket.setdefault(game_object, []).append(inst_name_idx)

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
    item_clusters = {}
    item_ids = {}
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
        for node in nodes:
            node_name, node_name_idx, u1, x, y, z, u2, u3, u4, u5, u6 = node
            # u1 appears to be a unique object ID
            if node_name_idx not in search_inst_ids:
                continue
            relevant = True
            if z < 0:
                print('WARNING: %s located %f below Ocean level' % (node_name, z), search_inst_ids[node_name_idx], inod_fname, node)
            altitude = z - height_map[int(x/2.0), int(y/2.0)]
            if altitude < 0 or altitude > 5:
                bad_nodes.append((node, altitude, inst_node_bounds[inod_index])) # TODO: Only add if actually bad, for now adding all for testing
            item_clusters.setdefault(search_inst_ids[node_name_idx], []).append(PlantCluster(u1, x, y))
            item_ids.setdefault(search_inst_ids[node_name_idx], []).append(u1)
        if relevant:
            relevant_inodes.append(inod_fname)

    dump_bad_nodes()

    item_id_map = {}
    for bucket in shuffle_buckets:
        if bucket.shuffle_mode == 1:
            all_items_in_bucket = []
            valid_note_types = []
            for game_object in bucket.bucket:
                item_instances = item_ids.get(game_object, [])
                if item_instances:
                    all_items_in_bucket.extend(item_instances)
                    valid_note_types.append(game_object)
                    #print(game_object, item_instances)
                else:
                    print('Skipping %s with 0 instances in the map' % game_object)
            print('Total notes:  %i' % len(all_items_in_bucket))
            print('Unique notes: %i' % len(valid_note_types))
            # Extend the list of unique notes so there is enough for the total
            # notes. We want to ensure at least one of each note is given out,
            # without making any specific note more or less likely to appear.
            # The first shuffle before extending the list ensures that when we
            # do remove notes it will be random which ones get removed, then we
            # extend that list by repetition and cut it to match the number of
            # total notes we need to give out, then shuffle again to ensure all
            # is as random as possible
            # TODO: We could alternatively not distribute duplicate notes at
            # all? From the player's POV this would look pretty similar since
            # picking up a note removes all duplicates according to the removal
            # mode, but it might make some notes harder to find...
            # TODO: Or, we could replace some of the duplicate notes with our
            # own hints revealing some ingredient locations...
            bucket.random.shuffle(valid_note_types)
            note_bucket = (valid_note_types * (len(all_items_in_bucket) // len(valid_note_types) + 1))[:len(all_items_in_bucket)]
            bucket.random.shuffle(note_bucket)
            for item_id in all_items_in_bucket:
                item_id_map[item_id] = bucket.random.choice(bucket.bucket[note_bucket.pop()])
            assert(len(note_bucket) == 0)
        elif bucket.shuffle_mode == 2:
            keys,vals = map(list, zip(*bucket.bucket.items()))
            bucket.random.shuffle(keys)
            bucket.bucket.update(dict(zip(keys,vals)))
            print('DEBUG / SPOILER: Shuffled bucket:', bucket.bucket)
        elif bucket.shuffle_mode == 3:
            all_clusters_in_bucket = []
            num_clusters_of_plant = {}
            for game_object in bucket.bucket:
                clusters = item_clusters[game_object]
                initial_len = len(clusters)
                making_progress = True
                while making_progress:
                    making_progress = False
                    i = 0
                    while i < len(clusters):
                        j = i + 1
                        while j < len(clusters):
                            if clusters[i].intersects(clusters[j]):
                                clusters[i].merge(clusters.pop(j))
                                making_progress = True
                            else:
                                j += 1
                        i += 1
                final_len = len(clusters)
                print('%i instances of %s grouped into %i clusters' % (initial_len, game_object, final_len))
                all_clusters_in_bucket.extend(clusters)
                num_clusters_of_plant[game_object] = final_len
            print('Shuffling clusters...')
            bucket.random.shuffle(all_clusters_in_bucket)
            for game_object in bucket.bucket:
                num_clusters = num_clusters_of_plant[game_object]
                for cluster in all_clusters_in_bucket[:num_clusters]:
                    for plant_id in cluster.contents:
                        item_id_map[plant_id] = bucket.random.choice(bucket.bucket[game_object])
                all_clusters_in_bucket = all_clusters_in_bucket[num_clusters:]
            assert(len(all_clusters_in_bucket) == 0)

    randomizer_rs5 = rs5archive.Rs5ArchiveEncoder(randomizer_filename)
    for inod_fname in relevant_inodes:
        decompressed = main_rs5[inod_fname].decompress()
        nodes = list(inst_node.parse_inod(StringIO(decompressed), inst_node_names))
        new_nodes = []
        for node in nodes:
            node_name, node_name_idx, u1, x, y, z, u2, u3, u4, u5, u6 = node
            if node_name_idx in search_inst_ids:
                for bucket in shuffle_buckets:
                    if bucket.shuffle_mode == 2:
                        game_object = models[node_name]
                        if game_object in bucket.bucket:
                            node_name_idx = bucket.random.choice(bucket.bucket[game_object])
                            #print('SPOILER: Replaced %s with %s' % (node_name, inst_node_names[node_name_idx]))
                            #print('DEBUG: Replaced %s with %i' % (node_name, node_name_idx)) # Not printing replaced name to avoid spoilers. Even printing ID might be too much...
                            node_name = '_replaced' # Not used, just setting to avoid confusion
                            break
                    elif bucket.shuffle_mode in (1, 3):
                        # Shuffling happened above, we just apply the
                        # replacements specified in item_id_map.
                        if u1 in item_id_map:
                            node_name_idx = item_id_map[u1]
                            node_name = '_replaced'
                            break
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

    return seed

def parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--seed', type=int)
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    seed = generate_and_install_randomizer(args.seed)
    # spoil('plant31')
    #spoil('note1')
    #spoil(cure_plants)
    #spoil(important_plants)
    #spoil(FUNGI_BUCKET)
    spoil(None)
    print('Miasmata Randomizer Seed: %u' % seed)
