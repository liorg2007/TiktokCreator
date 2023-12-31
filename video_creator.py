import math
import random
from tiktokVoiceMain.tiktokVoiceMain import textToSpeech
from moviepy import editor
import os
import whisper_timestamped as whisper
from pydub import AudioSegment

def makeSpeech(myText, speaker, fileName, max_chunk_size=250):
    # Split text into sentences
    sentences = myText.split(". ")

    # Initialize variables
    chunk_index = 0
    chunk_files = []

    for sentence in sentences:
        # Get the length of the current chunk
        chunk_length = len(sentence)

        # Break down the sentence into smaller chunks
        for start_index in range(0, chunk_length, max_chunk_size):
            end_index = start_index + max_chunk_size
            chunk = sentence[start_index:end_index]

            # Generate the file name for the current chunk
            chunk_file = f"{fileName}_chunk{chunk_index}.mp3"

            # Use the text-to-speech API to generate the audio for the current chunk
            textToSpeech.tts(session_id="73782eef66d5ab64bf83342be9623375", text_speaker=speaker, req_text=chunk, filename=chunk_file, play=False)

            # Append the current chunk file to the list
            chunk_files.append(chunk_file)

            # Update variables for the next iteration
            chunk_index += 1

    # Combine generated chunks into one audio file
    combine_mp3_files(chunk_files, f"{fileName}_combined.mp3")

    # Delete individual chunk files
    for chunk_file in chunk_files:
        os.remove(chunk_file)

def combine_mp3_files(file_paths, output_file):
    # Initialize an empty audio segment
    combined_audio = AudioSegment.silent()

    # Iterate over each file path
    for file_path in file_paths:
        # Load the current audio file
        audio_chunk = AudioSegment.from_file(file_path, format="mp3")

        # Combine the current audio with the overall combined audio
        combined_audio += audio_chunk

    # Export the combined audio to a new file
    combined_audio.export(output_file, format="mp3")


def getText(directory):
    list = []
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        # checking if it is a file
        if os.path.isfile(f):
            with open(f, 'r') as file:
                list.append(file.read())
    
    return list

def makeSoundFiles(directory, list):
    for i in range(len(list)):
        fileName = f"{directory}/sound{i}.mp3"
        makeSpeech(list[i], "en_us_009", fileName)

def getSubtitleClip(audio):
    model = whisper.load_model("base")
    results = whisper.transcribe(model, audio)
    #adding subtitles
    subs = []
    for segment in results["segments"]:
        for word in segment["words"]:
            text = word["text"].upper()
            start = word["start"]
            end = word["end"]
            duration= end - start
            txt_clip = editor.TextClip(txt=text, fontsize=40, font="Arial-Bold", stroke_width=2, stroke_color="white", color = "white")
            txt_clip = txt_clip.set_start(start).set_duration (duration).set_pos(("center","center"))
            subs.append(txt_clip)
    return subs

def trimVideosAndEdit():
    i = 0
    soundDir = "Sounds"

    number = random.randint(1, 4)

    video = editor.VideoFileClip(f"OriginVideos/video{number}.mp4")
    video = video.without_audio()

    for filename in os.listdir(soundDir):
        f = os.path.join(soundDir, filename)
        audio = editor.AudioFileClip(f)
        length = math.ceil(audio.duration)

        random_point = random.randint(0, math.ceil(video.duration))

        new_video = video.subclip(random_point, random_point + length)

        # Get subtitles
        clips = getSubtitleClip(f)

        # Create TextClips for each subtitle

        # Overlay text clips on the video
        final_clip = editor.CompositeVideoClip([new_video] + clips)

        # Load background music
        number = random.randint(1, 3)
        background_music = editor.AudioFileClip(f"Music/music{number}.mp3")

        # Ensure background music duration matches speech audio duration
        if background_music.duration > length:
            background_music = background_music.subclip(0, length)
        else:
            # If background music is shorter, loop it to match the length
            background_music = background_music * math.ceil(length / background_music.duration)
        background_music = background_music.volumex(0.1)
        # Composite the audio clips
        final_audio = editor.CompositeAudioClip([audio, background_music])

        # Set the audio of the final clip
        final_clip = final_clip.set_audio(final_audio)

        # Write the final video with subtitles to a file
        final_clip.write_videofile(f"TrimmedVideos/video{i}.mp4", fps=24)  # Many options...
        i += 1


def main():
    list = getText("Texts")
    makeSoundFiles("Sounds", list)

    trimVideosAndEdit()



def createTextFiles(list):
    for i in range(len(list)):
        with open(f"Texts\\text{i}.txt", "w") as f:
            f.write(list[i])

if __name__ == "__main__":
    main()