#!/usr/bin/env python
"""
If two image frames are selected both images will be swapped.
Images get scaled if both frames doesn't have the same size.
"""

import logging
import scribusfotofiller as sff
import scribus as sc
import sys

def error_msg(text):
    sc.messageBox(
        'Swap images', 
        f"Excact two image frames must be selected.\n{text}", 
        sc.ICON_CRITICAL
    )
    sys.exit(1)



def main():
    if sc.selectionCount() == 2:
        images = ( sc.getSelectedObject(0), sc.getSelectedObject(1) )
        for image in images:
            if sc.getObjectType(image) != "ImageFrame":
                logging.debug(f"Image type {sc.getObjectType(image)}, but 'ImageFrame' expected")
                error_msg(f'{image} not an image frame. But type {sc.getObjectType(image)}')
        image_files = (sc.getImageFile(images[0]), sc.getImageFile(images[1]))
        # keep Scale and Offset, before reset by image load
        image_0_offset = sc.getImageOffset(images[0])
        image_0_scale  = sc.getImageScale(images[0])
        image_1_offset = sc.getImageOffset(images[1])
        image_1_scale  = sc.getImageScale(images[1])
        sc.loadImage(image_files[1], images[0]) 
        sc.loadImage(image_files[0], images[1]) 
        if sc.getSize(images[0]) == sc.getSize(images[1]):
            # Frames have the same size swap scale and offset
            logging.debug(f"Frames have the same size {sc.getSize(images[0])}, swap offset and scale")
            logging.debug(f"Image 0: {images[0]}, Image 1: {images[1]}")
            logging.debug(f"Image properties: offset {sc.getImageOffset(images[0])}, scale {image_0_scale}")

            sc.setImageOffset(*image_1_offset, images[0])
            sc.setImageScale(*image_1_scale, images[0])
            sc.setImageOffset(*image_0_offset, images[1])
            sc.setImageScale(*image_0_scale, images[1])
        else:
            # scale and center
            logging.debug("Different size scale and center, both.")
            for name in images:
                x, y = sff.scale_to_frame(name)
                sff.center_image(name, x, y)


    else:
        logging.debug(f"{sc.selectionCount()} frames selected.")
        error_msg(f'{sc.selectionCount()} frames selected')

if __name__ == '__main__':
    logging.basicConfig(filename='{}.log'.format(sff.BASENAME), level=logging.DEBUG)
    main()
    sc.docChanged(1)
    sc.setRedraw(True)
