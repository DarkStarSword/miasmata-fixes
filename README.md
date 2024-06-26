Miasmata Fixes
==============

Requirements:
----------------------
- Python 2.7.x
- [Microsoft Visual C++ Compiler for Python 2.7](https://web.archive.org/web/20170210071654/https://download.microsoft.com/download/7/9/6/796EF2E4-801B-4FC4-AB28-B59FBF6D907B/VCForPython27.msi)
- [Microsoft Visual C++ 2008 Redistributable Package (x86) ](https://web.archive.org/web/20171019151356/http://download.microsoft.com/download/1/1/1/1116b75a-9ec3-481a-a3c8-1777b5381140/vcredist_x86.exe)

Installation
----------------------
- Add the location of MSVCP90.dll (installed with the C++ 2008 Redistributable Package) to your system path
- ``pip install -r requirements.txt``

---------

- To build **Miaschiev**, **Miasmod**, and **Miaspatch**, run:
    - ``miaschiev-bbfreeze.py``
    - ``miasmod-bbfreeze.py``
    - ``miaspatch-bbfreeze.py``

Builds are output to the ``miaschiev``, ``miasmod``, and ``miaspatch`` directories.

---------

Miaschiev
---------
This Python application can show the progress towards several achievements:
- Shows which parts of the coast have been mapped, and highlights any missing
  sections.
- Shows which urns have been lit, and which ones are remaining. Note that this
  displays everything listed in the saved game, and in some cases camp fires
  may show up as well for an unknown reason. It does not yet cross-check these
  with the urns listed in the game's Markers file.
- Shows how many notes have been collected.
- Shows the number of unique plants/fungi that have been collected.
- If it detects that the glitched Sanchez #1 note has been picked up but was
  not added to the journal (a bug fixed by Miaspatch), it also gives
  the option to reset the note so it can be picked up again from the camp where
  it was originally found.

Miasmod
---------
A Python application for creating game mods. Example mods are available in the ``mods`` directory.   

Can modify:
- ``environment.rs5``
- ``main.rs5``
- ``saves.dat``   


See <https://steamcommunity.com/app/223510/discussions/0/630800445647188169/> for more information.
### Example mods ###
- ``ailurophobia.miasmod``
  - Removes the creature
- ``cartographobia.miasmod``
  - Prevents  map from being filled in when picking up notes
  - Removes the effect of the mental clarity tonic (does not remove the tonic itself, only its effect)
  - Does not clear any existing map data (requires a new save)
- ``dehydrated.miasmod``
  - Disables water jugs
  - Only allows a single drink of water to be carried in the canteen at a time
- ``insomnia.miasmod``
  - Disables sleeping in beds
  - Removes tiredness
  - Has not been tested enough to fully confirm functionality

Miaspatch
---------
A Python application for applying the unofficial community patch.
### Changes: ###
- Fixes broken achievements: 
  - ``Botanical Bad A**``
  - ``Just doing some light reading?``
  - ``Oh, my glorious brain...``
  - ``The Bored Cartographer``
- Fixes broken ``Sanchez #1`` note that incorrectly registers as ``Sanchez #3``
- Fixes cut off Pitcher plant research link on the objectives page
- Fixes missing Titan plant research link on the objectives page
- Fixes mislabeled ``document on the muscle emphasis drug`` in the notes index to read ``endurance emphasis drug``
- Hammock is now usable as a bed
- Patch allowing the game to use 4 GB of memory, fixing some crashes
- Removes five urn icons from the map that didn't actually exist in game
- Removes unused ``glance left/right`` options from the settings menu
- Restores missing camp icons that were not present on the map
- Ruin near the apple tree can now be used for triangulation

Miasmata Analysis/Modding Tools
-------------------------------
These are Python scripts I created to analyse and decode various game files.
They were hacked together while I was still in the process of understanding the
game's file formats and they are rather messy, probably broken and desperately
in need of refactoring and polish. They were first created simply to allow me
to better analyse the format of the game files, and the ability to repack some
of the files came later.

### rs5-extractor.py ###
This script can extract the contents of an RS5 archive into to a directory, or
pack files from a directory into a new RS5 archive. The local file headers are
left attached to the extracted files since they are used when repacking the RS5
archive.

It currently cannot manipulate files within an existing archive - the entire
archive has to be unpacked and repacked to edit any contained files.

### environment.py ###
This script can decode the game's environment database into human editable
JSON, and then re-encode the JSON back into the binary format used by the game.

### data.py ###
This script can decode & re-encode any database used by the game to/from JSON,
including the saved games.

### markers.py ###
This script lists and plots the location of items listed in the game's markers
file on the game's map. These include things like structures that can be used
to triangulate the player's position, creature spawn locations and so on.
Strings can be passed in on the command line to only plot certain types of
entities.

_Currently it requires certain files to have already been extracted into
specific locations - TODO is the ability to read them directly from main.rs5._

### inst_node.py ###
This script plots the location of items listed in the game's inst nodes on the
game's map. By default it will create one image showing the location of every
single item in the game, as well as individual images showing the locations of
each specific type of item.

**This script can take a long time to run!**

_Currently it requires certain files to have already been extracted into
specific locations - TODO is the ability to read them directly from main.rs5._

### plot_inst_nodes.py ###
This script reads the list of inst nodes that the game uses and plots their
bounding box on the game's map. This visually shows how the game breaks up it's
data structures that list all the items found in the game (where items also
includes grass, trees, rocks, etc).

_Currently it requires certain files to have already been extracted into
specific locations - TODO is the ability to read them directly from main.rs5._

### lookup_inst_nodes.py ###
This script takes a set of coordinates and plots the inst nodes that include
that location on the game's map.

_Currently it requires certain files to have already been extracted into
specific locations - TODO is the ability to read them directly from main.rs5._

### smap.py ###
This script can decode the various SMAP type files in the game and overlay them
on the game map.

_Currently it requires certain files to have already been extracted into
specific locations - TODO is the ability to read them directly from main.rs5._

### cterr_hmap.py ###
This script generates a heightmap of the game's map

_Currently it requires certain files to have already been extracted into
specific locations - TODO is the ability to read them directly from main.rs5._

### exposure_map.py ###
This script decodes the exposure map field from a saved game & overlays the
bored cartographer achievement smap to track down any missing pixels.

_Currently it requires certain files to have already been extracted into
specific locations - TODO is the ability to read them directly from main.rs5._

----------------------

DEPRECATED
----------------------
### BotanicalBadAssPatcher ###
This is a small C# program that automates the process of patching Miasmata.exe
to fix the broken Botanical Bad A\*\* achievement. This fix can now be performed by Miaspatch.

Refer to this thread for more info:
<http://steamcommunity.com/app/223510/discussions/0/648812305304655075/>