import pygame
import os
import config.shaku_constants as consts
from services.midi_creator import MidiCreator
from services.conversions import MusicConverter
from services.filing import FileManager

class MusicPlayer:
    """Class for playing music generated from Shakunotator Music -format
    
    Attributes:
        filemanager: FileManager -instance for handling loading and saving files
        midi_creator: MidiCreator instance for generating MIDI -format music representation
    """
    def __init__(self):
        """Constructor, sets up class instances necessary for music playback, and initializes pygame mixer"""
        self._filemanager = FileManager()
        self._midi_creator = MidiCreator(tempo=consts.PLAYBACK_TEMPO)
        pygame.mixer.init()

    def play(self, parts: list):
        """Generates midi file, converts it to wav-format and uses to stream it for playback, fluidsynth installation necessary. After playback, removes temporary .mid and .wav files

        Args:
            parts: List of musical score parts in Shakunotator's Part -instance format
        """
        for part in parts:
            self._midi_creator.create_track(part)
        midi = self._midi_creator.generate_midi()
        tmp_filename = "tmpshaku"
        self._filemanager.save_midi(midi, tmp_filename + ".mid")
        converter = MusicConverter()
        converter.convert(tmp_filename + ".mid", tmp_filename + ".wav")
        pygame.mixer.init()
        pygame.mixer.music.load(tmp_filename + ".wav")
        pygame.mixer.music.play(0, 0.0)
        os.remove(tmp_filename + ".mid")
        os.remove(tmp_filename + ".wav")