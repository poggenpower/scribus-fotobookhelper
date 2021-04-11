# -*- coding: utf-8 -*-
"""
Scales and center all selced images.
If no image selected all "sffimage"s get processes 
"""
import logging
import scribusfotofiller as sff
import scribus as sc

def main():
    nbrSelected = sc.selectionCount()

    objList = []
    if nbrSelected > 0:
        for i in range(nbrSelected):
            objList.append(sc.getSelectedObject(i))
    else:
        # nothing selected get images from current page
        objList = sff.get_imageframes_on_page(0,name_filter=sff.IMAGEFRAMENAME)

    for name in objList:
        x, y = sff.scale_to_frame(name)
        sff.center_image(name, x, y)

if __name__ == '__main__':
    logging.basicConfig(filename='{}.log'.format(sff.BASENAME), level=logging.DEBUG)
    main()
    sc.docChanged(1)
    sc.setRedraw(True)

