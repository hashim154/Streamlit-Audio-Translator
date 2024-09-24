import streamlit as st
import azure.cognitiveservices.speech as speechsdk
import requests
import time
from PIL import Image

# Custom CSS for the webpage
st.markdown("""
    <style>

    .absolute-image {
        position: absolute;
        top: 20px; /* Set your desired top position */
        left: 20px; /* Set your desired left position */
        width: 100px; /* Width of the image */
        height: 200px; /* Height of the image */
    }        

        /* Background color and font styles */
        body {
            background-color: #181818; /* Dark background */
            color: #fff; /* White text */
            font-family: 'Arial', sans-serif;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }
        /* Title styling */
        .title {
            font-size: 3rem;
            font-weight: bold;
            color: #FF5733; /* Orange */
            text-align: center;
            margin-bottom: 20px;
        }
        /* Subheader styling */
        .subheader {
            color: #fff; /* White text */
            font-size: 1.2rem;
            text-align: center;
            margin-bottom: 20px;
        }
        /* Upload button styling */
        .stFileUploader {
            text-align: center;
        }
        .css-1m6pqlz {
            border: 2px dashed #FF5733;
            padding: 20px;
            border-radius: 10px;
            background-color: #f8f8f8;
        }
        /* Button styling */
        .css-1offfwp {
            background-color: #FF5733;
            color: white;
        }
        /* Footer design */
        footer {
            position: relative;
            bottom: 0;
            width: 100%;
            text-align: center;
            padding: 10px;
            background-color: #FF5733; /* Orange background */
            color: white;
        }
        /* Logo styling */
        .logo {
            position: absolute;
            top: 0px;
            left: 0px;
            width: 100px;
            height: 100px;
        }
        /* Subheader text styling */
        .subheader-text {
            color: #fff; /* White text */
        }

    </style>
""", unsafe_allow_html=True)

# Display the header for the app
st.markdown('<div class="title">KloudStack Audio Translator</div>', unsafe_allow_html=True)

# Add a logo (you'll need to provide a logo image path)

# Display the logo with an ID using HTML
# st.image("logo.png", width=100, use_column_width=False)

# Instructional text or subheader (in white)
st.markdown('<div class="subheader"><div class="subheader-text">Upload an Arabic audio file to transcribe and translate to the language of your choice.</div></div>', unsafe_allow_html=True)

# Function to translate Arabic text to English (or another language)
def translate_to_english(text, subscription_key, region):
    translation_endpoint = f"https://{region}.api.cognitive.microsofttranslator.com/translate?api-version=3.0&to=en"
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Ocp-Apim-Subscription-Region': region,
        'Content-Type': 'application/json'
    }
    body = [{'text': text}]
    
    response = requests.post(translation_endpoint, headers=headers, json=body)
    if response.status_code == 200:
        translations = response.json()
        return translations[0]['translations'][0]['text']
    else:
        return "Translation Error: {}".format(response.status_code)

# Function to perform continuous speech recognition and translation from an audio file
def recognize_from_audio_file_continuous(audio_file_path, speech_key, speech_region, target_language):
    # Set up speech translation config
    speech_translation_config = speechsdk.translation.SpeechTranslationConfig(subscription=speech_key, region=speech_region)
    speech_translation_config.speech_recognition_language = "ar-AE"  # Recognize Arabic
    
    # Set the target language for translation
    speech_translation_config.add_target_language(target_language)
    
    # Use the audio file instead of microphone input
    audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
    
    # Create translation recognizer
    translation_recognizer = speechsdk.translation.TranslationRecognizer(translation_config=speech_translation_config, audio_config=audio_config)
    
    st.write("Processing audio file: {}".format(audio_file_path))
    
    full_transcription = []
    full_translation = []

    def recognized_cb(evt):
        if evt.result.reason == speechsdk.ResultReason.TranslatedSpeech:
            full_transcription.append(evt.result.text)
            full_translation.append(evt.result.translations[target_language])
            st.write("Transcribed Arabic Text: {}".format(evt.result.text))
            st.write(f"Translated to {target_language.upper()}: {evt.result.translations[target_language]}")
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            st.write("No speech could be recognized.")

    def stop_cb(evt):
        st.write("Recognition has stopped.")
    
    translation_recognizer.recognized.connect(recognized_cb)
    translation_recognizer.session_stopped.connect(stop_cb)
    translation_recognizer.canceled.connect(stop_cb)

    # Start the continuous recognition
    translation_recognizer.start_continuous_recognition()

    # Wait for the recognition to complete
    done = False
    def stop_cb(evt):
        nonlocal done
        done = True
    
    translation_recognizer.session_stopped.connect(stop_cb)
    translation_recognizer.canceled.connect(stop_cb)

    while not done:
        time.sleep(1)

    # Once complete, display the final transcription and translation
    transcribed_text = ' '.join(full_transcription)
    translated_text = ' '.join(full_translation)
    st.write(f"Final Transcribed Arabic Text: {transcribed_text}")
    st.write(f"Final Translated Text ({target_language.upper()}): {translated_text}")

# Add language selection for translation
target_language = st.selectbox("Select the language to translate to", ['en', 'it', 'fr', 'es', 'de'])  # You can add more languages here

# File uploader section
uploaded_file = st.file_uploader("Select an Arabic wav file to upload")

if uploaded_file:
    try:
        # Read the uploaded audio file and play it in the app
        audio_bytes = uploaded_file.read()
        st.audio(audio_bytes, format='audio/wav')
        
        # Save the uploaded file temporarily
        with open('./uploaded_audio.wav', 'wb') as f:
            f.write(audio_bytes)
        
        # Add your Azure Translator and Speech API key and region here
        speech_key = 'ac6d86ea42eb4e76bcf82cf62fd08336'  # Replace with your Azure Speech API key
        speech_region = 'uksouth'  # Replace with your Azure region
        translation_key = '80fbcbfc29c9433f98157066d4f5ea58'  # Replace with your Azure Translation key (if needed)
        translation_region = 'eastus'  # Replace with your Translator API region
        
        
        # Perform continuous speech recognition and translation
        recognize_from_audio_file_continuous('./uploaded_audio.wav', speech_key, speech_region, target_language)
        
    except Exception as e:
        st.write("Error processing the audio file. Please ensure it's a valid wav file. Error: {}".format(e))

# Footer section
st.markdown('<footer>© 2024 KloudStack Audio Translator</footer>', unsafe_allow_html=True)
