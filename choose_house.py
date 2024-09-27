import asyncio
import os
from enum import Enum
import threading

from colour import Color
import edge_tts
from playsound import playsound
import speech_recognition as sr
import tkinter as tk

from database import (
    create_connection,
    create_table,
    get_student_house,
    insert_or_update_student
)
from sorting_hat_gui import SortingHatGUI

class House(Enum):
    GRYFFINDOR = "Gryffindor"
    HUFFLEPUFF = "Hufflepuff"
    RAVENCLAW = "Ravenclaw"
    SLYTHERIN = "Slytherin"

counts = {
    House.GRYFFINDOR: 0,
    House.HUFFLEPUFF: 0,
    House.RAVENCLAW: 0,
    House.SLYTHERIN: 0
}

recognizer = sr.Recognizer()

async def text_to_speech(text, rate="-20%"):
    communicate = edge_tts.Communicate(text, voice='en-GB-ThomasNeural')
    await communicate.save('temp.wav')
    playsound('temp.wav')
    os.remove('temp.wav')

async def speak(text, background_color=None, image_paths=None):
    gui = SortingHatGUI.get_instance()
    gui.update_label(text)
    
    if image_paths:
        gui.display_images(image_paths)
    else:
        gui.stop_gif()
        gui.play_gif()
    
    if background_color:
        gui.set_background_color(background_color)
    else:
        gui.set_background_color('red')
    
    await text_to_speech(text)
    
    gui.reset_background()

async def listen(seconds=3, use_last_word=True):
    text = ""
    gui = SortingHatGUI.get_instance()
    try:
        with sr.Microphone() as source:
            print(f"Recording for {seconds} seconds")
            gui.set_background_color('green')
            recorded_audio = await asyncio.to_thread(recognizer.listen, source, timeout=seconds)
            print("Done recording")
            gui.reset_background()

        print("Recognizing the text")
        text = await asyncio.to_thread(recognizer.recognize_google, recorded_audio, language="en-US")
        print(f"Decoded Text: {text}")
    except sr.WaitTimeoutError:
        gui.reset_background()
        pass
    except Exception as ex:
        gui.reset_background()
        print(ex)

    if text and use_last_word:
        return text.split()[-1]
    return text

async def get_name():
    await speak("Now...state your name!")
    name = await listen()
    
    retries = 0
    
    while not name and retries < 3:
        retries += 1
        await speak(f"I'm sorry; I didn't catch that. Could you please state your name again?")
        name = await listen()
    
    if not name:
        await speak("I'm sorry, but I couldn't catch your name. Let's try again later.")
        return None
    
    return name.title()

def check_color(color):
    try:
        Color(color.replace(" ", ""))
        return True
    except ValueError:
        return False

async def get_favorite_color():
    await speak("What is your favorite color?")
    
    retries = 0
    max_retries = 3
    
    while retries < max_retries:
        color = await listen()
        if check_color(color) and color is not None and color != "":
            return color
        else:
            retries += 1
            if retries < max_retries:
                await speak(f"I'm sorry, but {color} doesn't seem to be a valid color. Please try again with a different color.")
            else:
                await speak("...I couldn't understand your favorite color.")
                return None

    return None

def update_house_counts_from_color(favorite_color):
    if favorite_color.lower() in ["yellow", "gold"]:
        counts[House.HUFFLEPUFF] += 1
    elif favorite_color.lower() in ["blue"]:
        counts[House.RAVENCLAW] += 1
    elif favorite_color.lower() in ["teal", "silver", "green", "gray", "grey"] or "aqua" in favorite_color.lower():
        counts[House.SLYTHERIN] += 1
    elif favorite_color.lower() in ["red", "scarlet", "maroon", "crimson", "ruby", "crimson", "burgundy", "pink", "rose", "magenta", "violet", "purple", "lavender", "indigo", "blue", "teal", "turquoise", "green", "olive", "lime", "chartreuse", "gold",  "orange"]:
        counts[House.GRYFFINDOR] += 1

async def ask_favorite_color_question():
    favorite_color = await get_favorite_color()
    if favorite_color is None:
        return None
    update_house_counts_from_color(favorite_color)
    await speak(f"Ah yes...{favorite_color}!  An excellent color!", favorite_color)
    return favorite_color

async def get_pet_type():
    pet_images = ["assets/Cat.png", "assets/Owl.png", "assets/Rat.png", "assets/Toad.png"]
    await speak("Hogwarts allows students to care for a small pet, teaching companionship and responsibility. If you were given a choice of the following creatures, which would strike your fancy? Cat, toad, rat, or owl.", image_paths=pet_images)
    
    valid_pets = ["cat", "toad", "rat", "owl"]
    while True:
        response = await listen(seconds=30, use_last_word=False)
        response_words = response.lower().split()
        
        for word in response_words:
            if word in valid_pets:
                SortingHatGUI.get_instance().hide_images()
                return word

        await speak("I'm sorry, I didn't catch that. Please choose either a cat, toad, rat, or owl.", image_paths=pet_images)

def update_house_counts_from_pet_type(pet_type):
    if pet_type.lower() == "toad":
        counts[House.HUFFLEPUFF] += 1
    elif pet_type.lower() == "owl":
        counts[House.RAVENCLAW] += 1
    elif pet_type.lower() == "rat":
        counts[House.SLYTHERIN] += 1
    else:
        counts[House.GRYFFINDOR] += 1

async def ask_pet_type_question():
    pet_type = await get_pet_type()
    update_house_counts_from_pet_type(pet_type)
    
    pet_image = f"assets/{pet_type.capitalize()}.png"
    gui = SortingHatGUI.get_instance()
    gui.display_image(pet_image)
    
    await speak(f"Ah yes...the {pet_type}! A wonderful creature!")
    
    gui.hide_image()
    
    return pet_type

async def get_adjective_descriptors():
    await speak("A Hogwarts student should always be able to describe themselves well.  List adjectives that describe you.")
    
    async def listen_with_timeout():
        try:
            return await listen(seconds=5, use_last_word=False)
        except Exception as e:
            print(f"Error during listening: {e}")
            return ""

    adjectives = await listen_with_timeout()
    
    if not adjectives:
        await speak("I'm sorry, I didn't catch that. Could you please try again?")
        adjectives = await listen_with_timeout()
    
    return adjectives

def update_house_count_from_adjectives(adjectives):
    gryffindor_adjectives = ["brave", "daring", "funny", "adventurous", "happy", "fearless", "nervous", "kind", "proud", "silly"]
    hufflepuff_adjectives = ["hardworking", "hard-working", "loyal", "nice", "patient", "friendly", "calm", "sad", "honest", "generous", "helpful"]
    ravenclaw_adjectives = ["smart", "creative", "imaginative", "perceptive", "thoughtful", "peaceful", "interesting", "curious", "innovative"]
    slytherin_adjectives = ["ambitious", "determined", "sneaky", "careful", "shy", "clever", "shrewd", "sad", "persistent", "focused", "frustrated", "evil"]
    
    words = adjectives.lower().split()
    
    for word in words:
        if word in gryffindor_adjectives:
            counts[House.GRYFFINDOR] += 1
        elif word in hufflepuff_adjectives:
            counts[House.HUFFLEPUFF] += 1
        elif word in ravenclaw_adjectives:
            counts[House.RAVENCLAW] += 1
        elif word in slytherin_adjectives:
            counts[House.SLYTHERIN] += 1

async def ask_adjective_descriptor_question():
    adjectives = await get_adjective_descriptors()
    update_house_count_from_adjectives(adjectives)
    await speak(f"Ah yes...you do seem like a very {', '.join(adj.lower() for adj in adjectives.split())} person. Interesting...")
    return adjectives.split()

async def listen_for_house_choice():
    sounds = await listen(seconds=5, use_last_word=False)
    sounds = sounds.lower()
    houses = [house.value for house in House]

    for house in houses:
        not_pattern = f'not {house.lower()}'
        not_count = sounds.count(not_pattern)
        if not_count > 0:
            counts[House(house)] -= not_count

        house_count = sounds.count(house.lower())
        if house_count > 0:
            counts[House(house)] += house_count

async def speak_chosen_house(house):
    gui = SortingHatGUI.get_instance()
    if isinstance(house, House):
        house_name = house.value
    elif isinstance(house, str):
        house_name = house
    else:
        print(f"Unexpected house type: {type(house)}")
        house_name = House.GRYFFINDOR.value
    gui.update_label(house_name.upper())

    image_path = f"assets/{house_name}.png"
    audio_path = f"assets/{house_name}.mp3"

    gui.display_image(image_path)
    playsound(audio_path)
    gui.hide_image()

def quit_app(conn):
    SortingHatGUI.get_instance().close_window()
    conn.close()
    exit()

async def run_sorting_ceremony(root):
    conn = create_connection()
    create_table(conn)
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
    await speak("Hogwarts School of Witchcraft and Wizardry would like to welcome you to Aaliyah's birthday party!")
    await speak("Your sorting ceremony, where you will be placed into a house, will begin shortly.")
    await speak("Each house has its own noble history, and each has produced outstanding witches and wizards.")
    await speak("Try to stick to one-word responses unless I specify otherwise.")
    await speak("Also note that I will only be able to hear you when the background is green!")
    name = await get_name()
    if name is None:
        return
    student_house = get_student_house(conn, name)
    if student_house is not None:
        await speak(f"Hello again, {name}! I've already sorted you into a house: {student_house}! Would you like me to announce it again?")
        should_announce = await listen()
        if should_announce.lower() == "yes":
            await speak_chosen_house(student_house)
            quit_app(conn)
            return
        await speak("Or would you rather try the sorting ceremony again?")
        redo_ceremony = await listen()
        if redo_ceremony.lower() != "yes":
            await speak(f"Very well, {name}. Until next time!")
            quit_app(conn)
            return
    else:
        await speak(f"Right! Hello there, {name}, nice to meet you!")
    await speak("Let us begin the sorting ceremony! The first bit of information I'd like to know:")
    favorite_color = await ask_favorite_color_question()
    if favorite_color is None:
        await speak("I'm sorry, but we couldn't complete the sorting ceremony. Let's try again another time.")
        quit_app(conn)
        return
    await speak("Let's move along.")
    pet_type = await ask_pet_type_question()
    await speak("And now on to our final question.")
    adjective_descriptors = await ask_adjective_descriptor_question()
    await speak("Give me a few moments to sort you into a house.")
    await speak("Feel free to take a deep breath or to whisper something the way Harry Potter famously did.")
    await listen_for_house_choice()
    chosen_house = max(counts, key=counts.get)
    insert_or_update_student(conn, name, favorite_color, pet_type, adjective_descriptors, chosen_house.value)
    print(f"Student {name} has been sorted into {chosen_house.value}!")
    print(f"Counts: {counts}")
    await speak_chosen_house(chosen_house)
    quit_app(conn)

if __name__ == "__main__":
    root = tk.Tk()
    gui = SortingHatGUI(root)

    async def main():
        await run_sorting_ceremony(root)

    def run_async():
        asyncio.run(main())

    threading.Thread(target=run_async, daemon=True).start()
    
    root.mainloop()
