__author__ = 'rberg'

import os, sys
import pygame
from pygame.locals import *
import pygame.midi
import random
import tone
if not pygame.font: print('Warning: fonts disabled')
if not pygame.mixer: print('Warning: sound disabled')

class MiditiMain:
    """Main Class, initializes the game"""
    def __init__(self):
        pygame.init()
        info = pygame.display.Info()
        self.width = 600 #info.current_w
        self.height = 400 #info.current_h
        self.screen = pygame.display.set_mode((self.width,self.height)) #,pygame.FULLSCREEN)

        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill(Color("white"))

        self.instrument = MidiMachine(self.screen,self.width,self.height)
        self.key_mappings = {
            K_a: "A",
            K_b: "B",
            K_c: "C",
            K_d: "D",
            K_e: "E",
            K_f: "F",
            K_g: "G",
        }
        self.silenced = False

    def run(self):
        while True:
            if not self.silenced: self.instrument.process()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key in [K_q]:
                        sys.exit()
                    if event.key == K_SPACE:
                        self.toggle_pause()
                    if event.key in self.key_mappings:
                        new_key = self.key_combo_to_key_signature(event.key)
                        self.instrument.change_tone(new_key)
            #Screen
            pygame.display.flip()
            pygame.time.delay(10)
    def toggle_pause(self):
        if self.silenced:
            print("Unpausing")
            pygame.mixer.unpause()
        else:
            print("Pausing")
            pygame.mixer.stop()
        self.silenced = not self.silenced

    def key_combo_to_key_signature(self, key):
        music_note = self.key_mappings.get(key,"C")
        keyboard_modifiers = pygame.key.get_mods()
        music_note_modifier = ""
        if keyboard_modifiers & pygame.KMOD_SHIFT: music_note_modifier = "S"
        music_key_modifier = "M"
        if keyboard_modifiers & pygame.KMOD_CTRL: music_key_modifier = "m"
        return "%s%s%s" % (music_note,music_note_modifier,music_key_modifier)

class MidiMachine:
    MAX_READ_LENGTH = 1024
    STANDARD = 'standard'
    FAKE = 'fake'

    def __init__(self,screen,width,height):
        self.screen = screen
        self.width = width
        self.height = height
        pygame.midi.init()
        self.notes = {}
        self._setup_device()
        self._setup_tones()

    def _setup_tones(self):
        self.tones = []
        index = 0
        octave = 0
        note_names = ['A','Bb','B','C','Db','D','Eb','E','F','Gb','G','Ab']
        while index <= MidiAction.MAX_NOTE:
            for note_name in note_names:
                self.tones.append(
                    tone.GenerateTone(
                        freq='%s%d'%(note_name,octave),
                        vol=0.01,
                    )
                )
                index += 1
            octave = octave + 1
        print("Fully configured %d tones" % len(self.tones))

    def _setup_device(self, auto_pick="USB Axiom 61 Port 1"):
        device_count = pygame.midi.get_count()
        if device_count > 100:
            choice=None
            for midi_id in range(0,device_count):
                if auto_pick == pygame.midi.get_device_info(midi_id)[1]:
                    choice = midi_id
                    break
            if choice is None:
                print("Please choose one of the following:")
                for midi_id in range(0,device_count):
                    pygame.midi.get_device_info(midi_id)
                    print("\t%d: %s" % (midi_id, pygame.midi.get_device_info(midi_id)))
                    choice = input("Which do you want to use? (%s) " % ','.join(str(x) for x in range(0,device_count)))
            self.change_device(int(choice))
            self.midi_mode = MidiMachine.STANDARD
        else:
            self.midi = MidiFaker(.99)
            self.midi_mode = MidiMachine.FAKE

    def change_device(self, device_index):
        try: self.midi = pygame.midi.Input(device_index)
        except: raise Exception("Unknown midi instrument choice: %s" % str(device_index))

    def process(self):
        if self.midi.poll():
            for item in self.midi.read(MidiMachine.MAX_READ_LENGTH):
                self.process_action(MidiAction.from_array(item[0]))

    def process_action(self, action):
        if action.is_type(MidiAction.NOTE_PLAY):
            if action.is_activate(): self.activate_note(action)
            else: self.deactivate_note(action)

    def activate_note(self, note):
        if note.is_valid():
            self.notes[note.target] = note.to_rect(self.width,self.height)
            self.tones[note.target].stop()
            self.tones[note.target].play(loops=-1)
            pygame.draw.rect(self.screen, Color("white"), self.notes[note.target])

    def deactivate_note(self,note):
        if note.is_valid():
            if note.target in self.notes:
                rect = self.notes.pop(note.target)
                self.tones[note.target].stop()
                pygame.draw.rect(self.screen, Color("black"), rect)
            else: raise Exception("Tried to deactivate inactive note: %d-%s" % (note.target,str(note)))

    def draw_instruments(self):
        for note_key, note_action in self.notes:
            pygame.draw.rect(self.screen,color,note_action.to_rect(self.width,self.height))

    def change_tone(self,key):
           if self.midi_mode == MidiMachine.FAKE:
                self.midi.change_key(key)

class MidiAction:
    PITCH_BEND = 244
    NOTE_PLAY = 144
    NOTE_EFFECT = 208
    SLIDER_CHANGE = 176

    MAX_NOTE = 80
    MAX_VELOCITY = 15
    MIN_NOTE = 30
    STATUSES = [
        PITCH_BEND,
        NOTE_PLAY,
        NOTE_EFFECT,
        SLIDER_CHANGE,
    ]

    def __init__(self, status, target, magnitude, something_else):
        self.status = status
        self.target = target
        self.magnitude = magnitude

    def is_activate(self):
        return self.magnitude != 0

    def is_valid(self):
        if self.status == MidiAction.NOTE_PLAY:
            return self.target >= MidiAction.MIN_NOTE and self.target <= MidiAction.MAX_NOTE
        return self.status in MidiAction.STATUSES

    def is_type(self,type):
        return self.status == type

    def to_rect(self,width,height):
        if self.status == MidiAction.NOTE_PLAY:
            left = (float(self.target-MidiAction.MIN_NOTE) / float(MidiAction.MAX_NOTE-MidiAction.MIN_NOTE))*width
            top = height-(float(self.magnitude) / float(MidiAction.MAX_VELOCITY))*height
            width = width/(MidiAction.MAX_NOTE - MidiAction.MIN_NOTE)
            return (
                left,
                top,
                width,
                height-top
            )
        return (0,0,0,0)

    @staticmethod
    def from_array(array):
        return MidiAction(array[0],array[1],array[2],array[3])

class NoteRanges:
    @staticmethod
    def notes_from_key(key):
        picker = {
            "AM": NoteRanges.A,
            "ASM": NoteRanges.AS,
            "BM": NoteRanges.B,
            "BSM": NoteRanges.C,
            "CM": NoteRanges.C,
            "CSM": NoteRanges.CS,
            "DM": NoteRanges.D,
            "DSM": NoteRanges.DS,
            "EM": NoteRanges.E,
            "ESM": NoteRanges.F,
            "FM": NoteRanges.F,
            "FSM": NoteRanges.FS,
            "GM": NoteRanges.G,
            "GSM": NoteRanges.GS,
            "Am": NoteRanges.Am,
            "ASm": NoteRanges.ASm,
            "Bm": NoteRanges.Bm,
            "BSm": NoteRanges.Cm,
            "Cm": NoteRanges.Cm,
            "CSm": NoteRanges.CSm,
            "Dm": NoteRanges.Dm,
            "DSm": NoteRanges.DSm,
            "Em": NoteRanges.Em,
            "ESm": NoteRanges.Fm,
            "Fm": NoteRanges.Fm,
            "FSm": NoteRanges.FSm,
            "Gm": NoteRanges.Gm,
            "GSm": NoteRanges.GSm,
        }
        return picker.get(key, NoteRanges.C)
NoteRanges.C = [x for x in range(MidiAction.MIN_NOTE,MidiAction.MAX_NOTE) if x % 12 in [0,4,7]]
NoteRanges.CS = [x + 1 for x in NoteRanges.C]
NoteRanges.D = [x + 2 for x in NoteRanges.C]
NoteRanges.DS = [x + 3 for x in NoteRanges.C]
NoteRanges.E = [x + 4 for x in NoteRanges.C]
NoteRanges.F = [x + 5 for x in NoteRanges.C]
NoteRanges.FS = [x + 6 for x in NoteRanges.C]
NoteRanges.G = [x + 7 for x in NoteRanges.C]
NoteRanges.GS = [x + 8 for x in NoteRanges.C]
NoteRanges.A = [x + 9 for x in NoteRanges.C]
NoteRanges.AS = [x + 10 for x in NoteRanges.C]
NoteRanges.B = [x + 11 for x in NoteRanges.C]
NoteRanges.Cm = [x for x in range(MidiAction.MIN_NOTE,MidiAction.MAX_NOTE) if x % 12 in [0,3,7]]
NoteRanges.CSm = [x + 1 for x in NoteRanges.Cm]
NoteRanges.Dm = [x + 2 for x in NoteRanges.Cm]
NoteRanges.DSm = [x + 3 for x in NoteRanges.Cm]
NoteRanges.Em = [x + 4 for x in NoteRanges.Cm]
NoteRanges.Fm = [x + 5 for x in NoteRanges.Cm]
NoteRanges.FSm = [x + 6 for x in NoteRanges.Cm]
NoteRanges.Gm = [x + 7 for x in NoteRanges.Cm]
NoteRanges.GSm = [x + 8 for x in NoteRanges.Cm]
NoteRanges.Am = [x + 9 for x in NoteRanges.Cm]
NoteRanges.ASm = [x + 10 for x in NoteRanges.Cm]
NoteRanges.Bm = [x + 11 for x in NoteRanges.Cm]


class MidiFaker:
    VELOCITY_DELTA_MAX = 24
    MAX_SIMULTANEOUS_NOTES = 4

    def __init__(self,starting_key="CM",frequency=.08):
        self.frequency = frequency
        self.last_velocity = random.randint(0,MidiAction.MAX_VELOCITY)
        self.in_transition = True
        self.notes = {}
        self.change_key(starting_key)

    def poll(self):
        if random.random() < self.frequency: return True
        else: return False

    def read(self,unused_read_length=0):
        note = self.random_note()
        velocity = 0
        if note in self.notes:
            self.notes.pop(note)
        else:
            self.notes[note] = True
            velocity = self.random_velocity()
        return (((MidiAction.NOTE_PLAY,note,velocity,0),),)

    def random_velocity(self):
        delta = random.randint(-1*MidiFaker.VELOCITY_DELTA_MAX,MidiFaker.VELOCITY_DELTA_MAX)
        self.last_velocity = min(max(1,self.last_velocity+delta), MidiAction.MAX_VELOCITY)
        return self.last_velocity

    def change_key(self,key):
        print(key)
        self.note_options = NoteRanges.notes_from_key(key)
        self.in_transition = True

    def random_note(self):
        if self.in_transition or len(self.notes) > self.MAX_SIMULTANEOUS_NOTES:
            if len(self.notes) > 0:
                notes = list(self.notes.keys())
                return random.choice(notes)
            self.in_transition = False
        return random.choice(self.note_options)


if __name__ == "__main__":
    MainWindow = MiditiMain()
    MainWindow.run()
