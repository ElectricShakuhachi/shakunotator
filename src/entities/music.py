from types import prepare_class
from copy import copy

class Note:
    def __init__(self, text: str, pitch: int, position: list, lenght=8):
        self.text = text
        self.pitch = pitch
        self.lenght = lenght
        self.position = position

class Music:
    def __init__(self):
        self.notes = []
        self.name = ""
        self.composer = ""
        self.next_lenght = 8
        self.measure_counter = 0

    def next_position(self):
        if len(self.notes) == 0:
            return [505, 80]
        next = copy(self.notes[-1].position)
        next[1] += self.notes[-1].lenght * 6
        if self.measure_counter == 0:
            next[1] += 14
        if next[1] > 830:
            next[1] = 80
            next[0] -= 60
        return next

    def add_note(self, note: Note):
        if note.position[0] < 30:
            return "full"
        else:
            self.notes.append(note)
            self.measure_counter += note.lenght
            if self.measure_counter == 16:
                self.measure_counter = 0
            return "ok"