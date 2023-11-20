import streamlit as st
from dotenv import load_dotenv
import threading
from openai import OpenAI

# load_dotenv()
client = OpenAI()

new_clipboard_text = ""
warning = ""

class TimeOutException(Exception):
    pass

def word_count(text):
    num_of_words = len(text.split())
    return num_of_words

def gpt3_rhyme(clipboard_text, temperature, api_key):
    OpenAI.api_key = api_key
    new_clipboard_text = gpt3_meter(clipboard_text, temperature, api_key)
    sys_message = f"""
    
        # MISSION
        The goal is to rewrite the given text to match the reference poem's Rhyme Pattern while maintaining the Choice of Meter, the meaning and emotional depth.
        
        # REFERENCE POEM
        {clipboard_text}

        # INSTRUCTION
        - Analyze the Rhyme Scheme in the reference poem and rewrite the text accordingly.
        - AS MUCH AS POSSIBLE keep the Statement (Subject matter and theme), Setting, Voice, Rhythm (Choice of Meter), Rhyme, and Tone of the poem.
        - Use your entire vocabulary, including synonyms, sophisticated and rare words.

        # RULES
        - You MUST MAKE THE POEM RHYME in the same pattern (same lines, places, and stanzas) even if it slyghtly changes the meaning.
        - DO NOT CHANGE THE POEM'S METER (rhythm and number of syllables).

        # OUTPUT FORMAT
        - Output only the poem in the same format you were given."""
    
    max_retry = 5
    retry = 0
    while True: 
        try:
            print('\nRhyming...\n')
            response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {
                "role": "system",
                "content": sys_message
                },
                {
                "role": "user",
                "content": new_clipboard_text
                }
            ],
            temperature=temperature,
            max_tokens=1000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )
            # print(sys_message)
            print(response.choices[0].message.content)
            return response.choices[0].message.content
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                print(f'\n\nError communicating with OpenAI: "{oops}"')
                response = "@#$%^&*()Warning: error communicating with OpenAI."


def gpt3_meter(clipboard_text, temperature, api_key):
    OpenAI.api_key = api_key
    new_clipboard_text = gpt3_translate(clipboard_text, api_key)
    sys_message = f"""
    
        # MISSION
        The goal is to adjust the Choice of Meter of the text to ensure that the rhythm is consistent with the reference poem.        
        
        # REFERENCE POEM
        {clipboard_text}

        # INSTRUCTION
        - Analyze the Choice of Meter in the reference poem and adjust the rhythm accordingly to closely match the reference poem.
        - Repeat the process for each line, ensuring that the syllable count is as close as possible to the original, maintaining the poem's rhythm and flow.
        - Use your entire vocabulary, including synonyms, sophisticated and rare words.
        - AS MUCH AS POSSIBLE keep the Statement (Subject matter and theme), Setting, Voice, Rhythm (Choice of Meter), Rhyme, and Tone of the poem.

        # RULES
        - YOU MUST MAKE THE POEM IN THE SAME METER (rhythm and number of syllables) even if it slyghtly changes the meaning.

        # OUTPUT FORMAT
        - Output only the poem in the same format you were given.
        """
    
    max_retry = 5
    retry = 0
    while True: 
        try:
            print('\nAdjusting meter...\n')
            response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {
                "role": "system",
                "content": sys_message
                },
                {
                "role": "user",
                "content": new_clipboard_text
                }
            ],
            temperature=temperature,
            max_tokens=1000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )
            # print(sys_message)
            print(response.choices[0].message.content)
            return response.choices[0].message.content
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                print(f'\n\nError communicating with OpenAI: "{oops}"')
                response = "@#$%^&*()Warning: error communicating with OpenAI."


def gpt3_translate(clipboard_text, api_key):
    OpenAI.api_key = api_key
    max_retry = 5
    retry = 0
    while True:
        try:
            print('\nTranslating...\n')
            response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {
                "role": "system",
                "content": f"""
                
                # MISSION\n
                The goal is to accuratetly translate the poem's meaning to English, preserving its content and emotions.\n\n
                
                # INPUT\n
                - The user will give you input of a poem.\n\n
                
                # INSTRUCTIONS\n
                - Prefer exact meaning of translation over rhymes.\n\n
                
                # OUTPUT FORMAT\n
                - Output only the translated poem in the same format you were given."""
                },
                {
                "role": "user",
                "content": clipboard_text
                }
            ],
            temperature=0,
            max_tokens=1000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )
            print(response.choices[0].message.content)
            return response.choices[0].message.content
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                print(f'\n\nError communicating with OpenAI: "{oops}"') 
                response = "@#$%^&*()Warning: error communicating with OpenAI."


def run_with_timeout(func, args=(), kwargs={}, timeout_duration=100):
    class FuncThread(threading.Thread):
        def __init__(self):
            super().__init__()
            self.result = None
            self.exception = None

        def run(self):
            try:
                self.result = func(*args, **kwargs)
            except Exception as e:
                self.exception = e

    func_thread = FuncThread()
    func_thread.start()
    func_thread.join(timeout_duration)
    if func_thread.is_alive():
        func_thread.join()  # Make sure thread has finished before raising exception
        raise TimeOutException("Function did not complete within the timeout period")
    if func_thread.exception:
        raise func_thread.exception
    return func_thread.result


def translate_poem(clipboard_text, temperature):
    count = word_count(clipboard_text)

    if count > 700:
        warning = "@#$%^&*()Warning: The text is too long."
        return warning
    elif count < 1:
        warning = "@#$%^&*()Warning: The text is too short."
        return warning
    else:
        try:
            text = run_with_timeout(gpt3_rhyme, args=(clipboard_text, temperature, api_key,), timeout_duration=100)
            if not text:
                warning = "@#$%^&*()Error: Failed to get response from OpenAI."
                return warning
            return text
        except TimeOutException as e:
            print(f"@#$%^&*()Error: {e}")
            warning = "@#$%^&*()Error: Failed to get response from OpenAI."
            return warning
        except Exception as e:
            print(f"@#$%^&*()Error: {e}")
            warning = "@#$%^&*()Error: Failed to get response from OpenAI."
            return warning


# Streamlit application layout
st.title("📜 Poem Translator")

# Label
st.markdown("#### *GPT-4 attempt of matching original rhyme and meter.*")
# st.markdown("Tip: Try several times and combine the best results.")

# Multiline text input field
clipboard_text = st.text_area("Enter poem to translate:", height=350)

# Layout for slider and password input
col1, col2 = st.columns(2)
with col1:
    temperature = st.slider("Creativity", min_value=0.0, max_value=1.0, value=0.25)
with col2:
    api_key = st.text_input("Enter your OpenAI API Key:", type="password")

st.caption('_Tip: Run several times and combine the best takes._')

# Submit button and result display
if st.button("Translate Poem"):
    if clipboard_text and api_key:
        # Display an informational message
        with st.spinner("Translating your poem..."):
            translation = translate_poem(clipboard_text, temperature)

        st.markdown("### Translated Poem:")
        # Display the result using st.text
        st.text(translation)
    else:
        if not clipboard_text:
            st.warning("Please enter a poem to translate.")
        if not api_key:
            st.warning("Please enter your OpenAI API Key.")
