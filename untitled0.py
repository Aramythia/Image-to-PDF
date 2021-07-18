import PIL.Image, PIL.ImageTk, PIL.ImageOps

from tkinter import *
from tkinter import ttk
from tkinter import filedialog

class ConverterFrame(ttk.Frame):
    """A frame that holds an image and its options.

    Attributes
    ----------
    original_image : PIL.Image.Image
        The original image being opened. This one should be edited by all methods.
        All changes to original_image must be applied to resized_image and display_image
    resized_image : PIL.Image.Image
        A resized form of the original image to be converted into a tkinter-friendly format and
        be displayed at a reasonable size.
    display_image : PIL.ImageTk.PhotoImage
        The tkinter-friendly image that will be displayed in the GUI
    image_label : ttk.Label
        A label that contains the display_image in the GUI

    Methods
    -------
    apply_image_edit()
        Apply all changes made to original_image to resized_image and display_image.
    resize_original_image()
        Set the resized_image to be a smaller version of the original image.
        The maximum image size is 800x600 or 800x600. 
        If the image already meets these constraints, then nothing will be changed.
    rotate()
        Rotate the image 90 degrees counterclockwise.
    flip()
        Flip the image over the x-axis.
    """
    def __init__(self, container, image):
        """
        Parameters
        ----------
        container : Tk
            The frame parent
        image : str
            A path to the image being used in this frame
        """
        super().__init__(container)

        self.original_image = PIL.Image.open(image)
        self.resized_image = None
        self.resize_original_image() # This sets resized_image
        self.display_image = PIL.ImageTk.PhotoImage(self.resized_image)

        # field options
        self.options = {'padx': 5, 'pady': 0}

        # image viewer
        self.image_label = ttk.Label(self, image=self.display_image)
        self.image_label.grid(column=0, row=0, sticky='w',  **self.options)

        image_options = ttk.LabelFrame(self)
        image_options['text'] = "Image Options"

        # # rotate and flip buttons
        # self.rotate_button = ttk.Button(self, text='Rotate')
        # self.rotate_button.grid(column=1, row=0, sticky='w', **self.options)
        # self.rotate_button.configure(command=self.rotate)

        # self.flip_button = ttk.Button(self, text='Flip')
        # self.flip_button.grid(column=1, row=1, sticky='w', **self.options)
        # self.flip_button.configure(command=self.flip)

        self.image_options = ImageOptions(self)
        self.image_options.grid(column=0, row=1, sticky='w', **self.options)

        # add padding to the frame and show it
        self.grid(column=0, row=0, padx=5, pady=5, sticky="nsew")

    def apply_image_edit(self):
        """Apply all changes made to original_image to resized_image and display_image."""
        self.resize_original_image()
        self.display_image = PIL.ImageTk.PhotoImage(self.resized_image)

        self.image_label = ttk.Label(self, image=self.display_image)
        self.image_label.grid(column=0, row=0, sticky='w',  **self.options)

    def resize_original_image(self):
        """Set the resized_image to be a smaller version of the original image.
        The maximum image size is 800x600 or 600x800. 
        If the image already meets these constraints, then nothing will be changed.
        """
        length = self.original_image.size[0]
        height = self.original_image.size[1]

        aspect_ratio = length / height
        
        if length > height: #Then it is a landscape --> limit to 800x600
            if length < 800 and height < 600: # then nothing needs to be done
                self.resized_image = self.original_image
                return 
            
            # Compare the percent distance from the maximum from both coordinates
            length_distance = length / 800
            height_distance = height / 600
            
        else: #It is a portrait --> limit to 600x800
            if length < 800 and height < 600:
                self.resized_image = self.original_image
                return
            
            length_distance = length / 800
            height_distance = height / 600
            
        # Whichever side deviates most from its maximum size will be reduced to that size
        if length_distance > height_distance:
            length_resize = int(length / length_distance)
            # The other will be reduced by the amount given by the aspect_ratio
            height_resize = int(length_resize / aspect_ratio)
        else:
            height_resize = int(height / height_distance)
            length_resize = int(height_resize * aspect_ratio)

        self.resized_image = self.original_image.resize((length_resize,height_resize))

    def rotate(self):
        """Rotate the image 90 degrees counterclockwise."""
        self.original_image = self.original_image.rotate(90, expand=True)
        self.apply_image_edit()

    def flip(self):
        """Flip the image over the x-axis."""
        self.original_image = PIL.ImageOps.mirror(self.original_image)
        self.apply_image_edit()

class ImageOptions(ttk.LabelFrame):
    def __init__(self, container):

        super().__init__(container)
        self.container = container
        self['text'] = 'Image Options'

        options = {'padx': 5, 'pady': 0}

        self.rotate_button = ttk.Button(self, text='Rotate')
        self.rotate_button.grid(column=0, row=0, sticky='w', **options)
        self.rotate_button.configure(command=self.rotate)

        self.flip_button = ttk.Button(self, text='Flip')
        self.flip_button.grid(column=1, row=0, sticky='w', **options)
        self.flip_button.configure(command=self.flip)

        self.grid(column=0, row=1, padx=5, pady=5, sticky='ew')

    def rotate(self):
        self.container.rotate()

    def flip(self):
        self.container.flip()

class ControlFrame(ttk.LabelFrame):
    def __init__(self, container):

        super().__init__(container)
        self.container = container
        self['text'] = 'Options'

        # radio buttons
        self.selected_value = IntVar()

        ttk.Button(self, text="Add Image", command=self.add_new_image).grid(column=0, row=1, sticky=W)

        self.save_button = ttk.Button(self, 
                                      text="Save as PDF", 
                                      command=self.save_as_pdf,
                                      state=DISABLED).grid(column=1, row=1, sticky=W)

        # ttk.Label(self, text="Enter file name:").grid(column=0, row=2, sticky=W)

        # self.name = StringVar()
        # ttk.Entry(self, width=15, textvariable=self.name).grid(column=1, row=2, sticky=W)

        self.grid(column=0, row=1, padx=5, pady=5, sticky='ew')

        # initialize frames
        self.buttons = []
        self.frames = []

    def change_frame(self):
        frame = self.frames[self.selected_value.get()]
        frame.tkraise()

    def add_new_image(self):
        """Let user choose a new image to add to the application window.
        Appends the image to self.frames and raises the new frame. Then creates a radio button.
        """
        filename = filedialog.askopenfilename(
            filetypes = (("jpeg files","*.jpg"),("png files", "*.png"),("tiff files","*.tif")))
        new_frame = ConverterFrame(self.container, filename)
        self.frames.append(new_frame)
        
        # Create radio button
        new_button = ttk.Radiobutton(
            self,
            text=f"Image {len(self.buttons)}",
            value = len(self.buttons),
            variable = self.selected_value,
            command=self.change_frame).grid(column=len(self.buttons), row=0, padx=5, pady=5)
        self.buttons.append(new_button)

        # Finally update window
        self.change_frame()

        self.save_button = ttk.Button(self, 
                                      text="Save as PDF", 
                                      command=self.save_as_pdf).grid(column=1, row=1, sticky=W)

    def save_as_pdf(self):
        directory = filedialog.asksaveasfilename(confirmoverwrite=True, 
                                                 filetypes=[("pdf files", "*.pdf")], 
                                                 defaultextension=".pdf")                                   

        if directory == '':
            return

        images = [frame.original_image for frame in self.frames]
        images[0].save(directory, format="pdf", save_all=True, append_images=images[1:])

root = Tk()
root.title("Image to PDF")

ControlFrame(root)

root.mainloop()