#!/usr/bin/env python2.7

from __future__ import print_function

from StringIO import StringIO
import random
import os

import rs5archive
import rs5file
import rs5mod
import environment
import inst_header
import inst_node

# 1: Dumb random mode, all plants just selected at random. Way to easy to find goal items, while also not guaranteed that goal items will exist.
# 2: Shuffle kinds of plants (all instances of x will now be instances of y)
# 3: Unimplemented, planning to randomize groups of nearby plants together
SHUFFLE_MODE_NOTES  = 1 # FIXME: Guarantee all notes spawn at least one instance
SHUFFLE_MODE_PLANTS = 2

# "randomizer.rs5mod" is causing the game to crash on launch if the rs5mod
# is in the game directory, maybe that same issue with naming anything
# after "e"? I thought I tested the rs5mod extension avoiding that? Dangit
randomizer_filename = 'randomizer.dss5mod'

# TODO: Blacklist:
# - Orbital launch site East of Rigel
min_z_blacklist_whole_node = -1.0
# - Developer area above river near spawn
# - Milo island East of Desert
# - Use cterr_hmap to verify nothing else underground / in air

# TODO: Eggplant model is in multiple parts - three takable fruit models +
# leaves that remain. Will need special handling to randomize this later, but
# for now make sure that I cache the leaves models as well
ADDITIONAL_MODELS = {'Eggplant_Leaves1': 'plant34'}

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

def get_plants_notes_list(env_rs5):
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
        if removal_mode == 0:
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
    for node in bad_nodes:
        node_name, node_name_idx, u1, x, y, z, u2, u3, u4, u5, u6 = node
        if z < min_z_blacklist_whole_node: # Way too far below water, unreachable
            colour = (255,0,0)
        elif z <= 0: # Some legitimately below water level, but need to check
            colour = (0,255,0)
        else:
            colour = (0,0,128+int(z))
        miasmap.plot_square(int(x), int(y), 20, colour)
    miasmap.save_image('bad_nodes.jpg')

class ShuffleBucket():
    def __init__(self, shuffle_mode, bucket):
        self.shuffle_mode = shuffle_mode
        self.bucket = bucket
        if shuffle_mode == 1:
            # Counter to ensure all items are given out at least once
            self.rr_counter = 0

def spoil(plant):
    import miasmap
    tmp = miasmap.image
    miasmap.image = tmp.copy()
    miasmap.pix = miasmap.image.load()

    install_path = find_install_path()

    env_rs5 = load_environment_rs5(install_path)
    models = get_plants_notes_list(env_rs5)
    m = [ k for (k,v) in models.items() if v == plant ]
    print('Searching for', m)

    main_rs5 = load_main_rs5(install_path)
    inst_header_fp = inst_header.open_inst_header_from_rs5(main_rs5)
    inst_node_names = inst_header.get_name_list(inst_header_fp)
    search_inst_ids = [ inst_node_names.index(x) for x in m ]

    for inod_fname,compressed_file in main_rs5.iteritems():
        if compressed_file.type != 'INOD':
            continue
        decompressed = compressed_file.decompress()
        nodes = inst_node.parse_inod(StringIO(decompressed), inst_node_names)
        for node in nodes:
            node_name, node_name_idx, u1, x, y, z, u2, u3, u4, u5, u6 = node
            if node_name_idx in search_inst_ids:
                miasmap.plot_square(int(x), int(y), 20, (0, 255, 0))
    miasmap.save_image('spoiler.jpg')
    sys.exit(0)

def generate_and_install_randomizer():
    print('Removing previous randomizer from main.rs5...') # FIXME: may add seed numbers to fname?
    rs5mod.rm_mod('main.rs5', [randomizer_filename])
    try:
        os.remove(randomizer_filename)
    except:
        pass

    install_path = find_install_path()
    env_rs5 = load_environment_rs5(install_path)
    models = get_plants_notes_list(env_rs5)
    #print(models)

    main_rs5 = load_main_rs5(install_path)
    inst_header_fp = inst_header.open_inst_header_from_rs5(main_rs5)
    inst_node_names = inst_header.get_name_list(inst_header_fp)
    #print(inst_node_names)

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

    relevant_inodes = []
    for inod_fname,compressed_file in main_rs5.iteritems():
        if compressed_file.type != 'INOD':
            continue
        #print(inod_fname)
        decompressed = compressed_file.decompress()
        nodes = inst_node.parse_inod(StringIO(decompressed), inst_node_names)
        # TODO: Only randomize most detailed inst node LODs, search for
        # instances in less detailed LODs and make sure they match
        relevant = False
        blacklist = False
        for node in nodes:
            node_name, node_name_idx, u1, x, y, z, u2, u3, u4, u5, u6 = node
            # u1 appears to be a unique object ID
            if node_name_idx not in search_inst_ids:
                continue
            relevant = True
            if z < min_z_blacklist_whole_node:
                print('WARNING: Bad nodes detected in %s, blacklisting' % inod_fname)
                blacklist = True
                break
            elif z < 0:
                print('WARNING: %s located %f below Ocean level' % (node_name, z), search_inst_ids[node_name_idx], inod_fname, node)
            bad_nodes.append(node) # TODO: Only add if actually bad, for now adding all for testing
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
