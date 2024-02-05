import sys

import pygame
from pygame.locals import *

import speech_recognition as sr

import db_conn as db

pygame.init()


# SETUP #
fps = 60
fpsClock = pygame.time.Clock()

width, height = 640, 480
screen = pygame.display.set_mode((width, height))

font = pygame.font.Font(None, 74)

metronome_frames = (
    "media/images/metronome (1).gif",
    "media/images/metronome (2).gif",
    "media/images/metronome (3).gif",
    "media/images/metronome (4).gif",
    "media/images/metronome (5).gif",
    "media/images/metronome (6).gif",
    "media/images/metronome (7).gif",
    "media/images/metronome (8).gif",
    "media/images/metronome (9).gif",
    "media/images/metronome (10).gif",
    "media/images/metronome (11).gif",
    "media/images/metronome (12).gif",
    "media/images/metronome (13).gif",
    "media/images/metronome (14).gif",
    "media/images/metronome (15).gif",
    "media/images/metronome (16).gif",
    "media/images/metronome (17).gif",
    "media/images/metronome (18).gif",
    "media/images/metronome (19).gif",
    "media/images/metronome (20).gif",
    "media/images/metronome (21).gif",
    "media/images/metronome (22).gif",
    "media/images/metronome (23).gif",
)
frame_index = 0
frame_count = len(metronome_frames)

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
LIGHT_GRAY = (225, 225, 225)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Sidebar menu
SIDEBAR_WIDTH = 200
menu_items = ["choose song", "edit songs", "add song"]
menu_font = pygame.font.Font(None, 32)

# Hint section
hint_font = pygame.font.Font(None, 36)


# VOICE SEARCH #
class VoiceSearch:
    def __init__(self) -> None:
        pass

    def search(self):
        # obtain audio from the microphone
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Say something!")
            audio = r.listen(source)

        # recognize speech using Google Speech Recognition
        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
            print(
                "Google Speech Recognition thinks you said " + r.recognize_google(audio)
            )

            return int(db.getBPM(str(r.recognize_google(audio)).lower()))
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(
                "Could not request results from Google Speech Recognition service; {0}".format(
                    e
                )
            )
        except TypeError:
            print(f"Couldn't find a song named {r.recognize_google(audio)}")


vsearch = VoiceSearch()


# METRONOME
class Metronome:
    BPM = 100

    def __init__(self) -> None:
        pass

    def tick(self):
        return "media/audio/metronome.mp3"

    def setBPM(self, _BPM):
        self.BPM = _BPM


# PROGRAM #

# Boolean variable to track sidebar visibility
sidebar_visible = False

# Metronom tick behaviour
metronome = Metronome()


def tick():
    pygame.mixer.Sound.play(pygame.mixer.Sound(metronome.tick()))
    pygame.time.wait(int(1000 / (metronome.BPM / 60)))


def showBPM():
    text = font.render(str(metronome.BPM), 1, BLACK)
    screen.blit(text, (273, 10))


# Function to display fading text on the screen
def display_fading_text(text, font, color, center):
    alpha = 255  # Initial alpha value (fully opaque)
    fade_speed = 2  # Speed at which the text fades (adjust as needed)

    # Loop until the alpha value becomes 0 (fully transparent)
    while alpha > 0:
        screen.fill(WHITE)  # Clear the screen

        # Render the text surface with the current alpha value
        text_surface = font.render(text, True, color)
        text_surface.set_alpha(alpha)
        text_rect = text_surface.get_rect(center=center)
        screen.blit(text_surface, text_rect)

        pygame.display.flip()

        # Decrease the alpha value
        alpha = max(0, alpha - fade_speed)

        # Delay to control the speed of fading
        pygame.time.delay(10)


# Function to handle the "choose song" menu with scrolling and clickable buttons
def choose_song_menu(song_dict):
    scroll_offset = 0  # Offset for vertical scrolling
    num_visible_songs = height // 50  # Number of visible songs on the screen

    # Loop for the choose song menu
    while True:
        screen.fill(WHITE)  # Clear the screen

        # Draw the visible portion of the song list
        for i in range(num_visible_songs):
            song_index = i + scroll_offset
            if song_index < len(song_dict):
                song_id = list(song_dict.keys())[song_index]
                song_name, artist, bpm = song_dict[song_id]
                text_surface = menu_font.render(
                    f"{song_name} - {artist} ({bpm} BPM)", True, BLACK
                )
                text_rect = text_surface.get_rect(center=(width / 2, 50 + i * 50))
                screen.blit(text_surface, text_rect)

                # Define boundaries for the button
                button_top = 50 + i * 50
                button_bottom = button_top + 50
                button_left = (width / 2) - (text_rect.width / 2)
                button_right = (width / 2) + (text_rect.width / 2)

                # Check if the mouse is clicked within the boundaries of the button
                if button_top <= pygame.mouse.get_pos()[1] <= button_bottom and button_left <= pygame.mouse.get_pos()[0] <= button_right:
                    pygame.draw.rect(screen, LIGHT_GRAY, (button_left, button_top + 10, text_rect.width, 10))

        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None  # Return None if the user presses ESC to cancel
                if event.key == pygame.K_m:
                    return None  # Return None if the user presses M to go back to the main menu
                elif event.key == pygame.K_UP:
                    scroll_offset = max(0, scroll_offset - 1)  # Scroll up
                elif event.key == pygame.K_DOWN:
                    scroll_offset = min(len(song_dict) - num_visible_songs, scroll_offset + 1)  # Scroll down
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check if any song button is clicked
                for i in range(num_visible_songs):
                    song_index = i + scroll_offset
                    if song_index < len(song_dict):
                        song_id = list(song_dict.keys())[song_index]
                        song_name, artist, bpm = song_dict[song_id]
                        text_surface = menu_font.render(
                            f"{song_name} - {artist} ({bpm} BPM)", True, BLACK
                        )
                        text_rect = text_surface.get_rect(center=(width / 2, 50 + i * 50))

                        # Define boundaries for the button
                        button_top = 50 + i * 50
                        button_bottom = button_top + 50
                        button_left = (width / 2) - (text_rect.width / 2)
                        button_right = (width / 2) + (text_rect.width / 2)

                        # Check if the mouse click is within the boundaries of the button
                        if button_top <= event.pos[1] <= button_bottom and button_left <= event.pos[0] <= button_right:
                            chosen_song_bpm = bpm  # Set the chosen song BPM
                            return chosen_song_bpm  # Return the chosen song BPM

        pygame.display.flip()


# Function to handle adding a new song
def add_song_menu():
    inputs = ["", "", ""]  # Store user input for name, artist, and BPM
    max_lengths = [14, 14, 3]  # Maximum lengths for name, artist, and BPM
    active_input = 0  # Index of the active input field

    # Loop for the add song menu
    while True:
        screen.fill(WHITE)  # Clear the screen

        # Draw input boxes and labels
        labels = ["Enter Song Name:", "Enter Artist:", "Enter BPM:"]
        for i, label in enumerate(labels):
            label_surface = menu_font.render(label, True, BLACK)
            label_rect = label_surface.get_rect(center=(width / 2, 150 + i * 100))
            screen.blit(label_surface, label_rect)
            pygame.draw.rect(screen, GRAY, (width / 2 - 100, 170 + i * 100, 200, 30))

        # Draw confirmation button
        confirm_button = menu_font.render("Confirm", True, BLACK)
        confirm_rect = confirm_button.get_rect(center=(width / 2, 445))
        pygame.draw.rect(screen, GRAY, (width / 2 - 50, 430, 100, 30))
        screen.blit(confirm_button, confirm_rect)

        # Draw user input
        for i, (text, max_length) in enumerate(zip(inputs, max_lengths)):
            text = text[:max_length]  # Limit the input to the maximum length
            text_surface = menu_font.render(text, True, BLACK)
            screen.blit(text_surface, (width / 2 - 90, 175 + i * 100))

        # Highlight active input box
        pygame.draw.rect(
            screen, BLACK, (width / 2 - 100, 170 + active_input * 100, 200, 30), 2
        )

        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check if confirm button is clicked
                if confirm_rect.collidepoint(event.pos):
                    # Validate input (you can add more validation if needed)
                    if all(inputs) and inputs[2].isdigit() and int(inputs[2]) > 0:
                        # Add the song to the database
                        db.addSong(*inputs)  # Unpack inputs list
                        print("Song added successfully!")
                        display_fading_text("Song added successfully!", menu_font, GREEN, (width / 2, height / 2))
                        return
                # Check if any input box is clicked
                for i in range(3):
                    if (x := width / 2 - 100) < event.pos[0] < x + 200 and (
                        y := 170 + i * 100
                    ) < event.pos[1] < y + 30:
                        active_input = i
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return  # Return to the main menu if ESC or M is pressed
                elif event.key == pygame.K_BACKSPACE:
                    # Handle backspace to delete characters from input
                    inputs[active_input] = inputs[active_input][:-1]
                elif event.key == pygame.K_RETURN:
                    # Handle ENTER to confirm input
                    if all(inputs) and inputs[2].isdigit() and int(inputs[2]) > 0:
                        db.addSong(*inputs)  # Unpack inputs list
                        print("Song added successfully!")
                        display_fading_text("Song added successfully!", menu_font, GREEN, (width / 2, height / 2))
                        return
                elif event.unicode.isalnum() or event.unicode == " ":
                    # Handle alphanumeric input
                    inputs[active_input] += event.unicode

        pygame.display.flip()

# Function to handle the "edit songs" menu with scrolling and clickable buttons
def edit_songs_menu(song_dict):
    scroll_offset = 0  # Offset for vertical scrolling
    num_visible_songs = height // 50  # Number of visible songs on the screen

    # Loop for the edit songs menu
    while True:
        screen.fill(WHITE)  # Clear the screen

        # Draw the visible portion of the song list with delete buttons
        for i in range(num_visible_songs):
            song_index = i + scroll_offset
            if song_index < len(song_dict):
                song_id = list(song_dict.keys())[song_index]
                song_name, artist, bpm = song_dict[song_id]
                text_surface = menu_font.render(
                    f"{song_name} - {artist} ({bpm} BPM)", True, BLACK
                )
                text_rect = text_surface.get_rect(center=(width / 2, 50 + i * 50))
                screen.blit(text_surface, text_rect)

                # Define boundaries for the delete button
                button_top = 20 + i * 50
                button_bottom = button_top + 50
                button_left = (width / 2) + (text_rect.width / 2) + 10
                button_right = button_left + 100

                # Draw delete button
                pygame.draw.rect(screen, LIGHT_GRAY, (button_left, button_top, 100, 50))
                delete_text = menu_font.render("Delete", True, BLACK)
                delete_rect = delete_text.get_rect(center=(button_left + 50, button_top + 25))
                screen.blit(delete_text, delete_rect)

        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None  # Return None if the user presses ESC to cancel
                if event.key == pygame.K_m:
                    return None  # Return None if the user presses M to go back to the main menu
                elif event.key == pygame.K_UP:
                    scroll_offset = max(0, scroll_offset - 1)  # Scroll up
                elif event.key == pygame.K_DOWN:
                    scroll_offset = min(len(song_dict) - num_visible_songs, scroll_offset + 1)  # Scroll down
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check if any delete button is clicked
                for i in range(num_visible_songs):
                    song_index = i + scroll_offset
                    if song_index < len(song_dict):
                        song_id = list(song_dict.keys())[song_index]
                        song_name, artist, bpm = song_dict[song_id]
                        text_surface = menu_font.render(
                            f"{song_name} - {artist} ({bpm} BPM)", True, BLACK
                        )
                        text_rect = text_surface.get_rect(center=(width / 2, 50 + i * 50))

                        # Define boundaries for the delete button
                        button_top = 20 + i * 50
                        button_bottom = button_top + 50
                        button_left = (width / 2) + (text_rect.width / 2) + 10
                        button_right = button_left + 100

                        # Check if the mouse click is within the boundaries of the delete button
                        if button_top <= event.pos[1] <= button_bottom and button_left <= event.pos[0] <= button_right:
                            # Perform delete action here (you may need to implement this)
                            print(f"Deleting song: {song_name} - {artist}")
                            db.deleteSong(song_id)
                            display_fading_text("Deleted successfully!", menu_font, GREEN, (width / 2, height / 2))
                            # You can remove the song from the dictionary or perform any other action
                            break  # Exit the loop to avoid deleting multiple songs at once

        pygame.display.flip()



# Game loop.
while True:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # VOICE DETECTION MODE
                print("voice recognition mode...")
                search_text = font.render("Listening...", True, RED)
                search_rect = search_text.get_rect(center=(width / 2, height / 2))
                screen.blit(search_text, search_rect)
                pygame.display.flip()
                newBPM = vsearch.search()
                if newBPM is not None:
                    metronome.setBPM(newBPM)
                else:
                    notfound_text = font.render("Song not found", True, RED)
                    notfound_rect = notfound_text.get_rect(
                        center=(width / 2, height / 2 + 50)
                    )
                    search_text.set_alpha(0)
                    screen.blit(search_text, search_rect)
                    pygame.display.flip()
                    screen.blit(notfound_text, notfound_rect)
                    pygame.display.flip()
                    pygame.time.wait(1500)
            elif event.key == pygame.K_m:  # SIDEMENU
                sidebar_visible = not sidebar_visible

    # Update #

    showBPM()

    # Blit (draw) the current frame onto the screen
    current_frame = pygame.image.load(metronome_frames[frame_index])
    draw_frame = pygame.transform.scale(current_frame, (300, 300))
    screen.blit(draw_frame, ((width / 2) - 150, 180))

    # Update the frame index for the next iteration
    frame_index = (frame_index + 1) % frame_count

    # Draw sidebar
    if sidebar_visible:
        sidemenu = True
        while sidemenu:
            pygame.draw.rect(screen, GRAY, (0, 0, SIDEBAR_WIDTH, height))

            # Draw menu items
            for i, item in enumerate(menu_items):
                text_surface = menu_font.render(item, True, BLACK)
                text_rect = text_surface.get_rect(
                    center=(SIDEBAR_WIDTH / 2, 50 + i * 100)
                )
                screen.blit(text_surface, text_rect)

            # Menu events
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Check if any menu item is clicked
                    for i, item in enumerate(menu_items):
                        text_rect = text_surface.get_rect(
                            center=(SIDEBAR_WIDTH / 2, 50 + i * 100)
                        )
                        if text_rect.collidepoint(event.pos):
                            # Perform action based on clicked item
                            if item == "choose song":
                                # Handle "choose song" action
                                songlist = db.getSongs()
                                chosenBPM = choose_song_menu(songlist)
                                if chosenBPM is not None:
                                    metronome.setBPM(chosenBPM)
                                    sidemenu = not sidemenu
                            elif item == "edit songs":
                                # Handle "edit songs" action
                                songlist = db.getSongs()
                                edit_songs_menu(songlist)
                            elif item == "add song":
                                # Handle "add song" action
                                add_song_menu()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        sidebar_visible = not sidebar_visible
                        sidemenu = not sidemenu

            pygame.display.flip()

    # Draw hints
    text_hint_1 = hint_font.render(
        "Press <Space> to activate voice song switch mode", True, GRAY
    )
    hint_1_rect = text_hint_1.get_rect(center=(width / 2, 100))
    screen.blit(text_hint_1, hint_1_rect)

    text_hint_2 = hint_font.render("Press 'm' button to toggle menu", True, GRAY)
    hint_2_rect = text_hint_2.get_rect(center=(width / 2, 140))
    screen.blit(text_hint_2, hint_2_rect)

    text_hint_3 = hint_font.render(
        "Use arrows <Left-Right> to manually adjust BPM", True, GRAY
    )
    hint_3_rect = text_hint_3.get_rect(center=(width / 2, 180))
    screen.blit(text_hint_3, hint_3_rect)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        metronome.setBPM(max(1, metronome.BPM - 1))
        pygame.time.wait(100)
    elif keys[pygame.K_RIGHT]:
        metronome.setBPM(metronome.BPM + 1)
        pygame.time.wait(100)
    else:
        tick()

    # Draw.
    pygame.display.flip()
    fpsClock.tick(fps)
