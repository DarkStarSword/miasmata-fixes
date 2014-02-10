#!/usr/bin/env python

from gimpfu import *

end_a = '''
The wind begins to carry you - towards that infinite line between
sea and sky. Your conscience is undivided now. You peer over the
edge of the boat to find your reflection on the surface of the water.
You see the man you hoped to see and you smile.
'''

# font = 'Times New Roman,'
# font = 'Gentium' # Closer
# font = 'Nimbus Roman No9 L' # Closer, h still not tall enough
# font = 'STIXGeneral' # No
# font = 'URW Palladio L Medium' # Still not quite right, shape is off
# font = 'Liberation Serif'
# font = 'Georgia' # Close
# font = 'Gentium Book Basic' # Close
# font = 'Gentium Basic'
# font = 'Droid Serif'
# font = 'DejaVu Serif'
# font = 'cmr10' # <-- Pretty close, letters aren't quite well enough defined
# font = 'Century Schoolbook L Medium'  # close
# font = 'Bitstream Charter'
# font_size = 40.0
# line_spacing = 27.0
# line_spacing = 31.0

font = 'perpetua' # Closest yet for shape. Letters not quite thick enough
font_size = 44.0
line_spacing = 20.0

def render_end_slide():
    width = height = 1024

    image = gimp.Image(width, height, RGB)
    background = gimp.Layer(image, 'Background', width, height, RGB_IMAGE, 100, NORMAL_MODE)
    image.add_layer(background)

    try:
        gimp.Display(image)
    except:
        pass

    gimp.set_background(0, 0, 0)
    background.fill(BACKGROUND_FILL)

    gimp.set_foreground(255, 255, 255)
    text = pdb.gimp_text_fontname(image, None, 0, 0, end_a, 0, True, font_size, PIXELS, font)
    text.name = 'Text'
    pdb.gimp_text_layer_set_line_spacing(text, line_spacing)
    pdb.gimp_text_layer_set_hint_style(text, TEXT_HINT_STYLE_NONE)

    # TODO: When GIMP scripting supports setting text markup, add e.g.
    # <span size=\"61440\">...</span> around first letter.

    pdb.gimp_context_set_interpolation(INTERPOLATION_LANCZOS)
    text.scale(width - 2*170, text.height)
    text.translate(170, (image.height - text.height) / 2)

    pdb.plug_in_gauss_rle2(image, text, 1.0, 1.0)

    # image.active_layer = background

    pdb.gimp_xcf_save(0, image, image.active_layer, 'output.xcf', 'output.xcf')
    image.clean_all()

    image2 = pdb.gimp_image_duplicate(image)
    image2.flatten()

    pdb.file_png_save2(image2, image2.active_layer, 'output.png', 'output.png',
            0, # interlace
            9, # compression
            0, # save background colour
            0, # save gamma
            0, # save layer offset
            1, # save pHYs (resolution?)
            1, # save creation time
            1, # save comment
            1, # preserve colour of transparent pixels
    )

    pdb.file_dds_save(
            image2,
            image2.layers[0],
            'output.dds', # filename
            'output.dds', # raw_filename
            1, # 1 = DXT1 (no alpha), 3 = DXT5 (alpha)
            0, # 1 = generate mipmaps
            0, # 0 = save current layer
            0, # format
            -1, # transparent-index
            0, # DXT compression color-type (Tweaking may help in some cases)
            0, # Dither
            0, # mipmap-filter - maybe try tweaking this for in-game objects
            0, # gamma-correct
            2.2, # gamma
    )

register(
    "miasmata_end_slide",
    "Generate an image for Miasmata's end sequence",
    "Generate an image for Miasmata's end sequence",
    "Ian Munsie",
    "Ian Munsie",
    "2014",
    "<Toolbox>/_Miasmata/_End",
    None,
    [],
    [],
    render_end_slide,
)

main()
