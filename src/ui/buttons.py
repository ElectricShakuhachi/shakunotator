from tkinter import Button, Entry, constants, Frame, ttk, Label, Checkbutton, BooleanVar, Menu
import pygame
from PIL import Image, ImageTk
from services.filing import FileManager
from services.midi_creator import MidiCreator
from services.music_player import MusicPlayer
from services.image_creator import ImageCreator
from services.svg_creator import SvgCreator
from ui.messages import ShakuMessage
import config.shaku_constants as consts
from commands.commands import Commands
from ui.ui import UI

class Buttons:
    """Container for user interface Buttons"""
    def __init__(self, main_ui):
        """Construct class attributes and generate default buttons

        Args:
            ui: Main ui container instance
        """
        self.main_ui = main_ui
        self.buttons = {}
        self.frames = {}
        self.buttons_by_frame = {}
        self.textboxes = {}
        self.textboxbuttons = {}
        self.separators = {}
        self.labels = []
        self.chosen_lenght = 8
        self.saved = True
        self._octave = "Otsu"
        self._create_default_buttons()
        self.buttons["Add Part"].press()
        self.commands = Commands(self.main_ui)
        self._setup_menu(self.main_ui.window)

    @property
    def octave(self):
        return self._octave

    @octave.setter
    def octave(self, octave: str):
        if octave not in ["Otsu", "Kan", "Daikan"]:
            raise ValueError("Not a valid shakuhachi notation register")
        self._octave = octave

    def _create_default_buttons(self):
        self._create_naming_frame()
        self._create_octave_buttons()
        self._create_note_buttons()
        self._create_break_buttons()
        self._create_lenght_buttons()
        self._create_part_buttons()
        self._create_export_buttons()
        self._create_file_buttons()
        self._create_play_buttons()

    def _create_octave_buttons(self):
        buttons = []
        for octave in ["Otsu", "Kan", "Daikan"]:
            buttons.append({'text': octave, "button_class": OctaveButton})
        self._generate_button_frame(
            "Octave",
            buttons,
            self.main_ui.frames["right"],
            separator=False
            )
        self.separators["Octave"] = ButtonSeparator(self.main_ui.frames["right"])

    def _create_note_buttons(self):
        frame = self.frames["Notes"] = Frame(self.main_ui.frames["right"])
        frame.pack(side=constants.TOP)
        self.populate_note_buttons(frame, self._octave)
        self.separators["Note"] = ButtonSeparator(self.main_ui.frames["right"])

    def _clear_note_buttons(self):
        old_frames = []
        for key, value in self.frames.items():
            if "Note " in key:
                value.destroy()
                old_frames.append(key)
        for found in old_frames:
            self.frames.pop(found)

    def populate_note_buttons(self, frame, octave):
        """Fill note button frame depending on chosen octave

        Args:
            frame: Frame to put buttons to
            octave: Octave based on which notes are chosen
        """
        self._clear_note_buttons()
        notes = consts.NOTES
        buttons = {}
        for key in notes:
            buttons[key] = {'text': f"Pitch {key}", 'data': key, "button_class": NoteButton}
        if octave == "Otsu":
            mini = 0
            maxi = 13
        elif octave == "Kan":
            mini = 14
            maxi = 30
        elif octave == "Daikan":
            mini = 29
            maxi = 41
        i = mini
        while i < maxi:
            frame_buttons = [buttons[x] for x in range(i, min(i + 4, maxi))]
            self._generate_button_frame(f"Note {i}", frame_buttons, frame, separator=False)
            i += 4

    def _create_break_buttons(self):
        buttons = [{"text": "8th_break", "data": -1, "button_class": NoteButton},
        {"text": "4th_break", "data": -2, "button_class": NoteButton},
        {"text": "half_break", "data": -4, "button_class": NoteButton}
        ]
        if consts.MEASURE_LENGHT >= 4:
            buttons.append({"text": "whole_break", "data": -8, "button_class": NoteButton})
        self._generate_button_frame("Break", buttons, self.main_ui.frames["right"], separator=False)
        self.separators["Break"] = ButtonSeparator(self.main_ui.frames["right"])

    def _create_lenght_buttons(self):
        buttons = []
        for data, text in consts.LENGHTS.items():
            buttons.append({"text": text, "data": data, "button_class": LenghtButton})
        self._generate_button_frame("Duration", buttons, self.main_ui.frames["right"])

    def _create_part_buttons(self):
        buttons = [
            {"text": "Add Part", "button_class": AddPartButton},
        ]
        self._generate_button_frame(
            "Add Part",
            buttons,
            self.main_ui.frames["right"],
            separator=False
            )
        self._generate_button_frame("Parts", None, self.main_ui.frames["right"], separator=False)
        self.separators["Parts"] = ButtonSeparator(self.main_ui.frames["right"])

    def _create_export_buttons(self):
        buttons = [
            {"text": "export MIDI", "button_class": ExportMidiButton},
            {"text": "export PDF", "button_class": ExportPdfButton},
            {"text": "export SVG", "button_class": ExportSvgButton}
        ]
        self._generate_button_frame(
            "Export",
            buttons,
            self.main_ui.frames["right"],
            separator=False
            )
        self.buttons["grid_option_choice"] = BooleanVar()
        self.buttons["sheet_grid_option"] = Checkbutton(
            self.main_ui.frames["right"], text="Include grid",
            variable=self.buttons["grid_option_choice"],
            onvalue=True,
            offvalue=False
            )
        self.buttons["sheet_grid_option"].pack()
        self.separators["Export"] = ButtonSeparator(self.main_ui.frames["right"])

    def _create_file_buttons(self):
        buttons = [
            {"text": "upload", "button_class": UploadButton}
        ]
        self._generate_button_frame("File", buttons, self.main_ui.frames["right"])

    def _create_play_buttons(self):
        buttons = [{"text": "Play/Stop", "button_class": PlayButton}]
        self._generate_button_frame("Play", buttons, self.main_ui.frames["right"], separator=False)

    def _create_naming_frame(self):
        self.textboxes["musicname"] = (Entry(self.main_ui.frames["top1"]))
        self.textboxes["composername"] = (Entry(self.main_ui.frames["top2"]))
        self.textboxbuttons["namebutton"] = (
            Button(self.main_ui.frames["top1"], text="Add Name", command=self.add_name)
            )
        self.textboxbuttons["composerbutton"] = (
            Button(self.main_ui.frames["top2"], text="Add Composer", command=self.add_composer)
            )
        for label in self.textboxbuttons.values():
            label.pack(side = constants.LEFT)
        for box in self.textboxes.values():
            box.pack(side = constants.RIGHT)

    def _generate_button_frame(
        self,
        text: str,
        buttoninfo,
        parent_frame,
        label=True,
        separator=True
        ):
        frame = self.frames[text] = Frame(parent_frame)
        frame.pack(side=constants.TOP)
        self.frames[text] = frame
        if label:
            self.labels.append(Label(frame, text=text))
        self.buttons_by_frame[text] = []
        if buttoninfo:
            for button_spec in buttoninfo:
                if 'data' in button_spec:
                    button = button_spec['button_class'](
                        button_spec['text'],
                        button_spec['data'],
                        self.main_ui,
                        self,
                        frame
                        )
                else:
                    button = button_spec['button_class'](
                    button_spec['text'],
                    self.main_ui,
                    self,
                    frame
                    )
                if "Note" in text or text in ("Parts", "Octave", "Break"):
                    button.button.pack(side=constants.LEFT)
                else:
                    button.button.pack(side=constants.TOP)
                self.buttons[button_spec['text']] = button
                self.buttons_by_frame[text].append(button)
        if separator:
            self.separators[text] = ButtonSeparator(frame)

    def add_name(self, name=None):
        """Set composition name

        Args:
            name: Name to be added. If None, name is fetched from textbox
        """
        if not name:
            name = self.textboxes["musicname"].get()
        try:
            self.main_ui.music.name = name
        except ValueError:
            self.main_ui.messages.append(ShakuMessage("long_name_and_composer"))
        self.main_ui.draw_texts()

    def add_composer(self, composer=None):
        """Set composer name

        Args:
            composer: Name to be added. If None, composer is fetched from textbox
        """
        if not composer:
            composer = self.textboxes["composername"].get()
        try:
            self.main_ui.music.composer = composer
        except ValueError:
            self.main_ui.messages.append(ShakuMessage("long_name_and_composer"))
        self.main_ui.draw_texts()

    def load_json(self, data):
        """Set name/composer from data and forward to UI

        Args:
            data: JSON -format data
        """
        self.main_ui.load_json(data)
        self.add_name(data['name'])
        self.add_composer(data['composer'])

    def _load(self):
        if not self.saved: # refactor later -> some of the framework already exists
            self.main_ui.messages.append(ShakuMessage("Overwrite"))
        data = self.commands.load()
        if data is None:
            return
        self.load_json(data)
        self.buttons["Add Part"].button.config(state="normal", relief=constants.RAISED)
        for button in self.buttons_by_frame["Parts"]:
            if button.text != "Add Part":
                button.button.destroy()
        self.buttons_by_frame["Parts"] = [self.buttons["Add Part"]]
        for part_id in data["parts"].keys():
            self.buttons["Add Part"].press(loading_part=int(part_id))
        self.buttons_by_frame["Parts"][1].press()
        self.saved = True

    def _dummy_command(self):
        self.main_ui.messages.append(ShakuMessage("dev"))

    def _setup_menu(self, root): #maybe refactor -> get list of texts + their commands
        menu = Menu(root)
        file_menu = Menu(menu, tearoff=0)
        file_menu.add_command(label="New", command=self._dummy_command)
        file_menu.add_command(label="Open", command=self._load)
        file_menu.add_command(label="Save", command=self.commands.save)
        file_menu.add_command(label="Save As", command=self.commands.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Properties", command=self._dummy_command)
        file_menu.add_separator()
        file_menu.add_command(label="Export Sheet", command=self._dummy_command)
        file_menu.add_command(label="Import", command=self._dummy_command)
        file_menu.add_separator()
        file_menu.add_command(label="Export Sound", command=self._dummy_command)
        file_menu.add_separator()
        file_menu.add_command(label="Upload", command=self._dummy_command)
        file_menu.add_command(label="Download", command=self._dummy_command)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self._dummy_command)
        menu.add_cascade(label="File", menu=file_menu)

        edit_menu = Menu(menu, tearoff=0)
        edit_menu.add_command(label="Undo", command=self._dummy_command)
        edit_menu.add_command(label="Redo", command=self._dummy_command)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self._dummy_command)
        edit_menu.add_command(label="Copy", command=self._dummy_command)
        edit_menu.add_command(label="Paste", command=self._dummy_command)
        edit_menu.add_separator()
        edit_menu.add_command(label="Find/Replace", command=self._dummy_command)
        menu.add_cascade(label="Edit", menu=edit_menu)

        insert_menu = Menu(menu, tearoff=0)
        insert_menu.add_command(label="Special notations", command=self._dummy_command)
        insert_menu.add_command(label="Create custom notation", command=self._dummy_command)
        insert_menu.add_command(label="Insert text", command=self._dummy_command)
        menu.add_cascade(label="Insert", menu=insert_menu)

        parts_menu = Menu(menu, tearoff=0)
        parts_menu.add_command(label="Add part", command=self._dummy_command)
        parts_menu.add_command(label="Configure parts", command=self._dummy_command)
        menu.add_cascade(label="Parts", menu=parts_menu)

        play_menu = Menu(menu, tearoff=0)
        play_menu.add_command(label="Play / Stop", command=self._dummy_command)
        play_menu.add_command(label="Playback options", command=self._dummy_command)
        menu.add_cascade(label="Play", menu=play_menu)

        help_menu = Menu(menu, tearoff=0)
        help_menu.add_command(label="Guide", command=self._dummy_command)
        help_menu.add_command(label="Fingering charts", command=self._dummy_command)
        menu.add_cascade(label="Help", menu=help_menu)

        root.config(menu=menu)

class ButtonSeparator:
    """Horizontal line to separate buttons"""
    def __init__(self, frame, pady=10):
        """Generate horizontal divider line

        Args:
            frame: Tkinter frame to generate line to
            pady: Padding for line. Defaults to 10.
        """
        self.line = ttk.Separator(frame, orient="horizontal")
        self.line.pack(fill="x", pady=pady)

class OctaveButton():
    """Button for octave and its linked functionality"""
    def __init__(self, text, main_ui, owner, frame):
        """Initialize button data and connections

        Args:
            text: Button text
            ui: UI instance
            owner: Container class
            frame: Tkinter frame to show button in
        """
        self.main_ui = main_ui
        self.owner = owner
        self.text = text
        self.button = Button(frame, text=self.text, font="Shakunotator", command=self.press)
        #if self.text == "Otsu":
        #   self.button.config(relief=constants.SUNKEN, state="disabled")
        image = Image.open(consts.OCTAVES[self.text])
        scale =  consts.BUTTON_NOTE_SIZE / 1000
        self.pil_img = image.resize([int(scale * s) for s in image.size])
        self.image = ImageTk.PhotoImage(self.pil_img)
        self.button.config(
            image=self.image,
            width=consts.NOTE_BUTTON_SIZE,
            height=consts.NOTE_BUTTON_SIZE
            )

    def press(self, auto_press=False):
        """Configs octave for upcoming notes

        Args:
            auto_press: Set to True if used by program itself
        """
        self.owner.octave = self.text
        self.owner.populate_note_buttons(self.owner.frames["Notes"], self.owner.octave)
        self.button.config(relief=constants.SUNKEN, state="disabled")
        for button in self.owner.buttons_by_frame["Octave"]:
            if button.text != self.text:
                button.button.config(relief=constants.RAISED, state="normal")
        if not auto_press:
            self.main_ui.active_part.clear_pre_existing_notation()
            self.main_ui.active_part.append_misc_notation(self.text)
            self.main_ui.update()

class NoteButton():
    """Button used to add a musical note
    """
    def __init__(self, text, data, main_ui: UI, owner, frame):
        """Initialize button data and connections

        Args:
            text: Button text
            data: pitch of note
            ui: UI instance
            owner: Container class
            frame: Tkinter frame to show button in
        """
        self.main_ui = main_ui
        self.owner = owner
        self.text = text
        self.button = Button(frame, text=self.text, font="Shakunotator", command=self.press)
        self.pitch = data
        image = Image.open(consts.NOTES[self.pitch])
        scale = consts.BUTTON_NOTE_SIZE / 1000
        self.pil_img = image.resize([int(scale * s) for s in image.size])
        self.image = ImageTk.PhotoImage(self.pil_img)
        self.button.config(
            image=self.image,
            width=consts.NOTE_BUTTON_SIZE,
            height=consts.NOTE_BUTTON_SIZE
            )

    def press(self):
        """Adds a note on part currently under edition if not full"""
        if self.pitch < 0:
            lenght = abs(self.pitch) * 4
        else:
            lenght = self.owner.chosen_lenght
        if self.main_ui.add_note(self.pitch, lenght):
            self.owner.saved = False

class LenghtButton():
    """Button for choosing a lenght for upcoming musical notes
    """
    def __init__(self, text, data, main_ui, owner, frame):
        """Initialize button data and connections

        Args:
            text: Button text
            data: lenght relative to 32th note speed
            ui: UI instance
            owner: Container class
            frame: Tkinter frame to show button in
        """
        self.main_ui = main_ui
        self.owner = owner
        self.text = text
        self.button = Button(frame, text=self.text, font="Shakunotator", command=self.press)
        self.lenght = data

    def press(self):
        """Choose a lenght for following notes on currently chosen part"""
        self.owner.chosen_lenght = self.lenght
        self.button.config(state="disabled", relief=constants.SUNKEN)
        for button in self.owner.buttons_by_frame["Duration"]:
            if button.text != self.text:
                button.button.config(state="normal", relief=constants.RAISED)

class AddPartButton():
    """Button for adding a part on ensemble sheet music
    """
    def __init__(self, text, main_ui, owner, frame):
        """Initialize button data and connections

        Args:
            text: Button text
            ui: UI instance
            owner: Container class
            frame: Tkinter frame to show button in
        """
        self.main_ui = main_ui
        self.owner = owner
        self.text = text
        self.button = Button(frame, text=self.text, font="Shakunotator", command=self.press)

    def _add_part_button(self, part_id):
        new_button = PartButton(
            part_id,
            part_id,
            self.main_ui,
            self.owner,
            self.owner.frames["Parts"]
            )
        self.owner.buttons_by_frame["Parts"].append(new_button)
        new_button.button.pack(side=constants.LEFT)
        return new_button

    def press(self, loading_part=None):
        """Add a part on sheet music being edited

        Args:
            loading_part: id of part being loaded (when parts added on load).
        """
        if loading_part is None:
            i = len(self.main_ui.music.parts) + 1
            self.main_ui.music.add_part(i)
            new_button = self._add_part_button(i)
        else:
            new_button = self._add_part_button(loading_part)
        self.main_ui.update()
        if new_button and not loading_part:
            new_button.press()
        if len(self.main_ui.music.parts) > 3:
            self.button.config(state="disabled", relief=constants.SUNKEN)

class PartButton():
    """Button for choosing a part (ShakuPart) to edit
    """
    def __init__(self, text, data, main_ui, owner, frame):
        """Initialize button data and connections

        Args:
            text: Button text
            data: reference to part to be chosen by this button
            ui: UI instance
            owner: Container class
            frame: Tkinter frame to show button in
        """
        self.main_ui = main_ui
        self.owner = owner
        self.text = text
        self.button = Button(frame, text=self.text, font="Shakunotator", command=self.press)
        self.part = data

    def press(self):
        """Choose musical part in ensemble music to edit"""
        self.button.config(state="disabled", relief=constants.SUNKEN)
        for button in self.owner.buttons_by_frame["Parts"]:
            if button.text not in (self.text, "Add Part"):
                button.button.config(state="normal", relief=constants.RAISED)
        self.main_ui.active_part = self.main_ui.music.parts[self.part]
        self.owner.buttons["4th"].press()

class ExportMidiButton():
    """Button for exporting music in midi form
    """
    def __init__(self, text, main_ui, owner, frame):
        """Initialize button data and connections

        Args:
            text: Button text
            ui: UI instance
            owner: Container class
            frame: Tkinter frame to show button in
        """
        self.main_ui = main_ui
        self.owner = owner
        self.text = text
        self.button = Button(frame, text=self.text, font="Shakunotator", command=self.press)
        self.creator = MidiCreator()
        self.filemanager = FileManager()

    def press(self):
        """Export currently edited music to MIDI -format file"""
        for part in self.main_ui.music.parts.values():
            self.creator.create_track(part)
        midi = self.creator.generate_midi()
        self.filemanager.save_midi(midi)

class ExportPdfButton():
    """Button for exporting sheet in pdf form
    """
    def __init__(self, text, main_ui, owner, frame):
        """Initialize button data and connections

        Args:
            text: Button text
            ui: UI instance
            owner: Container class
            frame: Tkinter frame to show button in
        """
        self.main_ui = main_ui
        self.owner = owner
        self.text = text
        self.button = Button(frame, text=self.text, font="Shakunotator", command=self.press)

    def press(self):
        """Export currently edited music sheet to PDF -format file"""
        filemanager = FileManager()
        image_creator = ImageCreator()
        images = image_creator.create_images(
            self.main_ui.music,
            self.owner.buttons["grid_option_choice"].get()
            )
        filemanager.save_pdf(images)

class ExportSvgButton():
    """Button for exporting sheet in svg form
    """
    def __init__(self, text, main_ui, owner, frame):
        """Initialize button data and connections

        Args:
            text: Button text
            ui: UI instance
            owner: Container class
            frame: Tkinter frame to show button in
        """
        self.main_ui = main_ui
        self.owner = owner
        self.text = text
        self.button = Button(frame, text=self.text, font="Shakunotator", command=self.press)

    def press(self):
        """Export currently edited music sheet to SVG -format file"""
        filemanager = FileManager()
        svg_creator = SvgCreator()
        svg = svg_creator.create_svg(
            self.main_ui.music,
            self.owner.buttons["grid_option_choice"].get()
            )
        filemanager.save_svg(svg)

class PlayButton():
    """Button for music playback
    """
    def __init__(self, text, main_ui, owner, frame):
        """Initialize button data and connections

        Args:
            text: Button text
            ui: UI instance
            owner: Container class
            frame: Tkinter frame to show button in
        """
        self.main_ui = main_ui
        self.owner = owner
        self.text = text
        self.button = Button(frame, text=self.text, font="Shakunotator", command=self.press)
        self.player = MusicPlayer()

    def press(self):
        """Play a generated audio of the music currently being edited"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        else:
            self.player.play(self.main_ui.music.parts.values())

class UploadButton():
    """Button for uploading to AWS S3
    """
    def __init__(self, text, main_ui, owner, frame):
        """Initialize button data and connections

        Args:
            text: Button text
            ui: UI instance
            owner: Container class
            frame: Tkinter frame to show button in
        """
        self.main_ui = main_ui
        self.owner = owner
        self.text = text
        self.button = Button(frame, text=self.text, font="Shakunotator", command=self.press)

    def press(self):
        """Upload currently edited music sheet to .shaku (JSON) -file to AWS S3"""
        filemanager = FileManager()
        data = self.main_ui.music.convert_to_json()
        name = self.main_ui.music.name
        if not name or name == "":
            self.main_ui.messages.append(ShakuMessage("No Name"))
        elif not filemanager.upload_to_aws_s3(data, name=name):
            self.main_ui.messages.append(ShakuMessage("No Access"))
