import cohere
import fitz
import re
import random
import streamlit as st

co = cohere.Client('IP4Hkb6LxjrGuHpke3CJlyVeJx3rWwfDd2SNiPVG')

def get_script(text, conversation_id=None):
    prompt = f'''You are an AI screenplay writer tasked with organizing the "script" into scenes based on the below provided format:

###format###
Scenes: Scene Number
Characters: Provide a list of characters involved in the scene along with brief descriptions (age, personality traits, etc.)
Props: List any important props or objects used in the scene
Location: Specify the location where the scene takes place (interior/exterior, specific setting)
Dialogue: Include snippets of dialogue between the characters, identified by character name
Action: Describe the key actions, movements, and events that occur in the scene.

###sample###
Scene 1: EXT. DM SCHOOL - MORNING
Characters: Max (18): Timid, avoids eye contact, terrified of dogs. Shane (16 to 18): More outgoing, interacts with the dog. Owner (30+): Holds the dog on a leash, interacts with Shane. Small Dog: Reacts to the boys, snarls.
Props: AirPods: Worn by Max. Backpacks: Carried by Max and Shane. Leash: Used by the Owner for the dog.
Location: Exterior of DM School.
Dialogue: Owner: "Is he okay?" Shane: "Oh yeah. My brother Max is really scared of dogs because he got bit when he was little. Well, he's pretty much scared of everything."
Action: Max sees a small dog, gets terrified, and runs away. Shane approaches the dog and owner, asks if he can pet the dog, and does so.

###script###
{text}

###Instructions###
The script should be formatted similarly to the sample, and MUST INCLUDE Characters, Props, Location, Dialogue, and Action. Pay close attention to the level of detail provided in the sample for each section. The overall tone and writing style should match the sample script. You MUST organize all scenes(from 1 to 22) in one go.
'''
    if conversation_id is None:
        conversation_id = str(random.randint(1, 1000000000))

    response = co.chat(model="command-r-plus", message=prompt, conversation_id=conversation_id)
    org_script = response.text
    return org_script, conversation_id

def st_ui():
    st.title("Screenplay Script Generator")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if 'generated_script' not in st.session_state:
        st.session_state['generated_script'] = ''
    if 'continued_script' not in st.session_state:
        st.session_state['continued_script'] = ''
    if 'conversation_id' not in st.session_state:
        st.session_state['conversation_id'] = None

    if uploaded_file is not None:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            page_text = page.get_text()
            page_text = page_text.replace('\n', ' ')
            page_text = re.sub(r'\s+', ' ', page_text)
            text += page_text

        if st.button("Generate Script"):
            org_script, st.session_state['conversation_id'] = get_script(text)
            st.session_state['generated_script'] = org_script
            st.session_state['continued_script'] = ''  # Clear the continued_script

        st.write(st.session_state['generated_script'])

        continue_button = st.empty()

        if st.session_state['conversation_id']:
            with continue_button:
                if st.button("Continue"):
                    cont_response = co.chat(model="command-r-plus", message="continue", conversation_id=st.session_state['conversation_id'])
                    st.session_state['continued_script'] += cont_response.text
                    st.write(st.session_state['continued_script'])

if __name__ == "__main__":
    st_ui()