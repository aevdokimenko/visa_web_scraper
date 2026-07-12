import time

import simpleaudio as sa

def play_sound(rep):
    try:
        for _ in range(rep):
            wave_obj = sa.WaveObject.from_wave_file("audio/uti-puti.wav")
            wave_obj.play().wait_done()
            time.sleep(10)
    except:
        print("Cannot play sound")
        pass

def test_sound(rep = 1):
    wave_obj = sa.WaveObject.from_wave_file("audio/vot.wav")
    for _ in range(rep):
        wave_obj.play()
        time.sleep(5)
