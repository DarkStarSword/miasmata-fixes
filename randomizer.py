#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from __future__ import print_function

from StringIO import StringIO
import collections
import gc
import random
import os
import re
import sys
import time

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
randomizer_name_template     = 'randomizer_%s'
randomizer_filename_template = 'randomizer_%s.dss5mod'
randomizer_spoiler_template  = 'randomizer_%s_spoiler.jpg'
randomizer_version           = '0.1'

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

# Human-readable names for plants (used in the spoiler map tree view)
plant_names = {
    'plant0':  'Prickly Pear',
    'plant00': 'Violet Cactus',
    'plant1':  'Common White Mushroom',
    'plant2':  'Pawn Shaped Mushroom',
    'plant3':  'Red Toadstool',
    'plant4':  'Pearl-Blue Shelf Fungus',
    'plant5':  'Yellow Mushrooms',
    'plant6':  'Grey Shelf Fungus',
    'plant7':  'Brown Shelf Fungus',
    'plant8':  'Sponge-Like Fungus',
    'plant9':  'Wood Gill Fungus',
    'plant10': 'Trumpet Mushroom',
    'plant11': 'White Spiked Prairie Flower',
    'plant12': 'Pink-White Prairie Flower',
    'plant13': 'Orange Prairie Flower',
    'plant14': 'White Bundle Prairie Flower',
    'plant15': 'Sunflower',
    'plant16': 'Indigo Asteraceae',
    'plant17': 'Red and Yellow Hibiscus',
    'plant18': 'White/Pink Viola',
    'plant19': 'Blue-Capped Toadstool',
    'plant20': 'Red-Green Tree Fungus',
    'plant21': 'Fleshy Rooted Plant',
    'plant22': 'Pink Spotted Lilly',
    'plant23': 'Rainbow Orchard',
    'plant24': 'Titan Plant',
    'plant25': 'Giant Bloom',
    'plant26': 'Bulbous Fruit Plant',
    'plant27': 'Carnivorous Pitcher Plant',
    'plant28': 'Carnivorous Trap Plant',
    'plant29': 'Fabacae',
    'plant30': 'Bio-Luminescent Algae',
    'plant31': 'Blue Scaly Tree Fungus',
    'plant32': 'Large Jungle Flower',
    'plant33': 'Tropical Buttercup',
    'plant34': 'Fleshy Purple Fruit',
}

notes_names = {
    'note0': 'A Bloody Memo about The Cure',
    'note1': 'An Insane Note from Herbert',
    'note2': 'Letter from Sanchez about the Anti-Toxin',
    'note3': 'Map to Bio-Luminescent Algae',
    'note4': 'A Letter from Cornelius about Orchid Extracts', # Not used in game
    'note5': 'A Region Map for the Orchadae-Helius.',
    'note7': 'A Map to a Tall Plant with a Golden Spadix',
    'note8': 'A Regional Map of Outpost Sirius',
    'note9': 'A Letter from Isabela about an Adjuvent.',
    'note10': 'A procedure for developing The Adjuvent',
    'note11': 'A Regional Map for Outpost Rigel',
    'note12': 'A Study of Nepenthes Viri Pitcher Plant',
    'note13': 'A Study of Plant X',
    'note14': 'A Regional Map of Outpost Tau',
    'note15': 'A Document on the Synthesis of Anti-Plague Agent',
    'note16': 'A Study on the Inonotus Caeruleus Fungus',
    'note17': 'A Map to a cache of Pitcher Plants',
    'note18': 'A Map to a cache of Pitcher Plants', # Not used in game
    'noteA1': 'A Map of Outpost Draco',
    'noteA2': 'A Map to Purple Fruit and Jungle Flower',
    'noteA3': 'A Map to Giant Bloom and Blue Cap Mushroom',
    'noteA4': 'A Map to Sponge and Trumpet Mushrooms',
    'noteA5': "A Guide to Cartography and Triangulation 'B','C'",
    'noteA6': 'A Map of a Swamp Trail',
    'noteA7': 'Journal Entry From Herbert #1',
    'noteA8': 'Journal Entry From Herbert #2',
    'noteA9': 'Journal Entry From Sanchez #6',
    'noteAA': 'A codex of island Medicines',
    'noteBB': 'A List of Basic Medicinal Plants',
    'noteCC': 'Document on the Synthesis of Muscle Emphasis Drug',
    'noteDD': 'Document on the Synthesis of Endurance Emphasis Drug', # Mislabeled as Muscle Emphasis in game - fixed by community patch
    'noteEE': 'A List of Adrenaline Stimulants',
    'noteFF': 'A Document about a Mental Clarity Tonic',
    'noteGG': 'A Document about Anti-Hallucination Medicine',
    'noteHH': 'A Document about Potency Enhancers',
    'noteII': 'Photos of Chancellor Kallas',
    'noteJJ': 'Photos of Plague Victims',
    'noteKK': 'A Stack of Photos and Newspaper Clippings',
    'noteLL': 'Instructions for Synthesizing Medicines',
    'noteMM': 'A Pair of Island Photographs',
    'noteNN': 'A Message in a Bottle',
    'noteOO': 'Instructions for Researching Plants',
    'notePP': 'A Plague Photo and Newspaper Article',
    'noteQQ': 'A Photo and Article about Chancellor Kallas',
    'noteRR': 'A Map to a Boat Landing',
    'noteSS': 'A Document about Owl Statues',
    'noteTT': 'A Document on Mapping and Cartography',
    'noteUU': 'Instructions for Brain Emphasis Drug',
    'noteVV': 'Journal Entry from Doctor Sanchez #5',
    'noteWW': 'Journal Entry from Doctor Sanchez #4',
    'noteXX': 'Journal Entry from Doctor Sanchez #3',
    'noteYY': 'Journal Entry from Doctor Sanchez #2',
    'noteZZ': 'Journal Entry from Doctor Sanchez #1',
}

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

def find_install_path(explicit_path=None):
    '''Return the Miasmata install path, trying (in order):
       1. The explicitly provided path
       2. The Windows registry
       3. The current directory
       Returns None if not found.
    '''
    if explicit_path is not None:
        return explicit_path
    try:
        import miasutil
        path = miasutil.find_miasmata_install()
        if os.path.isfile(os.path.join(path, 'main.rs5')):
            return path
    except Exception:
        pass
    if os.path.isfile(os.path.join(os.curdir, 'miasmata.exe')) or \
       os.path.isfile(os.path.join(os.curdir, 'Miasmata.exe')):
        return os.path.abspath(os.curdir)
    return None

def load_main_rs5(install_path, cls=rs5archive.Rs5ArchiveDecoder):
    print('Loading main.rs5...')
    path = os.path.join(install_path, 'main.rs5')
    return cls(open(path, 'rb+'))

def load_environment_rs5(install_path):
    print('Loading environment.rs5...')
    path = os.path.join(install_path, 'environment.rs5')
    return environment.parse_from_archive(path)

# ── Points cache for repeated spoil() calls ──────────────────────────────────
# The INOD scan (iterating every instance-node file to collect plant/note XY
# positions) is the main bottleneck.  _get_cached_points() does this scan once
# and stores a compact {game_object: [(x,y), ...]} dict.  Only plant/note
# positions are retained, so memory usage is small (a few thousand coords).
#
# NOTE: We intentionally do NOT cache the Rs5ArchiveDecoder objects themselves.
# Keeping open 'rb+' file handles to main.rs5 across generate/install/uninstall
# cycles causes stale handle accumulation in 32-bit Python (the handles aren't
# released until the globals are overwritten, not when _rs5_cache_path is
# nulled), which contributes to memory pressure and potential read-corruption
# when rs5mod modifies the file while old handles remain open.
# Opening the archives fresh for each spoil() call is cheap.
_points_cache = {}   # install_path -> {game_object: [(x, y), ...]}

def _get_cached_points(install_path, main_rs5, env_rs5, progress_cb=None):
    '''Scan all INOD files and return {game_object: [(x,y), ...]} for every
    plant/note in the map.  Results are cached by install_path so subsequent
    calls with the same path return immediately.

    progress_cb, if provided, is called as progress_cb(done, total) after each
    INOD file is processed so callers can drive a progress bar.
    '''
    if install_path in _points_cache:
        return _points_cache[install_path]

    models_all = get_plants_notes_list(env_rs5, skip_non_removable=False)
    inst_header_fp = inst_header.open_inst_header_from_rs5(main_rs5)
    inst_node_names = inst_header.get_name_list(inst_header_fp)
    search_inst_ids = {
        inst_node_names.index(k): v
        for k, v in models_all.iteritems()
        if k in inst_node_names
    }

    inod_items = [(f, c) for f, c in main_rs5.iteritems() if c.type == 'INOD']
    print('Scanning %d instance node files for plant/note positions...' % len(inod_items))

    points = {}
    for i, (inod_fname, compressed_file) in enumerate(inod_items):
        if progress_cb:
            progress_cb(i, len(inod_items))
        decompressed = compressed_file.decompress()
        nodes = inst_node.parse_inod(StringIO(decompressed), inst_node_names)
        for node in nodes:
            _, node_name_idx, _, x, y, _, _, _, _, _, _ = node
            if node_name_idx in search_inst_ids:
                points.setdefault(search_inst_ids[node_name_idx], []).append(
                    (int(x), int(y)))

    if progress_cb:
        progress_cb(len(inod_items), len(inod_items))

    print('Done - found positions for %d plant/note types.' % len(points))
    _points_cache[install_path] = points
    return points

def _invalidate_points_cache():
    _points_cache.clear()


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
def dump_bad_nodes(main_rs5=None, install_path=None):
    try:
        import miasmap
    except Exception as e:
        print('Error importing miasmap, no spoiler maps for you', str(e))
        return
    if main_rs5 is not None:
        print('Extracting map texture from main.rs5...')
        miasmap.load_from_rs5(main_rs5, install_path)
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
    def __init__(self, idx, x, y, cluster_dist=CLUSTER_DISTANCE):
        self.cluster_dist = cluster_dist
        self.contents = []
        self.x1 = self.x2 = x
        self.y1 = self.y2 = y
        self.add(idx, x, y)
    def add(self, idx, x, y):
        self.x1 = min(self.x1, x - self.cluster_dist)
        self.x2 = max(self.x2, x + self.cluster_dist)
        self.y1 = min(self.y1, y - self.cluster_dist)
        self.y2 = max(self.y2, y + self.cluster_dist)
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


def spoil(plants, install_path=None, spoiler_filename='spoiler.jpg',
          progress_cb=None):
    if install_path is None:
        install_path = find_install_path()

    import miasmap

    main_rs5 = load_main_rs5(install_path)
    env_rs5  = load_environment_rs5(install_path)

    # Resolve 'plants=None' to all plants before filtering
    if plants is None:
        models = get_plants_notes_list(env_rs5, skip_non_removable=False)
        plants = [x for x in models.values() if x.startswith('plant')]
    elif not isinstance(plants, (list, tuple)):
        plants = (plants,)

    # load_from_rs5 prints a message and does work only on first call per path
    miasmap.load_from_rs5(main_rs5, install_path)

    # _get_cached_points scans all INODs on first call (driving the progress
    # bar via progress_cb), then returns instantly from cache on repeat calls.
    plants_lower = {p.lower() for p in plants}
    points_all = _get_cached_points(install_path, main_rs5, env_rs5,
                                    progress_cb=progress_cb)

    # Filter to the requested subset using case-insensitive comparison
    # (note capitalisation is inconsistent across game data files)
    points = {k: v for k, v in points_all.iteritems()
              if k.lower() in plants_lower}

    print('Plotting %d plant/note type(s)...' % len(points))

    tmp = miasmap.image
    miasmap.image = tmp.copy()
    miasmap.pix = miasmap.image.load()

    for plant, colour in spoiler_plant_colours.iteritems():
        for x, y in points.get(plant, []):
            miasmap.plot_square(int(x), int(y), 20, colour, additive=False)
    # Anything requested but without an assigned colour gets white
    for plant in set(points).difference(spoiler_plant_colours):
        for x, y in points[plant]:
            miasmap.plot_square(int(x), int(y), 20, (255, 255, 255), additive=False)
    miasmap.save_image(spoiler_filename)
    miasmap.image = tmp

def remove_previous_randomizer(install_path=None):
    if install_path is None:
        install_path = find_install_path()
    main_rs5_path = os.path.join(install_path, 'main.rs5')
    main_rs5 = rs5mod.Rs5ModArchiveUpdater(open(main_rs5_path, 'rb+'))
    rs5mod.do_add_undo(main_rs5)
    installed_mods = list(rs5mod.rs5_mods(main_rs5))
    print('Installed mods:\n  %s' % '\n  '.join(installed_mods))
    for mod in installed_mods:
        match = re.match(r'MIASMOD\\MODS\\(randomizer[_0-9a-z-]*)\.manifest', mod, re.IGNORECASE)
        if match:
            old_mod_name = match.group(1)
            print('Removing previous %s from main.rs5...' % old_mod_name)
            rs5mod.do_rm_mod(main_rs5, old_mod_name)

def get_installed_randomizer_names(install_path):
    '''Return list of installed randomizer mod names, or [] if none / error.'''
    try:
        main_rs5_path = os.path.join(install_path, 'main.rs5')
        main_rs5 = rs5archive.Rs5ArchiveDecoder(open(main_rs5_path, 'rb'))
        installed_mods = list(rs5mod.rs5_mods(main_rs5))
        names = []
        for mod in installed_mods:
            match = re.match(r'MIASMOD\\MODS\\(randomizer[_0-9a-z-]*)\.manifest', mod, re.IGNORECASE)
            if match:
                names.append(match.group(1))
        return names
    except Exception:
        return []

# Required to install with miasmod without errors
# REFACTORME: Move to rs5mod
def add_mod_meta(rs5, name, version):
    chunks = collections.OrderedDict((
        ('NAME', rs5file.Rs5ChunkEncoder('NAME', name)),
        ('VRSN', rs5file.Rs5ChunkEncoder('VRSN', version))
    ))
    chunks = rs5file.Rs5ChunkedFileEncoder('META', rs5mod.mod_meta_file, 1, chunks)
    rs5.add_from_buf(chunks.encode())

def generate_and_install_randomizer(install_path=None, seed=None,
                                    note_mode=SHUFFLE_MODE_NOTES,
                                    plant_mode=SHUFFLE_MODE_PLANTS,
                                    fungi_mode=SHUFFLE_MODE_PLANTS,
                                    cluster_dist=CLUSTER_DISTANCE,
                                    install=True):
    if install_path is None:
        install_path = find_install_path()

    if install:
        remove_previous_randomizer(install_path)

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

    seed_str = encode_seed_string(seed, note_mode, plant_mode, fungi_mode, cluster_dist)
    randomizer_filename = randomizer_filename_template % seed_str
    randomizer_name = randomizer_name_template % seed_str

    notes_bucket = ShuffleBucket(note_mode, seed)
    plants_bucket = ShuffleBucket(plant_mode, seed+1)
    fungi_bucket = ShuffleBucket(fungi_mode, seed+2)
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
        if game_object.lower().startswith('note'):
            bucket = notes_bucket
        elif game_object in FUNGI_BUCKET:
            bucket = fungi_bucket
        else:
            bucket = plants_bucket
        if bucket.shuffle_mode == 0:
            continue  # Mode 0: leave this category unshuffled
        search_inst_ids[inst_name_idx] = game_object
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
            item_clusters.setdefault(search_inst_ids[node_name_idx], []).append(
                PlantCluster(u1, x, y, cluster_dist))
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

    randomizer_rs5 = rs5archive.Rs5ArchiveEncoder(
        os.path.join(install_path, randomizer_filename))
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
    add_mod_meta(randomizer_rs5, randomizer_name, randomizer_version)
    randomizer_rs5.save()
    del randomizer_rs5 # Ensures file is closed

    print('Saved %s' % randomizer_filename)
    #print('rs5-extractor.py -f main.rs5 --add-mod %s' % randomizer_filename)
    if install:
        print('Installing new randomizer to main.rs5...')
        rs5mod.add_mod(os.path.join(install_path, 'main.rs5'),
                       [os.path.join(install_path, randomizer_filename)])

    # Release the large intermediate buffers (decoded INODs, item maps, etc.)
    # and explicitly run the cyclic GC.  In 32-bit Python, the heap can become
    # fragmented after several generate/install/uninstall cycles otherwise,
    # eventually causing MemoryError on the next large zlib.decompress call.
    del main_rs5, env_rs5, item_id_map, item_clusters, item_ids
    del relevant_inodes, height_map
    gc.collect()

    return seed


# ─────────────────────────────────────────────────────────────────────────────
# Seed string encoding / decoding
# ─────────────────────────────────────────────────────────────────────────────

def encode_seed_string(raw_seed, note_mode, plant_mode, fungi_mode, cluster_dist):
    '''Encode settings + raw seed into a compact string safe for filenames.

    Format: {note_mode}{plant_mode}{fungi_mode}-{cluster_dist}-{raw_seed}
    Example: 133-100-1234567890

    This makes the full settings visible to the player and allows sharing
    seeds that exactly reproduce a run including all settings.
    '''
    return '%d%d%d-%d-%u' % (note_mode, plant_mode, fungi_mode,
                              cluster_dist, raw_seed)


def decode_seed_string(s):
    '''Parse a seed string back into its components.

    Returns (raw_seed, note_mode, plant_mode, fungi_mode, cluster_dist) on
    success, or None if the string cannot be parsed.

    Accepts both the new format "133-100-1234567890" and the legacy format
    of a bare integer seed (uses module defaults for settings).
    '''
    s = s.strip()
    # New format: NNNs-ccc-sss where NNN are 1-digit mode values (1-3)
    m = re.match(r'^([0-3])([0-3])([0-3])-(\d+)-(\d+)$', s)
    if m:
        note_mode    = int(m.group(1))
        plant_mode   = int(m.group(2))
        fungi_mode   = int(m.group(3))
        cluster_dist = int(m.group(4))
        raw_seed     = int(m.group(5))
        return (raw_seed, note_mode, plant_mode, fungi_mode, cluster_dist)
    # Legacy format: bare integer
    try:
        raw_seed = int(s)
        if 0 <= raw_seed < 2**32:
            return (raw_seed, SHUFFLE_MODE_NOTES, SHUFFLE_MODE_PLANTS,
                    SHUFFLE_MODE_PLANTS, CLUSTER_DISTANCE)
    except ValueError:
        pass
    return None


# ─────────────────────────────────────────────────────────────────────────────
# GUI
# ─────────────────────────────────────────────────────────────────────────────

def _build_plant_tree_model():
    '''Build a QStandardItemModel for the spoiler map plant/note selector.'''
    from PySide import QtCore, QtGui

    model = QtGui.QStandardItemModel()
    model.setHorizontalHeaderLabels(['Plants / Notes'])

    def make_cat(label):
        item = QtGui.QStandardItem(label)
        item.setEditable(False)
        item.setCheckable(True)
        item.setCheckState(QtCore.Qt.Unchecked)
        # Allow three-state checkbox: unchecked / partial / checked
        item.setFlags(item.flags() | QtCore.Qt.ItemIsTristate)
        return item

    def make_item(label, data):
        item = QtGui.QStandardItem(label)
        item.setEditable(False)
        item.setCheckable(True)
        item.setCheckState(QtCore.Qt.Unchecked)
        item.setData(data, QtCore.Qt.UserRole)
        return item

    def note_sort_key(k):
        '''Sort note keys: numeric suffix first (in numeric order), then alphanumeric.'''
        suffix = k[4:]  # strip 'note' prefix
        if suffix.isdigit():
            return (0, int(suffix), u'')
        return (1, 0, suffix.upper())

    # Cure plants
    cure_cat = make_cat('Cure Ingredients')
    for pname, label in [
        ('plant26', 'Agent X: Bulbous Fruit Plant'),
        ('plant31', 'Agent X: Blue Scaly Tree Fungus'),
        ('plant23', 'Agent Y: Rainbow Orchard'),
        ('plant30', 'Agent Y: Bio-Luminescent Algae'),
        ('plant24', 'Agent Z: Titan Plant'),
        ('plant27', 'Agent Z: Pitcher Plant'),
    ]:
        cure_cat.appendRow(make_item(label, pname))
    model.appendRow(cure_cat)

    # All other plants sorted by key (cure ingredients excluded — they appear above)
    all_plants_cat = make_cat('Other Plants')
    for pname in sorted(plant_names.keys()):
        if pname not in cure_plants:
            all_plants_cat.appendRow(make_item(plant_names[pname], pname))
    model.appendRow(all_plants_cat)

    # Notes — use notes_names dict for complete, human-readable list
    notes_cat = make_cat('Notes')
    for nkey in sorted(notes_names.keys(), key=note_sort_key):
        notes_cat.appendRow(make_item(notes_names[nkey], nkey))
    model.appendRow(notes_cat)

    return model


def start_gui():
    from PySide import QtCore, QtGui
    from randomizer_ui import Ui_MainWindow
    from ui_utils import catch_error
    import traceback

    class _LogWriter(object):
        '''stdout-compatible object that appends lines to a QStandardItemModel.

        Writes are buffered and only flushed to the Qt model at most every
        _INTERVAL seconds.  This avoids the heavy cost of crossing the
        Python/C++ boundary on every print() call (which can easily be
        thousands of times during an RS5 scan) while still keeping the UI
        visibly alive during long operations.
        '''
        _INTERVAL = 0.1  # seconds between UI refreshes

        def __init__(self, list_view):
            self._model = QtGui.QStandardItemModel()
            self._list_view = list_view
            self._buf = ''       # partial line not yet ended with '\n'
            self._pending = []   # complete lines waiting to be added to model
            self._last_flush = 0.0

        def qt_model(self):
            return self._model

        def write(self, text):
            self._buf += text
            if '\n' in self._buf:
                parts = self._buf.split('\n')
                self._buf = parts[-1]
                self._pending.extend(parts[:-1])
            # Flush to Qt at most once per _INTERVAL to keep the event loop
            # responsive without paying the full C++ boundary cost every call.
            now = time.time()
            if now - self._last_flush >= self._INTERVAL:
                self._flush_pending()

        def _flush_pending(self):
            if not self._pending:
                self._last_flush = time.time()
                QtGui.QApplication.processEvents()
                return
            # Check scroll position before insert so we can restore it after.
            scrollbar = self._list_view.verticalScrollBar()
            at_bottom = scrollbar.value() >= scrollbar.maximum()
            # Block per-row signals so N inserts cause one view repaint, not N.
            self._model.blockSignals(True)
            try:
                for line in self._pending:
                    item = QtGui.QStandardItem(line)
                    item.setEditable(False)
                    self._model.appendRow(item)
            finally:
                self._model.blockSignals(False)
            self._pending = []
            self._last_flush = time.time()
            self._model.layoutChanged.emit()
            if at_bottom:
                self._list_view.scrollToBottom()
            QtGui.QApplication.processEvents()

        def flush(self):
            '''Called at the end of a run; ensure all buffered output is shown.'''
            if self._buf:
                self._pending.append(self._buf)
                self._buf = ''
            self._flush_pending()

        def clear(self):
            self._model.clear()
            self._buf = ''
            self._pending = []
            self._last_flush = 0.0

    class MiasRandomizer(QtGui.QMainWindow):
        def __init__(self, parent=None):
            super(MiasRandomizer, self).__init__(parent)

            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)

            self._install_path = None
            self._updating_seed = False
            self._updating_tree = False
            self._map_pixmap = None  # full-res pixmap; rescaled in _update_map_display

            # Log writer — pass the listView so it can auto-scroll
            self._log = _LogWriter(self.ui.listView)
            self.ui.listView.setModel(self._log.qt_model())

            # Plant tree for spoiler map
            self._plant_tree_model = _build_plant_tree_model()
            self.ui.treeView.setModel(self._plant_tree_model)
            self.ui.treeView.expandAll()
            self._plant_tree_model.itemChanged.connect(self._on_plant_item_changed)

            # Populate shuffle mode combo boxes.
            note_modes = [
                ('0 - Don\'t shuffle', 0),
                ('1 - Random assignment', 1),
            ]
            plant_modes = [
                ('0 - Don\'t shuffle', 0),
                ('1 - Random assignment', 1),
                ('2 - Swap plant kinds', 2),
                ('3 - Shuffle clusters (recommended)', 3),
            ]
            for combo, modes, default in [
                (self.ui.comboBox,   note_modes,  SHUFFLE_MODE_NOTES),
                (self.ui.comboBox_2, plant_modes, SHUFFLE_MODE_PLANTS),
                (self.ui.comboBox_3, plant_modes, SHUFFLE_MODE_PLANTS),
            ]:
                for text, mode in modes:
                    combo.addItem(text, mode)
                idx = combo.findData(default)
                if idx >= 0:
                    combo.setCurrentIndex(idx)

            self.ui.lineEdit_2.setText(str(CLUSTER_DISTANCE))

            # Manual signal connections
            self.ui.browse.clicked.connect(self._on_browse_clicked)
            self.ui.install_path.editingFinished.connect(self._on_install_path_changed)
            self.ui.pushButton.clicked.connect(self._on_uninstall_clicked)
            self.ui.pushButton_4.clicked.connect(self._on_generate_clicked)
            self.ui.pushButton_3.clicked.connect(self._on_show_clusters_clicked)
            self.ui.pushButton_2.clicked.connect(self._on_show_spoiler_clicked)
            self.ui.pushButton_5.clicked.connect(self._on_save_spoiler_clicked)

            # Settings → seed
            self.ui.comboBox.currentIndexChanged.connect(self._on_settings_changed)
            self.ui.comboBox_2.currentIndexChanged.connect(self._on_settings_changed)
            self.ui.comboBox_3.currentIndexChanged.connect(self._on_settings_changed)
            self.ui.lineEdit_2.editingFinished.connect(self._on_settings_changed)
            # Seed → settings
            self.ui.lineEdit.textChanged.connect(self._on_seed_text_changed)

        # ── Install path ──────────────────────────────────────────────────

        def _is_valid_install_path(self, path):
            for f in ('main.rs5', 'environment.rs5', 'Miasmata.exe'):
                if not os.path.exists(os.path.join(path, f)):
                    return False
            return True

        def _apply_install_path(self, path):
            self._install_path = path
            self.ui.install_path.setText(path)
            self._refresh_installed_label()

        def _refresh_installed_label(self):
            if not self._install_path:
                self.ui.label_2.setText('Installed Randomizer: (no path set)')
                self.ui.pushButton.setEnabled(False)   # uninstall
                self.ui.pushButton_4.setEnabled(False) # generate
                return
            names = get_installed_randomizer_names(self._install_path)
            installed = bool(names)
            if installed:
                self.ui.label_2.setText('Installed Randomizer: %s' % ', '.join(names))
            else:
                self.ui.label_2.setText('Installed Randomizer: (none)')
            # Uninstall only makes sense when something is installed;
            # generate is blocked when a randomizer is already active (must
            # uninstall first to avoid stacking conflicting mods).
            self.ui.pushButton.setEnabled(installed)         # uninstall
            self.ui.pushButton_4.setEnabled(not installed)   # generate
            self.ui.label_8.setVisible(installed)            # warning

        def find_install_path(self):
            '''Auto-detect install path; called after the window is shown.'''
            path = find_install_path()
            if path and self._is_valid_install_path(path):
                self._apply_install_path(path)
            else:
                self.ui.install_path.setPlaceholderText(
                    'Browse to your Miasmata install directory...')

        # ── Settings / seed sync ──────────────────────────────────────────

        def _read_settings(self):
            note_mode  = self.ui.comboBox.itemData(self.ui.comboBox.currentIndex())
            plant_mode = self.ui.comboBox_2.itemData(self.ui.comboBox_2.currentIndex())
            fungi_mode = self.ui.comboBox_3.itemData(self.ui.comboBox_3.currentIndex())
            try:
                cluster_dist = int(self.ui.lineEdit_2.text())
            except (ValueError, TypeError):
                cluster_dist = CLUSTER_DISTANCE
            return note_mode, plant_mode, fungi_mode, cluster_dist

        def _on_settings_changed(self, *args):
            if self._updating_seed:
                return
            seed_text = self.ui.lineEdit.text().strip()
            if not seed_text:
                return
            decoded = decode_seed_string(seed_text)
            if decoded is None:
                return
            raw_seed = decoded[0]
            note_mode, plant_mode, fungi_mode, cluster_dist = self._read_settings()
            new_seed = encode_seed_string(raw_seed, note_mode, plant_mode, fungi_mode, cluster_dist)
            self._updating_seed = True
            self.ui.lineEdit.setText(new_seed)
            self._updating_seed = False

        def _on_seed_text_changed(self, text):
            if self._updating_seed:
                return
            decoded = decode_seed_string(text.strip())
            if decoded is None:
                return
            raw_seed, note_mode, plant_mode, fungi_mode, cluster_dist = decoded
            self._updating_seed = True
            for combo, mode in [
                (self.ui.comboBox,   note_mode),
                (self.ui.comboBox_2, plant_mode),
                (self.ui.comboBox_3, fungi_mode),
            ]:
                idx = combo.findData(mode)
                if idx >= 0:
                    combo.setCurrentIndex(idx)
            self.ui.lineEdit_2.setText(str(cluster_dist))
            self._updating_seed = False

        # ── Button handlers ───────────────────────────────────────────────

        @catch_error
        def _on_browse_clicked(self):
            path = QtGui.QFileDialog.getExistingDirectory(
                self, 'Select Miasmata Install Directory',
                self._install_path or '')
            if not path:
                return
            if self._is_valid_install_path(path):
                self._apply_install_path(path)
            else:
                QtGui.QMessageBox.warning(
                    self, 'Invalid Directory',
                    'The selected directory does not look like a Miasmata '
                    'install (main.rs5, environment.rs5, Miasmata.exe not found).')

        @catch_error
        def _on_install_path_changed(self):
            path = self.ui.install_path.text().strip()
            if path and os.path.isdir(path) and self._is_valid_install_path(path):
                self._install_path = path
                self._refresh_installed_label()

        def _check_install_path(self):
            if not self._install_path:
                QtGui.QMessageBox.warning(self, 'No Install Path',
                    'Please set the Miasmata install path first.')
                return False
            return True

        def _run_with_log(self, func, *args, **kwargs):
            '''Run func with stdout redirected to the log model.
            Returns (success, result).'''
            self._log.clear()
            old_stdout = sys.stdout
            sys.stdout = self._log
            result = None
            try:
                result = func(*args, **kwargs)
                return True, result
            except Exception:
                print(traceback.format_exc())
                return False, None
            finally:
                sys.stdout = old_stdout
                self._log.flush()  # drain any lines still in the time-based buffer

        @catch_error
        def _on_uninstall_clicked(self):
            if not self._check_install_path():
                return
            ok, _ = self._run_with_log(remove_previous_randomizer, self._install_path)
            _invalidate_points_cache()
            self._refresh_installed_label()
            if ok:
                self.ui.statusbar.showMessage('Randomizer uninstalled.', 5000)

        @catch_error
        def _on_generate_clicked(self):
            if not self._check_install_path():
                return

            seed_text = self.ui.lineEdit.text().strip()
            raw_seed = None
            if seed_text:
                decoded = decode_seed_string(seed_text)
                if decoded:
                    raw_seed = decoded[0]

            note_mode, plant_mode, fungi_mode, cluster_dist = self._read_settings()
            do_install   = self.ui.checkBox.isChecked()
            save_spoiler = self.ui.checkBox_2.isChecked()

            ok, seed_out = self._run_with_log(
                generate_and_install_randomizer,
                install_path=self._install_path,
                seed=raw_seed,
                note_mode=note_mode,
                plant_mode=plant_mode,
                fungi_mode=fungi_mode,
                cluster_dist=cluster_dist,
                install=do_install,
            )
            if not ok:
                return

            seed_str = encode_seed_string(seed_out, note_mode, plant_mode,
                                          fungi_mode, cluster_dist)
            self._updating_seed = True
            self.ui.lineEdit.setText(seed_str)
            self._updating_seed = False

            _invalidate_points_cache()  # main.rs5 was modified; reload on next spoil

            if save_spoiler:
                spoiler_filename = os.path.join(
                    self._install_path,
                    randomizer_spoiler_template % seed_str)
                ok2, _ = self._run_with_log(
                    spoil, None,
                    install_path=self._install_path,
                    spoiler_filename=spoiler_filename)
                if ok2:
                    self.ui.statusbar.showMessage(
                        'Saved spoiler map to %s' % spoiler_filename, 5000)

            self._refresh_installed_label()
            if ok:
                self.ui.statusbar.showMessage(
                    'Generated randomizer with seed %s' % seed_str, 10000)

        @catch_error
        def _on_show_clusters_clicked(self):
            if not self._check_install_path():
                return
            _, cluster_dist_unused, _, cluster_dist = \
                (None,) + self._read_settings()[1:]  # just grab cluster_dist
            note_mode, plant_mode, fungi_mode, cluster_dist = self._read_settings()
            self._run_with_log(self._show_clusters, cluster_dist)

        def _show_clusters(self, cluster_dist):
            '''Print cluster statistics to stdout (redirected to log).'''
            env_rs5 = load_environment_rs5(self._install_path)
            models = get_plants_notes_list(env_rs5)
            main_rs5 = load_main_rs5(self._install_path)
            inst_header_fp = inst_header.open_inst_header_from_rs5(main_rs5)
            inst_node_names = inst_header.get_name_list(inst_header_fp)

            search_inst_ids = {}
            for model, game_object in models.iteritems():
                if model not in inst_node_names:
                    continue
                search_inst_ids[inst_node_names.index(model)] = game_object

            item_clusters = {}
            for inod_fname, compressed_file in main_rs5.iteritems():
                if compressed_file.type != 'INOD':
                    continue
                inod_index = int(inod_fname[9:])
                if inod_index in blacklist_inods:
                    continue
                decompressed = compressed_file.decompress()
                nodes = inst_node.parse_inod(StringIO(decompressed), inst_node_names)
                for node in nodes:
                    _, node_name_idx, u1, x, y, z, _, _, _, _, _ = node
                    if node_name_idx not in search_inst_ids:
                        continue
                    game_object = search_inst_ids[node_name_idx]
                    if game_object.lower().startswith('note'):
                        continue  # Don't cluster notes
                    item_clusters.setdefault(game_object, []).append(
                        PlantCluster(u1, x, y, cluster_dist))

            print('Cluster statistics (cluster distance = %d):' % cluster_dist)
            for game_object in sorted(item_clusters.keys()):
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
                name = plant_names.get(game_object, game_object)
                print('  %-40s %3i instances  ->  %i cluster(s)' % (
                    name, initial_len, len(clusters)))

        def _on_scan_progress(self, done, total):
            '''Progress callback passed to spoil() → _get_cached_points().
            Only called during a cold-cache INOD scan; ignored on cache hits.'''
            self.ui.progressBar.setMaximum(total)
            self.ui.progressBar.setValue(done)
            QtGui.QApplication.processEvents()

        def _run_spoil(self, selected, spoiler_filename):
            '''Run spoil() with progress bar, returning (ok, _).'''
            need_scan = self._install_path not in _points_cache
            if need_scan:
                self.ui.progressBar.setValue(0)
                self.ui.progressBar.setVisible(True)
            try:
                return self._run_with_log(
                    spoil, selected,
                    install_path=self._install_path,
                    spoiler_filename=spoiler_filename,
                    progress_cb=self._on_scan_progress)
            finally:
                self.ui.progressBar.setVisible(False)

        @catch_error
        def _on_show_spoiler_clicked(self):
            if not self._check_install_path():
                return
            selected = self._get_selected_items()
            if not selected:
                QtGui.QMessageBox.information(self, 'Nothing Selected',
                    'Please check one or more plants/notes in the list.')
                return
            import tempfile
            tmp_path = os.path.join(tempfile.gettempdir(),
                                    'randomizer_spoiler_preview.jpg')
            ok, _ = self._run_spoil(selected, tmp_path)
            if ok:
                self._display_image(tmp_path)

        @catch_error
        def _on_save_spoiler_clicked(self):
            if not self._check_install_path():
                return
            selected = self._get_selected_items()
            if not selected:
                QtGui.QMessageBox.information(self, 'Nothing Selected',
                    'Please check one or more plants/notes in the list.')
                return
            path, _ = QtGui.QFileDialog.getSaveFileName(
                self, 'Save Spoiler Map', '', 'JPEG Images (*.jpg)')
            if not path:
                return
            ok, _ = self._run_spoil(selected, path)
            if ok:
                self._display_image(path)
                self.ui.statusbar.showMessage('Saved spoiler map to %s' % path, 5000)

        def _get_selected_items(self):
            selected = []
            def walk(item):
                for row in range(item.rowCount()):
                    child = item.child(row)
                    data = child.data(QtCore.Qt.UserRole)
                    if data and child.checkState() == QtCore.Qt.Checked:
                        selected.append(data)
                    walk(child)
            walk(self._plant_tree_model.invisibleRootItem())
            return selected

        def _on_plant_item_changed(self, item):
            '''Handle check-state changes in the plant/note tree.

            Category headers: propagate their state to all children.
            Clicking a partially-checked category selects all (Unchecked →
            Checked; PartiallyChecked → Checked; Checked → Unchecked).

            Leaf items: update the parent header to reflect the aggregate
            state (Checked / Unchecked / PartiallyChecked).
            '''
            if self._updating_tree:
                return
            self._updating_tree = True
            try:
                parent = item.parent()
                if parent is None:
                    # Top-level category changed by user click.
                    state = item.checkState()
                    if state == QtCore.Qt.PartiallyChecked:
                        # Force partial → checked so clicking a mixed
                        # category always means "select all".
                        state = QtCore.Qt.Checked
                        item.setCheckState(state)
                    for row in range(item.rowCount()):
                        item.child(row).setCheckState(state)
                else:
                    # Leaf item changed — update parent tristate.
                    child_states = set(
                        parent.child(r).checkState()
                        for r in range(parent.rowCount()))
                    if child_states == {QtCore.Qt.Checked}:
                        parent.setCheckState(QtCore.Qt.Checked)
                    elif child_states == {QtCore.Qt.Unchecked}:
                        parent.setCheckState(QtCore.Qt.Unchecked)
                    else:
                        parent.setCheckState(QtCore.Qt.PartiallyChecked)
            finally:
                self._updating_tree = False

        def _display_image(self, path):
            pixmap = QtGui.QPixmap(path)
            if pixmap.isNull():
                QtGui.QMessageBox.warning(self, 'Image Error',
                    'Could not load image: %s' % path)
                return
            self._map_pixmap = pixmap
            self.ui.tabWidget.setCurrentWidget(self.ui.tab_2)
            # Defer the scale until the tab's viewport has finished laying out
            QtCore.QTimer.singleShot(0, self._update_map_display)

        def _update_map_display(self):
            '''Scale the stored pixmap to fit the scroll area viewport.'''
            if self._map_pixmap is None:
                return
            vp = self.ui.scrollArea.viewport()
            scaled = self._map_pixmap.scaled(
                vp.width(), vp.height(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation)
            self.ui.map_label.setPixmap(scaled)
            self.ui.map_label.resize(scaled.size())
            # Remove the hardcoded minimum so no spurious scrollbars appear
            self.ui.scrollAreaWidgetContents.setMinimumSize(QtCore.QSize(0, 0))
            self.ui.scrollAreaWidgetContents.resize(scaled.size())

        def resizeEvent(self, event):
            super(MiasRandomizer, self).resizeEvent(event)
            if self.ui.tabWidget.currentWidget() is self.ui.tab_2:
                self._update_map_display()

    # ── Launch ────────────────────────────────────────────────────────────
    app = QtGui.QApplication(sys.argv)

    window = MiasRandomizer()
    window.show()
    window.find_install_path()

    app.exec_()
    del window


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(
        description='Miasmata Randomizer - run with no arguments to launch the GUI')
    parser.add_argument('-g', '--generate', action='store_true',
        help='Generate and install a randomizer without the GUI')
    parser.add_argument('-s', '--seed', type=int,
        help='RNG seed to use (implies --generate)')
    parser.add_argument('--no-install', action='store_true',
        help='Generate the .dss5mod file but do not install it into main.rs5')
    parser.add_argument('--no-spoiler', action='store_true',
        help='Skip generating the spoiler map (CLI mode only)')
    parser.add_argument('--note-mode', type=int, default=SHUFFLE_MODE_NOTES,
        metavar='MODE',
        help='Note shuffle mode 1-3 (default: %d)' % SHUFFLE_MODE_NOTES)
    parser.add_argument('--plant-mode', type=int, default=SHUFFLE_MODE_PLANTS,
        metavar='MODE',
        help='Plant shuffle mode 1-3 (default: %d)' % SHUFFLE_MODE_PLANTS)
    parser.add_argument('--fungi-mode', type=int, default=SHUFFLE_MODE_PLANTS,
        metavar='MODE',
        help='Fungi shuffle mode 1-3 (default: %d)' % SHUFFLE_MODE_PLANTS)
    parser.add_argument('--cluster-dist', type=int, default=CLUSTER_DISTANCE,
        metavar='DIST',
        help='Cluster distance (default: %d)' % CLUSTER_DISTANCE)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    if args.generate or args.seed is not None:
        # ── CLI / headless mode ───────────────────────────────────────────
        install_path = find_install_path()
        if install_path is None:
            sys.exit('Could not find Miasmata install path. '
                     'Run from the Miasmata directory or check the registry.')

        seed = generate_and_install_randomizer(
            install_path=install_path,
            seed=args.seed,
            note_mode=args.note_mode,
            plant_mode=args.plant_mode,
            fungi_mode=args.fungi_mode,
            cluster_dist=args.cluster_dist,
            install=not args.no_install,
        )

        seed_str = encode_seed_string(seed, args.note_mode, args.plant_mode,
                                      args.fungi_mode, args.cluster_dist)
        print('Miasmata Randomizer Seed: %s' % seed_str)

        if not args.no_spoiler:
            spoiler_filename = os.path.join(install_path,
                                            randomizer_spoiler_template % seed_str)
            spoil(None, install_path=install_path, spoiler_filename=spoiler_filename)
    else:
        # ── GUI mode ──────────────────────────────────────────────────────
        start_gui()
