Miasmata Fixes
==============

BotanicalBadAssPatcher
----------------------
This is a small C# program that automates the process of patching Miasmata.exe
to fix the broken Botanical Bad A\*\* achievement.

Refer to this thread for more info:
<http://steamcommunity.com/app/223510/discussions/0/648812305304655075/>

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
  not added to the journal (a bug fixed by the community patch), it also gives
  the option to reset the note so it can be picked up again from the camp where
  it was originally found.

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
