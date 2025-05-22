# Accessibility AI Web App

![image](https://github.com/user-attachments/assets/ea5df7e2-91f9-494b-855c-006ed153c5fc)


This Streamlit web app provides accessible AI-powered features for users, including:
- Text-to-speech in multiple languages and voices (Azure AI Speech)
- Speech-to-text (voice input)
- Translation (Azure Translator)
- Azure OpenAI search and Q&A
- Image description (Azure Computer Vision)
- All outputs can be read aloud or translated for visually impaired users

## Features

- **Text Input:** Type or speak your text, then listen or translate it.
- **Voice Input:** Use your microphone to input text via Azure Speech-to-Text.
- **Translation:** Translate any text, OpenAI result, or image description to your chosen language.
- **Text-to-Speech:** Listen to any text, translation, OpenAI result, or image description in your selected language and voice.
- **Azure OpenAI Search:** Ask questions and get AI-generated answers, which can be read aloud or translated.
- **Image Description:** Paste an image URL to get a description, which can also be read aloud or translated.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/VincentK16/feeltheworldwithAI.git
cd feeltheworldwithA
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Azure Keys

Set your Azure resource keys and endpoints in `app.py`:

- `AZURE_SPEECH_KEY` and `AZURE_SPEECH_REGION`
- `AZURE_TRANSLATOR_KEY` and `AZURE_TRANSLATOR_REGION`
- `AZURE_OPENAI_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_API_VERSION`
- `AZURE_VISION_KEY` and `AZURE_VISION_ENDPOINT`

> **Note:** You need valid Azure resources for Speech, Translator, OpenAI, and Computer Vision.

### 4. Run the app

```bash
streamlit run app.py
```

The app will open in your browser.


## Usage

1. Launch the app as above.
2. Enter or speak your text, or paste an image URL.
3. Use the controls to translate, listen, or get AI answers.
4. Configure language and voice as needed.

---

**For more information on Azure services:**
- [Azure Speech Service](https://learn.microsoft.com/azure/cognitive-services/speech-service/)
- [Azure Translator](https://learn.microsoft.com/azure/cognitive-services/translator/)
- [Azure OpenAI](https://learn.microsoft.com/azure/cognitive-services/openai/)
- [Azure Computer Vision](https://learn.microsoft.com/azure/cognitive-services/computer-vision/)
