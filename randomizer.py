#!/usr/bin/env python2.7

from __future__ import print_function

import os
from StringIO import StringIO

import rs5archive
import rs5file
import environment
import inst_header
import inst_node

# TODO: Eggplant model is in multiple parts - three takable fruit models +
# leaves that remain. Will need special handling to randomize this later, but
# for now make sure that I cache the leaves models as well
ADDITIONAL_MODELS = {'Eggplant_Leaves1': 'plant34'}

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
    for modelset,item in env_rs5['player']['pick_objects'].iteritems():
        if not modelset.startswith('modelsets\\'):
            continue
        if not item.startswith('plant') and not item.startswith('note'):
            continue
        model_name = modelset.split('\\')[1]
        #print(item, model_name)
        ret[model_name] = item
    return ret

def generate_randomizer_inst_node_cache():
    install_path = find_install_path()
    env_rs5 = load_environment_rs5(install_path)
    models = get_plants_notes_list(env_rs5)
    #print(models)

    main_rs5 = load_main_rs5(install_path)
    inst_header_fp = inst_header.open_inst_header_from_rs5(main_rs5)
    inst_node_names = inst_header.get_name_list(inst_header_fp)
    #print(inst_node_names)

    search_inst_ids = {}
    for model,item in models.iteritems():
        if model not in inst_node_names:
            print('NOTE: %s referenced in environment.rs5 not found in inst_header (no instances of this item in the map)' % model)
            continue
        inst_name_idx = inst_node_names.index(model)
        #print(inst_name_idx, item, model)
        #search_inst_ids.append(inst_name_idx)
        search_inst_ids[inst_name_idx] = item

    for inod_fname,compressed_file in main_rs5.iteritems():
        if compressed_file.type != 'INOD':
            continue
        #print(inod_fname)
        decompressed = compressed_file.decompress()
        nodes = inst_node.parse_inod(StringIO(decompressed), inst_node_names)
        for node in nodes:
            node_name, node_name_idx, u1, x, y, z, u2, u3, u4, u5, u6 = node
            # u1 appears to be a unique object ID
            if node_name_idx not in search_inst_ids:
                continue
            if z < 0:
                print(search_inst_ids[node_name_idx], inod_fname, node)


if __name__ == '__main__':
    generate_randomizer_inst_node_cache()
