import PIL.Image, PIL.ImageTk, PIL.ImageOps

from tkinter import *
from tkinter import ttk
from tkinter import filedialog

class ImageFrame(ttk.Frame):
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
    """A frame that includes buttons to edit the ImageFrame that it is bound to.

    Attributes
    ----------
    rotate_button : ttk.Button
        A button that will rotate the image when pressed
    flip_button : ttk.Button
        A button that will flip the immage when pressed
    container : ImageFrame
        The object parent

    Methods
    -------
    rotate()
        Invoke the parent rotate method
    flip()
        Invoke the parent flip method
    """
    def __init__(self, container):
        """
        Parameters
        ----------
        container : ImageFrame
            The object parent; the ImageFrame whose image this object's buttons are bound to
        """
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
        """Invoke the parent rotate method."""
        self.container.rotate()

    def flip(self):
        """Invoke the parent flip method."""
        self.container.flip()

class ControlFrame(ttk.LabelFrame):
    """Frame with general settings for tool usage.
    
    Attributes
    ----------
    selected_value : IntVar()
        The key of the current ImageFrame being displayed
    save_button : ttk.Button
        The button which will save the file when pressed
    buttons : list
        A list of 'ttk.Radiobutton's which refer to the ImageFrame of the same key in frames
    frames : list
        A list of 'ImageFrame's that have been created by the user

    Methods
    -------
    change_frame()
        Display the current ImageFrom from frames with the key of the selected_value.
    add_new_image()
        Let user choose a new image to add to the application window.
        Appends the image to self.frames and raises the new frame. Then creates a ttk.Radiobutton.
    save_as_pdf()
        Prompt user to save the file.
    """
    def __init__(self, container):
        """
        Parameters
        ----------
        container : Tk
            The frame parent
        """
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
        """Display the current ImageFrom from frames with the key of the selected_value."""
        frame = self.frames[self.selected_value.get()]
        frame.tkraise()

    def add_new_image(self):
        """Let user choose a new image to add to the application window.
        Appends the image to self.frames and raises the new frame. Then creates a ttk.Radiobutton.
        """
        filename = filedialog.askopenfilename(
            filetypes = (("jpeg files","*.jpg"),("png files", "*.png"),("tiff files","*.tif")))
        new_frame = ImageFrame(self.container, filename)
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
        """Prompt user to save the file."""
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