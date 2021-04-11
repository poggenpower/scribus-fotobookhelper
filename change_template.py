# -*- coding: utf-8 -*-
"""
Applyes Layout from a other page to the current page.
sffimage Image frames are migrated. Order of frames should be kept.
Image frame names must contain "sffimage_#" where # is the number
of the image on the page.
"""
import sys
import logging
import scribusfotofiller as sff
import scribus as sc

def main():
    cur_page = sc.currentPage()
    logging.debug('Current page/page to replace: {}'.format(cur_page))
    cur_images = sff.get_sff_image_frames_details(cur_page)
    logging.debug('{} Image frames found on source page'.format(len(cur_images)))
    template_page = sc.valueDialog(
        'Choose Template for current page',
        'Warning you will loose all customizations. \nGive page number of the template: '
    )
    try:
        # check if template exist
        template_page = int(template_page)
    except TypeError:
        sc.messageBox(
            'Template invalid', 
            "You must provide a valid number.", 
            sc.ICON_CRITICAL
        )
    try:
        logging.debug("Page {} selected as template.".format(template_page))
        sc.getPageNSize(template_page)
        logging.debug("Template page exists.")
        template_images = sff.get_sff_image_frames_details(template_page)
        if len(template_images) < 1:
            logging.debug('No image frames in template found.')
            raise Exception('No Images on Template')
    except Exception as e:
        sc.messageBox(
            'Template invalid', 
            "Either page doesn't exists nor has SFF image frames.", 
            sc.ICON_CRITICAL
        )
        raise e
        sys.exit(1)

    logging.debug("start replacing page {}.".format(sc.currentPage()))
    sc.gotoPage(cur_page)
    sc.newPage(cur_page, sc.getMasterPage(cur_page))
    sc.gotoPage(cur_page - 1)
    sc.importPage(sc.getDocName(), ( template_page,  ), 0 )
    logging.debug("Replaced with template from page {}.".format(template_page))
    template_images = sff.get_sff_image_frames_details(cur_page)
    logging.debug('{} images frames found on new page'.format(len(template_images)))
    for image_idx in cur_images:
        if template_images.get(image_idx):
            logging.debug('Replacing {} with {}'.format(template_images[image_idx].name, cur_images[image_idx].path))
            template_images[image_idx].replace(cur_images[image_idx])
        else:
            logging.warning('not enough image frames')
    sc.deletePage(cur_page + 1)


if __name__ == '__main__':
    logging.basicConfig(filename='{}.log'.format(sff.BASENAME), level=logging.DEBUG)
    main()
    sc.docChanged(1)
    sc.setRedraw(True)
