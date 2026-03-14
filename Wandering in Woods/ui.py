import pygame
from settings import *

class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = pygame.font.SysFont("comicsansms", 20)
        # Added dynamic color support
        self.color = BTN_COLOR
        self.hover_color = BTN_HOVER

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        # Uses custom colors if assigned, otherwise defaults to blue
        current_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=8)
        
        txt_surface = self.font.render(self.text, True, (255,255,255))
        txt_rect = txt_surface.get_rect(center=self.rect.center)
        surface.blit(txt_surface, txt_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class SmallButton(Button):
    def __init__(self, x, y, w, h, text):
        super().__init__(x, y, w, h, text)
        self.font = pygame.font.SysFont("comicsansms", 16)

def draw_text(surface, text, x, y, size=24, color=TEXT_COLOR):
    font = pygame.font.SysFont("comicsansms", size)
    txt_surface = font.render(text, True, color)
    surface.blit(txt_surface, (x, y))