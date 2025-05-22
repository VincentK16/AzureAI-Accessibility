import streamlit as st
import azure.cognitiveservices.speech as speechsdk
import tempfile
import requests

# Azure Speech config (replace with your keys)
AZURE_SPEECH_KEY = "your Azure Speech key"
AZURE_SPEECH_REGION = "your Azure Speech region"

# Azure Translator config (replace with your key/region)
AZURE_TRANSLATOR_KEY = "<your Azure Translator key>"
AZURE_TRANSLATOR_REGION = "<Azure Translator Region>"
AZURE_TRANSLATOR_ENDPOINT = "https://api.cognitive.microsofttranslator.com"

# Azure OpenAI config (replace with your keys and deployment info)
AZURE_OPENAI_KEY = "<your Azure OpenAI key>"
AZURE_OPENAI_ENDPOINT = "<your Azure OpenAI endpoint"
AZURE_OPENAI_DEPLOYMENT = "<your Azure OpenAI deployment name>"
AZURE_OPENAI_API_VERSION = "2023-05-15"

# Azure Computer Vision config (replace with your key/endpoint)
AZURE_VISION_KEY = "<your Azure Computer Vision key>"
AZURE_VISION_ENDPOINT = "<your Azure Computer Vision endpoint>"

# Voice options for each language
VOICE_OPTIONS = {
    "English": [
        ("en-US-JennyNeural", "Jenny (US Female)"),
        ("en-US-GuyNeural", "Guy (US Male)")
    ],
    "Malay": [
        ("ms-MY-YasminNeural", "Yasmin (MY Female)"),
        ("ms-MY-OsmanNeural", "Osman (MY Male)")
    ],
    "Japanese": [
        ("ja-JP-NanamiNeural", "Nanami (JP Female)"),
        ("ja-JP-KeitaNeural", "Keita (JP Male)")
    ],
    "Chinese": [
        ("zh-CN-XiaoxiaoNeural", "Xiaoxiao (CN Female)"),
        ("zh-CN-YunyangNeural", "Yunyang (CN Male)")
    ],
    "Korean": [
        ("ko-KR-SunHiNeural", "SunHi (KR Female)"),
        ("ko-KR-InJoonNeural", "InJoon (KR Male)")
    ],
    "Tagalog": [
        ("fil-PH-BlessicaNeural", "Blessica (PH Female)"),
        ("fil-PH-AngeloNeural", "Angelo (PH Male)")
    ],
    "Arabic": [
        ("ar-EG-SalmaNeural", "Salma (EG Female)"),
        ("ar-SA-HamedNeural", "Hamed (SA Male)")
    ]
}

TRANSLATE_LANGS = {
    "English": "en",
    "Malay": "ms",
    "Japanese": "ja",
    "Chinese": "zh-Hans",
    "Korean": "ko",
    "Tagalog": "tl",
    "Arabic": "ar"
}

st.title("Text to Speech with Azure AI Speech")

# Add session state for text input and OpenAI answer
if "input_text" not in st.session_state:
    st.session_state.input_text = ""
if "openai_answer" not in st.session_state:
    st.session_state.openai_answer = ""
if "openai_translated" not in st.session_state:
    st.session_state.openai_translated = ""

def recognize_from_microphone():
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    st.info("Listening... Please speak into your microphone.")
    result = speech_recognizer.recognize_once()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        st.success("Recognized: " + result.text)
        st.session_state.input_text = result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        st.warning("No speech could be recognized.")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        st.error(f"Speech Recognition canceled: {cancellation_details.reason}\n{cancellation_details.error_details}")

# Microphone input button
if st.button("🎤 Speak (Speech to Text)"):
    recognize_from_microphone()

text = st.text_area("Enter text to read aloud or translate:", value=st.session_state.input_text)

language = st.selectbox("Select language for speech", list(VOICE_OPTIONS.keys()))
voice = st.selectbox("Select voice", VOICE_OPTIONS[language], format_func=lambda x: x[1])

translate_to = st.selectbox("Translate to", list(TRANSLATE_LANGS.keys()))
translated_text = st.empty()

# --- Azure OpenAI Search Section ---
st.header("Search with Azure OpenAI")
openai_query = st.text_input("Ask a question or search for information:")
if st.button("Search with Azure OpenAI"):
    if not openai_query.strip():
        st.warning("Please enter a question or search query.")
    else:
        headers = {
            "api-key": AZURE_OPENAI_KEY,
            "Content-Type": "application/json"
        }
        endpoint = f"{AZURE_OPENAI_ENDPOINT}openai/deployments/{AZURE_OPENAI_DEPLOYMENT}/chat/completions?api-version={AZURE_OPENAI_API_VERSION}"
        data = {
            "messages": [
                {"role": "system", "content": "You are an AI assistant that helps users find information."},
                {"role": "user", "content": openai_query}
            ],
            "max_tokens": 512,
            "temperature": 0.7
        }
        response = requests.post(endpoint, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            st.session_state.openai_answer = answer
            st.session_state.openai_translated = ""  # reset translation
        else:
            st.error(f"OpenAI request failed: {response.text}")

# Show OpenAI result if available
if st.session_state.openai_answer:
    st.text_area("Azure OpenAI Result:", value=st.session_state.openai_answer, height=150, key="openai_result")

# --- Unified Translation and TTS Controls ---
def do_translate(text_to_translate):
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_TRANSLATOR_KEY,
        "Ocp-Apim-Subscription-Region": AZURE_TRANSLATOR_REGION,
        "Content-type": "application/json"
    }
    params = {
        "api-version": "3.0",
        "to": TRANSLATE_LANGS[translate_to]
    }
    body = [{"text": text_to_translate}]
    response = requests.post(
        f"{AZURE_TRANSLATOR_ENDPOINT}/translate",
        params=params,
        headers=headers,
        json=body
    )
    if response.status_code == 200:
        result = response.json()
        return result[0]["translations"][0]["text"]
    else:
        st.error(f"Translation failed: {response.text}")
        return ""

def do_tts(text_to_speak):
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
    speech_config.speech_synthesis_voice_name = voice[0]
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        audio_config = speechsdk.audio.AudioOutputConfig(filename=f.name)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        result = synthesizer.speak_text_async(text_to_speak).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            st.audio(f.name, format="audio/wav")
        else:
            error_msg = f"Speech synthesis failed. Reason: {result.reason}"
            if result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                error_msg += f"\nError details: {cancellation_details.error_details}"
            st.error(error_msg)

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Translate"):
        # Prefer OpenAI result if available, else use main text
        source_text = st.session_state.openai_answer if st.session_state.openai_answer else text
        translated = do_translate(source_text)
        st.session_state.openai_translated = translated
        translated_text.text_area("Translated text:", value=translated, height=100)
with col2:
    if st.button("Read Aloud"):
        # Prefer OpenAI result if available, else use main text
        source_text = st.session_state.openai_answer if st.session_state.openai_answer else text
        do_tts(source_text)
with col3:
    if st.button("Read Translated Aloud"):
        # Prefer translated OpenAI result if available, else translate main text
        if st.session_state.openai_translated:
            do_tts(st.session_state.openai_translated)
        else:
            # If not translated yet, translate and speak
            source_text = st.session_state.openai_answer if st.session_state.openai_answer else text
            translated = do_translate(source_text)
            st.session_state.openai_translated = translated
            translated_text.text_area("Translated text:", value=translated, height=100)
            do_tts(translated)

# --- Azure Computer Vision Section ---
st.header("Describe an Image with Azure Computer Vision")
image_url = st.text_input("Paste an image URL to describe:")
vision_result = st.empty()

if "image_caption" not in st.session_state:
    st.session_state.image_caption = ""
if "image_caption_translated" not in st.session_state:
    st.session_state.image_caption_translated = ""

if st.button("Describe Image"):
    if not image_url.strip():
        st.warning("Please enter an image URL.")
    else:
        vision_api_url = f"{AZURE_VISION_ENDPOINT}vision/v3.2/analyze"
        params = {
            "visualFeatures": "Description"
        }
        headers = {
            "Ocp-Apim-Subscription-Key": AZURE_VISION_KEY,
            "Content-Type": "application/json"
        }
        data = {"url": image_url}
        response = requests.post(vision_api_url, headers=headers, params=params, json=data)
        if response.status_code == 200:
            result = response.json()
            if "description" in result and "captions" in result["description"] and result["description"]["captions"]:
                caption = result["description"]["captions"][0]["text"]
                st.session_state.image_caption = caption
                st.session_state.image_caption_translated = ""  # reset translation
                vision_result.success(f"Image description: {caption}")
            else:
                vision_result.warning("No description found for this image.")
                st.session_state.image_caption = ""
                st.session_state.image_caption_translated = ""
        else:
            vision_result.error(f"Vision API failed: {response.text}")
            st.session_state.image_caption = ""
            st.session_state.image_caption_translated = ""

# Show image description if available
if st.session_state.image_caption:
    st.text_area("Image Description:", value=st.session_state.image_caption, height=100, key="img_desc")

    img_col1, img_col2, img_col3 = st.columns(3)
    with img_col1:
        if st.button("Translate Image Description"):
            translated = do_translate(st.session_state.image_caption)
            st.session_state.image_caption_translated = translated
            st.text_area("Translated Image Description:", value=translated, height=100, key="img_desc_translated")
    with img_col2:
        if st.button("Read Image Description Aloud"):
            do_tts(st.session_state.image_caption)
    with img_col3:
        if st.button("Read Translated Image Description Aloud"):
            if st.session_state.image_caption_translated:
                do_tts(st.session_state.image_caption_translated)
            else:
                translated = do_translate(st.session_state.image_caption)
                st.session_state.image_caption_translated = translated
                st.text_area("Translated Image Description:", value=translated, height=100, key="img_desc_translated")
                do_tts(translated)
