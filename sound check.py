import pygame

# Initialize Pygame and mixer
pygame.init()
pygame.mixer.init()

# Load and play sound
try:
    pygame.mixer.music.load("mario.wav")
    pygame.mixer.music.play(-1)  # Loop indefinitely
except pygame.error as e:
    print(f"Error loading sound: {e}")

# Keep the program running to hear the sound
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
