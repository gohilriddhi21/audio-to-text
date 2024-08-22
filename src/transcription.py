"""Transcribe Audio Files. Audio-to-Text."""
import os
import sys
import logging
from tempfile import TemporaryDirectory
from pydub import AudioSegment
from pydub.silence import split_on_silence
import speech_recognition as sr

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def transcribe_audio(chunks):
    """Transcribes a list of audio chunks using Google's Speech Recognition API."""
    recognizer = sr.Recognizer()
    full_text = []
    with TemporaryDirectory() as temp_dir:
        for i, chunk in enumerate(chunks):
            text = ""
            chunk_filename = os.path.join(temp_dir, f"chunk_{i}.wav")
            try:
                chunk.export(chunk_filename, format="wav")
                with sr.AudioFile(chunk_filename) as source:
                    audio = recognizer.record(source)
                text = recognizer.recognize_google(audio)
                full_text.append(text)
            except sr.UnknownValueError:
                full_text.append("...")
            except sr.RequestError as e:
                logger.error("Could not request results from the speech recognition service: %s", e)
            except Exception as e: #pylint: disable=broad-except
                logger.error("Failed to process chunk %d: %s", i, e)
            finally:
                logger.debug("Chunk %d: %s", i, text)
    return full_text


def split_audio(wav_file, min_silence_len=300, silence_thresh=-35):
    """Splits an audio file into chunks based on periods of silence."""
    try:
        logger.info("Chunking audio file...This might take a few minutes...")
        audio = AudioSegment.from_wav(wav_file)
        chunks = split_on_silence(audio,
                                  min_silence_len=min_silence_len,
                                  silence_thresh=silence_thresh,
                                  keep_silence=500)
        if not chunks:
            raise ValueError("No chunks were generated.")
        logger.info("Audio file split into %d chunks.", len(chunks))
        return chunks
    except Exception as e: #pylint: disable=broad-except
        logger.error("Failed to split %s into chunks: %s", wav_file, e)
        sys.exit()


def convert_audio(mp3_file, output_dir="wav_files", output_format="wav"):
    """Converts an MP3 file to the specified format and saves it to the specified directory."""
    try:
        file_name = os.path.basename(mp3_file).replace(".mp3", f".{output_format}")
        output_file = os.path.join(output_dir, file_name)
        if not os.path.exists(output_file):
            os.makedirs(output_dir, exist_ok=True)
            audio = AudioSegment.from_file(mp3_file)
            audio.export(output_file, format=output_format)
        return output_file
    except Exception as e: #pylint: disable=broad-except
        logger.error("Failed to convert %s: %s", mp3_file, e)
        sys.exit()


def convert_split_transcribe_audio(audio_file):
    """Converts .mp3 to .wav, splits it into chunks, and transcribes each chunk."""
    output_file = convert_audio(audio_file)
    if not output_file:
        logger.error("Failed to convert %s to %s", audio_file, "wav")
        return None

    chunks = split_audio(output_file)
    if not chunks:
        logger.error("No chunks were generated for %s", output_file)
        return None

    transcribed_text = transcribe_audio(chunks)
    if not transcribed_text:
        logger.error("Transcription failed for %s", output_file)
        return None

    logger.debug("Transcribed text: %s", transcribed_text)
    return transcribed_text


def process_audio_files_in_directory(audio_files_dir, transcribed_files_dir):
    """Processes all audio files in a directory."""
    for file_name in os.listdir(audio_files_dir):
        if file_name.endswith(".mp3"):
            audio_file = os.path.join(audio_files_dir, file_name)
            logger.info("Processing %s", audio_file)
            transcribed_text = convert_split_transcribe_audio(audio_file)
            if transcribed_text:
                os.makedirs(transcribed_files_dir, exist_ok=True)
                file_name = os.path.splitext(file_name)[0] + ".txt"
                output_file = os.path.join(transcribed_files_dir, file_name)
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write("Transcribed Text: \n")
                    for line in transcribed_text:
                        f.write(line + " ")
                logger.info("Transcription saved to %s", output_file)
            else:
                logger.error("Failed to transcribe %s", audio_file)


if __name__ == "__main__":
    AUDIO_FILES_DIR = "audio_files"
    TRANSCRIBED_FILES_DIR = "transcribed_text_files"
    process_audio_files_in_directory(AUDIO_FILES_DIR, TRANSCRIBED_FILES_DIR)
