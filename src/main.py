import os
from pydub import AudioSegment
from pydub.silence import split_on_silence
import speech_recognition as sr
import logging 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging = logging.getLogger(__name__)

def transcribe_audio_chunks(chunks):
    """
    Transcribes a list of audio chunks using Google's Speech Recognition API.

    Args:
        chunks (list): A list of AudioSegment objects representing audio chunks.

    Returns:
        str: The transcribed text from all audio chunks.
    """
    recognizer = sr.Recognizer()
    full_text = ""
    chunks_dir = "chunks"
    os.makedirs(chunks_dir, exist_ok=True)

    for i, chunk in enumerate(chunks):
        text = ""
        chunk_filename = os.path.join(chunks_dir, f"chunk_{i}.wav")
        try:
            chunk.export(chunk_filename, format="wav")
            with sr.AudioFile(chunk_filename) as source:
                audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            full_text += text + " "
        except sr.UnknownValueError:
            full_text += "[Unintelligible] "
        except sr.RequestError as e:
            print(f"Could not request results from the speech recognition service; {e}")
        except Exception as e:
            print(f"Failed to process chunk {i}: {e}")
        finally:
            os.remove(chunk_filename)
    return full_text.strip()

def split_audio(wav_file, min_silence_len=500, silence_thresh=-35):
    """
    Splits an audio file into chunks based on periods of silence.

    Args:
        wav_file (str): The path to the input WAV file.
        min_silence_len (int, optional): Minimum length of silence (in milliseconds) to consider for splitting. Defaults to 500.
        silence_thresh (int, optional): Silence threshold (in dB) for splitting. Defaults to -35.

    Raises:
        ValueError: If no chunks are generated from the audio file.

    Returns:
        list: A list of AudioSegment objects representing the audio chunks.
    """
    try:
        print("Chunking audio file...This might take a few minutes...")
        audio = AudioSegment.from_wav(wav_file)
        chunks = split_on_silence(audio,
                                  min_silence_len=min_silence_len,
                                  silence_thresh=silence_thresh,
                                  keep_silence=300)
        if not chunks:
            raise ValueError("No chunks were generated. The audio might be too continuous or the silence threshold is too low.")
        print(f"Audio file split into {len(chunks)} chunks.")
        return chunks
    except Exception as e:
        print(f"Failed to split {wav_file} into chunks: {e}")
        return None


def convert_mp3(mp3_file, output_dir="wav_files", output_format="wav"):
    """Converts an MP3 audio file to the specified format and saves it to the specified directory.

    Args:
        mp3_file (str): The path to the input audio file (.mp3).
        output_dir (str, optional): The directory to save the converted audio file. Defaults to "wav_files".
        output_format (str, optional): The desired output format. Defaults to "wav".

    Returns:
        str: The path to the converted audio file.
    """

    try:
        os.makedirs(output_dir, exist_ok=True)
        audio = AudioSegment.from_file(mp3_file)
        output_file = os.path.join(output_dir, os.path.basename(mp3_file).replace(".mp3", f".{output_format}"))
        if os.path.exists(output_file):
            return output_file
        else:
            audio.export(output_file, format=output_format)
        return output_file
    except Exception as e:
        print(f"Failed to convert {mp3_file}: {e}")
        return None


def extract_text(audio_file):
    """Processes an audio file by converting it to WAV, splitting it into chunks, and transcribing each chunk.

    Args:
        audio_file (str): The path to the audio file.

    Returns:
        str: The transcribed text.
    """

    output_file = convert_mp3(audio_file)
    if output_file:
        chunks = split_audio(output_file)
        if chunks:
            transcribed_text = transcribe_audio_chunks(chunks)
            return transcribed_text
        else:
            print(f"No chunks were generated for {output_file}")
    return "Failed to process audio file"
    
    
    
def process_audio_files_in_directory(audio_files_dir, transcribed_files_dir):
    """Processes all audio files in a directory.

    Args:
        audio_files_dir (str): The path to the directory containing audio files.
        transcribed_files_dir (str): The path to the directory where the transcribed text files will be saved.
    """

    for file_name in os.listdir(audio_files_dir):
        if file_name.endswith(".mp3"):
            audio_file = os.path.join(audio_files_dir, file_name)
            print(f"\nProcessing: {audio_file}")
            transcribed_text = extract_text(audio_file)
            if transcribed_text:
                os.makedirs(transcribed_files_dir, exist_ok=True)
                output_file = os.path.join(transcribed_files_dir, os.path.splitext(file_name)[0] + ".txt")
                with open(output_file, "w") as f:
                    f.write(transcribed_text)
                print(f"Transcription saved to {output_file}")
            else:
                print(f"Failed to transcribe {audio_file}")
    

if __name__ == "__main__":
    audio_files_dir = "audio_files"
    transcribed_files_dir = "transcribed_text_files"
    process_audio_files_in_directory(audio_files_dir, transcribed_files_dir)
