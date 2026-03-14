import pyttsx3
import threading
import pygame
import os
from settings import SND_DIR

class AudioEngine:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        try:
            self.click_snd = pygame.mixer.Sound(os.path.join(SND_DIR, 'click.wav'))
            self.win_snd = pygame.mixer.Sound(os.path.join(SND_DIR, 'tada.wav'))
            pygame.mixer.music.load(os.path.join(SND_DIR, 'bg_music.mp3'))
            pygame.mixer.music.set_volume(0.2)
            pygame.mixer.music.play(-1)
        except:
            self.click_snd, self.win_snd = None, None

    def play_click(self):
        if self.click_snd: self.click_snd.play()

    def play_win(self):
        if self.win_snd: self.win_snd.play()

    def speak(self, text):
        def run_tts():
            try:
                engine = pyttsx3.init() 
                engine.setProperty('rate', 150)
                engine.say(text)
                engine.runAndWait()
            except:
                pass 
        threading.Thread(target=run_tts, daemon=True).start()