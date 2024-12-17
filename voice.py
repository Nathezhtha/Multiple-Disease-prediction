import os
import pygame
import playsound
from gtts import gTTS
from translate import Translator
from playsound import playsound
import time

class voice_call:
    def __init__(self):
        pygame.mixer.init()
    def speak(self,text,language):

        translator = Translator(from_lang="en", to_lang=language)
        translation = translator.translate(text)
        mytext = translation
        myobj = gTTS(text=mytext, lang=language, slow=True)
        myobj.save("a.mp3")
        return mytext
    def play_sound(self):




        pygame.mixer.music.load("a.mp3")
        pygame.mixer.music.play()
        # playsound('a.mp3')
        # pygame.mixer.music.stop()
        # pygame.mixer.quit()
        # time.sleep(1)

    def delete_file(self):
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        os.remove('a.mp3')





# dd=voice_call()
# #dd.speak("where are you",'ar')#Arabic
# #dd.speak("how are you",'zh-tw')#chinese
# #dd.speak("whats your name",'hi')#Hindi
# #dd.speak("how are you",'ta')#Tamil
# dd.speak("where are you",'ml')#Malayalam
#
# playsound('a.mp3')
