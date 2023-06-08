from tkinter import *
from tkinter import colorchooser, messagebox, ttk, filedialog
from PIL import ImageGrab


class ArtStudio(Tk):
    """An art studio application for creating drawings.

    It provide functionality for drawing using various tools and 
    geometric shapes, selecting colors, changing stroke size, 
    and saving drawings.

    Attributes:
        record_draw (list): A list to store the lines drawn in the current drawing.
        last_drawing: A list representing the last drawing (default is None).
        drawing_history (list): A list to store the history of completed drawings.
        current_deleted_lines (list): A list to store the lines deleted in the current action.
        deleted_history (list): A list to store the history of deleted drawings.
        previous_point (list): The coordinates of the previous point during drawing.
        current_point (list): The coordinates of the current point during drawing.
        start_x: An integer representing the starting x-coordinate (default is None).
        start_y: An integer representing the starting y-coordinate (default is None).
        value: The value representing the type of geometric shape being drawn (default is None).
        figure: The reference to the current geometric shape being drawn (default is None).
        saved (bool): A flag indicating whether the drawing has been saved already. 
        stroke_size (IntVar): The variable to store the stroke size.
        stroke_color (StringVar): The variable to store the stroke color.
    """

    def __init__(self):
        """Initialize the ArtStudio application.

        Set up the main window properties, initialize various variables,
        and create the interface elements.
        """
        super().__init__()

        # Main window properties
        self.title("ArtStudio")
        self.geometry("1070x700")
        self.resizable(False, False)

        self.record_draw = []
        self.last_drawing = None
        self.drawing_history = []
        self.current_deleted_lines = []
        self.deleted_history = []

        # Variables for making a drawing
        self.previous_point = [0, 0]
        self.current_point = [0, 0]

        # Variables associated with the geometric_draw methods
        self.start_x = None
        self.start_y = None
        self.value = None
        self.figure = None

        # Save flag
        self.saved = False

        # Variables for controlling the drawing stroke
        self.stroke_size = IntVar()
        self.stroke_size.set(3)
        self.stroke_color = StringVar()
        self.stroke_color.set('black')

        self.create_interface()

        self.create_dropdown_menu()

        self.create_drawing_bindings()

    def create_palette(self):
        """Create the color palette.

        Generate a color palette by creating rectangles with different 
        pre-defined colors. 
        """
        # Colors for the palette
        colors = ['red', 'blue', 'green', 'yellow', 'pink',
                  'purple', 'orange', 'brown', 'gray', 'silver']

        # Initial palette coordinates
        x1, y1, x2, y2 = 0, 0, 30, 30

        for color in colors:

            r = self.canvas_colors.create_rectangle(
                x1, y1, x2, y2, fill=color, outline='black')
            self.canvas_colors.tag_bind(
                r,
                '<Button-1>',
                lambda event, color_remembered=color: self.select_palette_color(event, color_remembered))
            x1 += 30
            x2 += 30
            y2 += 30

    def create_interface(self):
        """Create the user interface.

        Create the GUI elements, including the sections for tools,
        size, and color box, as well as the canvas.
        """
        # Head frame: tools
        self.head_frame = Frame(self, height=100, width=1100, pady=1)
        self.head_frame.grid(row=0, column=0, sticky=NW)

        # tools frame
        self.toolsFrame = Frame(self.head_frame, height=100,
                                width=100, relief=GROOVE,
                                highlightthickness=1, padx=5)
        self.toolsFrame.grid(row=0, column=0)

        self.pencil_button = ttk.Button(self.toolsFrame,
                                        text='Pencil', width=10, cursor="hand2",
                                        command=self.use_pencil)
        self.pencil_button.grid(row=0, column=0)

        self.eraser_button = ttk.Button(self.toolsFrame, text='Eraser',
                                        width=10, cursor="hand2", command=self.use_eraser)
        self.eraser_button.grid(row=1, column=0)

        self.eraser_button = ttk.Button(self.toolsFrame, text='Clear All',
                                        width=10, cursor="hand2", command=self.clean_all)
        self.eraser_button.grid(row=0, column=1)

        self.undo_button = ttk.Button(self.toolsFrame, text=u"\u2190",
                                      width=10, cursor="hand2", command=self.undo)
        self.undo_button.grid(row=1, column=1)

        self.redo_button = ttk.Button(self.toolsFrame, text=u"\u2192",
                                      width=10, cursor="hand2", command=self.redo)
        self.redo_button.grid(row=1, column=2)

        self.rectangle_button = ttk.Button(self.toolsFrame,
                                           text="Rectangle",
                                           width=10, cursor="hand2",
                                           command=lambda: self.geometric_draw(1))
        self.rectangle_button.grid(row=0, column=2)

        self.circle_button = ttk.Button(self.toolsFrame, text="Circle",
                                        width=10, cursor="hand2",
                                        command=lambda: self.geometric_draw(2))
        self.circle_button.grid(row=1, column=3)
        self.line_button = ttk.Button(self.toolsFrame, text="Line",
                                      width=10, cursor="hand2",
                                      command=lambda: self.geometric_draw(3))
        self.line_button.grid(row=0, column=3)

        self.tools_label1 = Label(
            self.toolsFrame, text='Tools', width=10)
        self.tools_label1.grid(
            row=2, column=0, columnspan=3, pady=(5, 0), padx=(130, 0))

        # Size frame
        self.sizeFrame = Frame(self.head_frame, height=100,
                               width=100, relief=GROOVE,
                               highlightthickness=1,
                               padx=5)
        self.sizeFrame.grid(row=0, column=1)

        self.default_button = ttk.Button(self.sizeFrame, text='Default',
                                         width=10, cursor="hand2", command=self.default)
        self.default_button.grid(row=0, column=0)

        # Drawing tool sizes
        self.options = [1, 2, 3, 4, 5, 10, 20, 30]

        self.sizes_list = ttk.Combobox(master=self.sizeFrame,
                                       textvariable=self.stroke_size,
                                       values=self.options)
        self.sizes_list.grid(row=1, column=0)

        self.size_label = Label(self.sizeFrame, text='Size', width=10)
        self.size_label.grid(row=2, column=0, pady=(5, 0))

        # ColorBox frame
        self.color_box_frame = Frame(self.head_frame,
                                     height=100, width=100,
                                     relief=GROOVE, highlightthickness=1, padx=5)
        self.color_box_frame.grid(row=0, column=2)

        self.color_box_button = ttk.Button(self.color_box_frame,
                                           text='Select Color', width=10, cursor="hand2",
                                           command=self.select_color)
        self.color_box_button.grid(row=0, column=0)

        self.canvas_bg = ttk.Button(self.color_box_frame,
                                    text='Canvas Color', width=10, cursor="hand2",
                                    command=self.select_canvas_color)
        self.canvas_bg.grid(row=0, column=1)

        self.canvas_colors = Canvas(self.color_box_frame,
                                    bg='black', height=25, width=298, cursor="crosshair")
        self.canvas_colors.grid(column=0, row=1, columnspan=2)

        self.color_label = Label(self.color_box_frame, text='Color', width=10)
        self.color_label.grid(row=2, column=0, columnspan=2, pady=(3, 0))

        # Create the colors palette inside the self.canvas_colors
        self.create_palette()

        # Frame 2: Create the canvas
        self.canvas_frame = Frame(self, height=500, width=1100, bg='yellow')
        self.canvas_frame.grid(row=1, column=0)

        self.canvas = Canvas(self.canvas_frame, height=600,
                             width=1064, bg='white')
        self.canvas.grid(row=0, column=0)

        self.canvas['cursor'] = 'spraycan'

    def create_dropdown_menu(self):
        """Create the dropdown menu.

        Add options for saving the drawing and exiting the application.
        Additionally, handle the window closing event so the user can save the drawing.
        """
        self.my_menu = Menu(self)
        self.config(menu=self.my_menu)

        self.file_menu = Menu(self.my_menu)

        self.my_menu.add_cascade(label='File', menu=self.file_menu)

        self.file_menu.add_command(label='Save', command=self.save_drawing)

        self.file_menu.add_separator()

        self.file_menu.add_command(label='Exit', command=self.save_on_closing)

        # Ask if the user wants to save the drawing before closing window
        self.protocol('WM_DELETE_WINDOW', self.save_on_closing)

    def create_drawing_bindings(self):
        """Enable drawing functionality using the mouse."""
        self.canvas.bind('<ButtonPress-1>', self.start)  # event.type = 4
        self.canvas.bind('<B1-Motion>', self.paint)  # event.type = 6
        self.canvas.bind('<ButtonRelease-1>',
                         self.button_release)  # event.type = 5

    def start(self, event):
        """Initialize the starting point of the drawing.

        Args:
            event (tkinter.Event): The mouse event containing the x and y coordinates.
        """
        x = event.x
        y = event.y
        self.previous_point = [x, y]

    def paint(self, event):
        """Handle the mouse motion event to perform drawing.

        Args:
            event (tkinter.Event): The mouse event containing the x and y coordinates.
        """
        self.current_point = [event.x, event.y]

        current = self.canvas.create_polygon(self.previous_point[0],
                                             self.previous_point[1],
                                             self.current_point[0],
                                             self.current_point[1],
                                             fill=self.stroke_color.get(),
                                             outline=self.stroke_color.get(),
                                             width=self.stroke_size.get())
        # Storing every line in a variable
        self.record_draw.append(current)

        self.previous_point = self.current_point

    def button_release(self, event):
        """Handle the release of the mouse button.

        Args:
            event (tkinter.Event): The mouse event containing the x and y coordinates.
        """
        # Storing the current drawing
        self.last_drawing = self.record_draw

        # This keeps track of the drawings' history
        self.drawing_history.append(self.last_drawing)
        self.record_draw = []

        self.saved = False

    def use_pencil(self):
        """Set the drawing tool to pencil."""
        self.stroke_color.set("black")
        self.stroke_size.set(1)
        self.canvas['cursor'] = "pencil"

    def use_eraser(self):
        """Set the drawing too to eraser."""
        self.stroke_color.set(self.canvas['bg'])
        self.canvas['cursor'] = DOTBOX

    def undo(self):
        """Undo the last drawing action."""
        if len(self.drawing_history):  # Check if drawings exist
            last_action = self.drawing_history.pop()

            # Retrieve the coordinates of the lines to be deleted
            [self.current_deleted_lines.append(self.canvas.coords(line) +
                                               [self.canvas.itemcget(line, 'fill'),
                                                self.canvas.itemcget(
                                                    line, 'width'),
                                                self.canvas.itemcget(line, 'outline')])
                for line in last_action]

            self.deleted_history.append(
                self.current_deleted_lines)  # Save those coords

            # Erase the last action
            self.canvas.delete(*last_action)
            self.current_deleted_lines = []

        self.saved = False

    def redo(self):
        """Redo the last undone drawing action."""
        if len(self.deleted_history):  # Check if there are deleted drawings
            last_deleted_drawing = self.deleted_history.pop()
            for line in last_deleted_drawing:  # Recreate the lines using the saved coords

                restored_line = self.canvas.create_polygon(line[0], line[1], line[2], line[3],
                                                           fill=line[4],
                                                           outline=line[6],
                                                           width=line[5])

                self.record_draw.append(restored_line)  # Store line
            # Add new drawing to user's history
            self.drawing_history.append(self.record_draw)

            self.record_draw = []  # Clear the temporary var

        self.saved = False

    def geometric_draw(self, value: int):
        """Enable drawing of geometric figures on the canvas.

        Args:
            value: An integer representing the type of geometric figure to be drawn.
        """
        self.canvas.bind("<ButtonPress-1>",
                         self.create_geometry_on_button_press)
        self.canvas.bind("<B1-Motion>", self.draw_geometry_on_motion)
        self.canvas.bind("<ButtonRelease-1>",
                         self.finish_geometry_on_button_release)

        self.canvas['cursor'] = 'tcross'

        # Determine what type of geometric figure is being drawn
        self.value = value

    def create_geometry_on_button_press(self, event):
        """Set the starting point to create a geometric figure on the canvas on button press.

        Args:
            event (tkinter.Event): The mouse event containing the x and y coordinates.
        """
        # Save mouse drag start position
        self.start_x = event.x
        self.start_y = event.y

        # Check which button was pressed and create the figure
        if self.value == 1:  # Rectangle
            self.figure = self.canvas.create_rectangle(
                -100, -100, -100, -100, outline=self.stroke_color.get(),
                width=self.stroke_size.get())
        elif self.value == 2:  # Oval/circle
            self.figure = self.canvas.create_oval(
                -100, -100, -100, -100, outline=self.stroke_color.get(),
                width=self.stroke_size.get())
        elif self.value == 3:  # Line
            self.figure = self.canvas.create_polygon(
                -100, -100, -100, -100, outline=self.stroke_color.get(),
                width=self.stroke_size.get())

        # Save the figure
        self.record_draw.append(self.figure)

    def draw_geometry_on_motion(self, event):
        """Adjusts the size and shape of the geometric figure as the mouse is being dragged.

        Args:
            event (tkinter.Event): The mouse event containing the x and y coordinates.
        """
        x, y = event.x, event.y

        # Expand the figure as the mouse is being dragged
        self.canvas.coords(self.figure, self.start_x,
                           self.start_y, x, y)

    def finish_geometry_on_button_release(self, event):
        """Finish the creation of the geometric figure on button release.

        Args:
            event (tkinter.Event): The mouse event containing the x and y coordinates.
        """
        # Restore default drawing functionality
        self.canvas.bind('<ButtonPress-1>', self.start)
        self.canvas.bind('<B1-Motion>', self.paint)
        self.canvas.bind('<ButtonRelease-1>',
                         self.button_release)

        self.canvas['cursor'] = 'spraycan'

        self.last_drawing = self.record_draw

        # Add the figure to the user's drawing history
        self.drawing_history.append(self.last_drawing)

        self.record_draw = []

        self.saved = False

    def select_color(self):
        """Allow the user to select a color for the stroke."""
        selected_color = colorchooser.askcolor(
            'blue', title='Select Color')
        if selected_color[1] is not None:
            self.stroke_color.set(selected_color[1])

    def select_palette_color(self, event, color: str):
        """Set the stroke color to the specified color from the palette.

        Args:
            event (tkinter.Event): The mouse event containing the x and y coordinates.
            color: The color selected from the palette.
        """
        self.stroke_color.set(color)

    def select_canvas_color(self):
        """Allow the user to select a color for the canvas."""
        color = colorchooser.askcolor('blue',
                                      title='Select A Color For The Canvas')
        self.canvas['bg'] = color[1]

        self.saved = False

    def default(self):
        """Set the default settings for the stroke."""
        self.stroke_color.set("black")
        self.stroke_size.set(3)
        self.canvas['cursor'] = 'arrow'

    def clean_all(self):
        """Clean the canvas by deleting all drawings."""
        if len(self.drawing_history):
            answer = messagebox.askyesno(
                title='', message='Are you sure you want to clean your drawing?')
            if answer:
                self.canvas.delete(ALL)
                self.drawing_history = []

    def save_drawing(self):
        """Save the current drawing as an image file.

        Raises:
            Exception: Raise an exception if an error occurs during the save operation.
        """
        try:
            file = filedialog.asksaveasfilename(
                defaultextension='.png',
                initialfile='untitled',
                filetypes=[("PNG", ".png"), ('JPG', '.jpg')])

            ImageGrab.grab(bbox=(
                self.canvas.winfo_rootx(),
                self.canvas.winfo_rooty(),
                self.canvas.winfo_rootx() + self.canvas.winfo_width(),
                self.winfo_rooty() + self.canvas.winfo_height()

            )).save(file)
            messagebox.showinfo(message="Image saved in: " + str(file))
        except:
            if file:
                messagebox.showerror(message='Image not saved\nError')

        self.saved = True

    def save_on_closing(self):
        """Prompt the user to save the drawing before closing the window."""
        if len(self.drawing_history) and self.saved == False:  # Check if there are drawings in the canvas
            answer = messagebox.askyesnocancel(
                message='Would like to save your drawing before closing the window?')

            if answer is not None:  # If the user press 'cancel'
                if answer:  # If the user press 'yes'
                    self.save_drawing()
                elif answer == False:
                    self.quit()

        else:
            self.quit()


if __name__ == '__main__':
    a = ArtStudio()
    a.mainloop()  # Run the app
