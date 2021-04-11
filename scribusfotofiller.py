'''
Prerequisits: Filenames must be uniq
'''

import sys
import os
import glob
import json
import logging
import re

try:
    import scribus as sc
except ImportError:
    print('Unable to import the scribus module. This script will only run within')
    print('the Python interpreter embedded in Scribus. Try Script->Execute Script.')
    sys.exit(1)

IMAGEFRAMENAME='sffimage'
BASENAME = os.path.splitext(os.path.basename(sc.getDocName()))[0]
CONFIG_FILE_NAME = '{}.json'.format(BASENAME)

os.chdir(os.path.dirname(sc.getDocName()))

class ImageFrame:
    """
    Image Frame Details
    """
    name = None
    path = None
    width = 0
    height = 0
    offset_x = 0
    offset_y = 0
    scale_x = 0 
    scale_x = 0

    def __init__(self, *args):
        """
        Optional argument "name" 
        """
        if len(args) > 0:
            self.name = args[0]
            self.path = sc.getImageFile(self.name)
            self.width, self.height = sc.getSize(self.name)
            self.offset_x, self.offset_y = sc.getImageOffset(self.name)
            self.scale_x, self.scale_y = sc.getImageScale(self.name)


class SffImageFrame(ImageFrame):
    """
    SffImageFrame knows its index on page
    """
    index = -1

    def __init__(self, name):
        super().__init__(name)
        self.index = self.get_index_from_name(self.name)

    def get_index_from_name(self, name):
        m = re.match(r'.*sffimage_([0-9]+).*', name)
        if m:
            return int(m.groups()[0])
        else:
            return -1

    def is_empty(self):
        """
        assume a frame as empty if not image assigned or
        oder filename contains dummy 
        """
        logging.debug("Check if {} is empty".format(self.path))
        if not self.path:
            return True
        if "DUMMY" in os.path.basename(self.path).upper():
            logging.debug('Dummy image assigend, assume empty.')
            return True
        return False

    def replace(self, image_frame):
        """
        replace the image.
        If frame has the same size, keep scale and offset
        else  fall and center
        """
        self.path = image_frame.path
        sc.loadImage(self.path, self.name)
        if self.width == image_frame.width and self.height == image_frame.height:
            self.scale_x = image_frame.scale_x
            self.scale_y = image_frame.scale_y
            sc.scaleImage(self.scale_x, self.scale_y, self.name)
            self.offset_x = image_frame.offset_x
            self.offset_y = image_frame.offset_y
            sc.setImageOffset(self.scale_x, self.scale_y, self.name)
        else:
            x, y = scale_to_frame(self.name)
            center_image(self.name, x, y)


def get_config():
    if os.path.exists(CONFIG_FILE_NAME):
        with open(CONFIG_FILE_NAME) as sf:
            return json.load(sf)
    else:
        return {}

def write_config(config):
    with open(CONFIG_FILE_NAME, 'w') as sf:
        json.dump(config, sf, indent=2)

def prepare_config(config):
    image_dir = config.get('image_dir')
    if image_dir:
        if not os.path.exists(image_dir):
            image_dir = get_image_dir()
    else:
        image_dir = get_image_dir()

    config['image_dir'] = image_dir

    if not config.get('images'):
        config['images'] = []

    return config

def get_images(path, ignore_list=[]):
    """
    path: get images from. Should contain Images only
    ignore_list: list of filenames to exclude
    """
    image_list = list(filter(os.path.isfile, glob.glob(os.path.join(path, '*'))))
    image_list.sort(key=lambda x: os.path.getmtime(x))
    for image in image_list:
        logging.debug("Found {}".format(image))
        if os.path.basename(image) in ignore_list:
            image_list.remove(image)
            logging.debug("Remove {}".format(image))
    return list(set(image_list) - set(ignore_list))

def get_image_dir(start_dir=''):
    if len(start_dir) == 0:
        start_dir = os.path.dirname(sc.getDocName())
    image_dir = sc.fileDialog('Choose Folder with Images',defaultname=start_dir,isdir=True)
    return image_dir

def is_imageframe_empty(name):
    file = sc.getImageFile(name)
    if len(file) > 0:
        return False
    return True


def get_imageframes_on_page(page_number, empty_only=False, name_filter=None):
    """
    page_number:  if 0 use current page, otherwise the given page
    set emty_only to return empty frames only
    name_filter: return frame if name conatins filter string
    returns a list of the image objects on the current page
    get all the items on the page
    """

    current_page = sc.currentPage()
    if page_number > 0:
        if page_number <= sc.pageCount():
            sc.gotoPage(page_number)
        else:
            logging.warning('Page {} out of rage.'.format(page_number))
            return []

    item_list = sc.getPageItems()
    # refine it to a list of only image objects
    objs = []
    for item in item_list:
        if item[1] == 2: #type 2 == image
            add_image = True
            if empty_only:
                add_image = is_imageframe_empty(item[0]) and add_image
            if name_filter:
                if name_filter in item[0]:
                    add_image = True and add_image
                else:
                    add_image = False and add_image
            if add_image:
                objs.append(item[0])
    sc.gotoPage(current_page)
    return objs

def get_image_frames_detail(page_number, empty_only=False, name_filter=None):
    """
    page_number:  if 0 use current page, otherwise the given page
    returns dictionary of ImageFrames by name
    """
    frames = get_imageframes_on_page(page_number, empty_only, name_filter)
    images_details = {}
    for frame in frames:
        images_details[frame] = ImageFrame(frame)

def get_sff_image_frames_details(page_number, empty_only=False):
    """
    page_number: if 0 use current page, otherwise the given page
    empty_only: assume empty if empty or a dummy image assigned 
    returns dictionary of ImageFrames by index
    """
    frames = get_imageframes_on_page(page_number, empty_only=False, name_filter='sffimage_')
    images_details = {}
    for frame in frames:
        image_frame = SffImageFrame(frame)
        if image_frame.index >= 0:
            if not empty_only or image_frame.is_empty():
                images_details[image_frame.index] = image_frame
    return images_details

def center_image(name,image_x, image_y):
    """
    name: image naem
    image_x: original image width
    image_y: original image higth
    """

    scaleC, _ = sc.getImageScale(name)
    offX, offY = sc.getImageOffset(name)
    frame_x, frame_y = sc.getSize(name)    
    ix = image_x * scaleC
    iy = image_y * scaleC

    if ix != frame_x:
        offX = ( frame_x - ix ) / 2
    if iy != frame_y:
        offY = ( frame_y - iy ) / 2
    sc.setImageOffset(offX, offY, name)

def scale_to_frame(obj):
    """
    scales the image so that it fills the frame completely. 
    One dimension of the image (width/height) may overflow the frame, 
    but at least one dimension will fill the frame exactly
    return scaled image size (X, Y) 
    """
    try:
        sc.setScaleImageToFrame(True, False, obj)
        scale_x, scale_y = sc.getImageScale(obj)
        frame_x, frame_y = sc.getSize(obj)    
        sc.setScaleImageToFrame(False, False, obj)
        if scale_x > scale_y:
            scale = scale_x
        elif scale_y > scale_x:
            scale = scale_y
        sc.setImageScale(scale, scale, obj)
        image_x = int(round(frame_x / scale_x))
        image_y = int(round(frame_y / scale_y))
        return (image_x, image_y)
    except:
        logging.info("scaling for image {} failed".format(obj))

def store_images(image_list, move=True):
    """
    store images in a subfolder "fotos" relative to the ddocument.
    image_list: list of path to images
    move: default move files, else copy

    returns: list of path to stored images
    """
    store_dir = os.path.join(os.path.dirname(sc.getDocName()), '{}.fotos'.format(BASENAME))
    if not os.path.exists(store_dir):
        os.mkdir(store_dir)
    stored_images = []
    for image in image_list:
        tartget = os.path.join(store_dir, os.path.basename(image))
        if move:
            os.rename(
                image,
                tartget
            )
        else:
            import shutil
            shutil.copyfile(
                image,
                tartget
            )
        stored_images.append(tartget)
    return stored_images


def fill_frames(image_frames, image_list):

    for frame, image in zip(image_frames, image_list):
        logging.debug('Put {} in {}.'.format(image, frame))
        sc.loadImage(image, frame)
        x, y = scale_to_frame(frame)
        center_image(frame, x, y)

def main():
    config = prepare_config(get_config())
    new_images = get_images(config['image_dir'], config['images'])
    image_frames = get_sff_image_frames_details(0, empty_only=True)

    if len(image_frames) > 0:
        if len(new_images) < len(image_frames):
            max_imports = len(new_images)
        else:
            max_imports = len(image_frames)

        import_text = [
            'Found {} empty image frames on the current page.'.format(len(image_frames)),
            'Following Images will be imported:'
        ]
        import_text.extend(new_images[:max_imports])
        import_text.extend( [
            '',
            'Click "Retry" to get further configuation options.'
        ] )

        answer = sc.messageBox('Image import', '\n'.join(import_text), 
            button1=sc.BUTTON_OK|sc.BUTTON_DEFAULT,
            button2=sc.BUTTON_RETRY,
            button3=sc.BUTTON_ABORT|sc.BUTTON_ESCAPE
        )

        if answer == sc.BUTTON_OK:
            stored_images = store_images(new_images[:max_imports])
            image_frame_names = []
            for idx in image_frames:
                image_frame_names.append(image_frames[idx].name)
                logging.debug("image frame: {}".format(image_frames[idx].name))
            fill_frames(image_frame_names, stored_images)
            config['images'].extend(stored_images)
            write_config(config)
        elif answer == sc.BUTTON_ABORT:
            sys.exit(0)
        elif answer == sc.Retry:
            print("Sorry not implemented jet :-(")
            sys.exit(0)

    else:
        sc.messageBox(
            'Script failed', 
            "Current page, doesn't contain empty image frames.", 
            sc.ICON_CRITICAL
        )
        sys.exit(1)

    sc.docChanged(1)
    sc.setRedraw(True)

if __name__ == '__main__':
    logging.basicConfig(filename='{}.log'.format(BASENAME), level=logging.DEBUG)
    main()
