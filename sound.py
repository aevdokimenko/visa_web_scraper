import simpleaudio as sa

def play_sound(rep):
    try:
        for _ in range(rep):
            wave_obj = sa.WaveObject.from_wave_file("audio/uti-puti.wav")
            play_obj = wave_obj.play()
            play_obj.wait_done()
    except:
        print("Cannot play sound")
        pass

def test_sound():
    wave_obj = sa.WaveObject.from_wave_file("audio/vot.wav")
    wave_obj.play().wait_done()
