# Scribus Photo Book Workflow

Followings scrips helps to create a Photo Book in Scribus(scribus.org).

they help 
- Using existing pages as template
- to scale images to a useful size
- apply another template to a page
- swap images of two image frames

## Workflow

This is not a Photo Book Generator, that creates automatically a book out of a set up pictures. We found that such generated books will never will look good enough.

The workflow helps to create the book page by page. Template pages help to keeps a consistent layout. The scripts help to handle some image operations. But it relies also on scribus build in functions and tools.

Using a template like (wir-machen-druck-fotobuch.sla). 
It starts with a set of template pages. One for each page side. 
For most of the functionality thee are no special requirements for these template pages, but to allow applying another template to an already created page, image frame names must contain a string `sffimage_#` where # is a number counting up from 1. 

### Main workflow
1. choose a page from the templates and create a copy at the end of the document.
'Page > Copy ... > OK'
2. Scroll down to the new page 
3. Open the Picture Browser 'Extras > Picture Browser ...'
4. Drag and drop the images to the image frames. (Found using the Picture Browser the easiest and most intuitive way, but you can use any other way in scribus to load images into the frames.)
5. Scribus build in scaling is a little bit suboptimal for such a photo book layout. Therefor the script `scale.py` resizes the image that is fully fills the frame and is centered. (If frame(s) are selected only this one get resized, otherwise all image frames on the page get scaled)
6. make manual changes to the page as needed.

### Apply a new template
In some situation you may find the template you have chosen in step 1 above is not the best anymore. Or you need a template with more frames to add another image. 
1. Choose the new template and keep the page number in mind.
2. Navigate to the page you want to change.
3. run `change_template.py`, it will ask for the page number of the new template you have chosen in 1. 

WARNING: If the new template has less image frames than the source, overlapping images will be lost.

Image frames between old and new will be matched by the name part `sffimage_#`. If size between source and destination frame doesn't have the same size, the image will be scaled and centered to fully fill the frame.

### swap two images
In case you want to reorder the images you can use `swap.py` to swap the images from two frames.
1. select two image frames
2. run `swap.py`

If size between source and destination frame doesn't have the same size, the image will be scaled and centered to fully fill the frame.


## Requirements and Tech Details

### Requirements
- Tested with scribus 1.5.6.1 on mac os with python3
- Scripts should work on other OSes, feedback is welcome
- Older versions may not work, because these scripts requires python3
- beside wiki.scribus.org, http://write.flossmanuals.net/scribus/scripter-and-scripts/ is a good description to learn how to start scripts in scribus

### Tech Details
- `scribusfotofiller.py` is a base library from all the other scripts (it has some additional logic to autofill pages, but this has shown not to be very useful)
- There are no custom dialogues (e.g. with TKInter), because they doesn't work with MacOS.
- Check the log with the same name of your current sla file.


## ToDo / Wishlist
- Tooling to create/prepare templates 
  - automatic frame naming
  - automatic template mirroring to create left from right page and the other way round.
  - better handling of overlapping images, while template change
- making workflow independent from left/right positioning of a page
- Filling the "Überschrift" automatically by image meta data
  - time stamps
  - tags
- Create Table of content based on image meta data like tags and timestamps 