import streamlit as st # type: ignore
from difflib import SequenceMatcher
import pdfplumber # type: ignore
from docx import Document # type: ignore
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def apply_custom_css():
    st.markdown("""
<style>
    body {
        font-family: 'Courier New', Courier, monospace;
        margin: 0;
        padding: 0;
    }

    h1, h2, h3 {
        font-family: 'Roboto', sans-serif;
        font-weight: 600;
    }

    .script-container {
        font-family: 'Courier New', Courier, monospace;
        white-space: pre-wrap;
        font-size: 16px;
        line-height: 1.8;
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #ddd;
        max-width: 100%;
        overflow-wrap: break-word;
        margin-bottom: 25px;
        box-shadow: 0px 10px 15px rgba(0, 0, 0, 0.05);
        transition: box-shadow 0.3s ease;
    }

    .script-container:hover {
        box-shadow: 0px 10px 25px rgba(0, 0, 0, 0.15);
    }

    .dialogue {
        margin-left: 40px;
    }

    .character {
        font-weight: bold;
        color: #2a5d84;
    }

    .action {
        font-style: italic;
        color: #6a6a6a;
    }

    .center-dialogue {
        text-align: center;
        margin-left: -5px;
        font-style: italic;
        color: #005f77;
    }

    .stTextArea textarea {
        font-family: 'Roboto', sans-serif;
        font-size: 16px;
        line-height: 1.8;
        width: 100%;
        height: 300px;
        padding: 12px;
        border-radius: 12px;
        border: 1px solid #ccc;
        background-color: #ffffff;
        color: #333;
        resize: vertical;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }

    .stTextArea textarea:focus {
        border-color: #005f77;
        box-shadow: 0 0 5px rgba(0, 95, 119, 0.4);
    }

    .download-btn-container {
        margin-top: 20px;
        text-align: center;
    }
    
.radio-container {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 0 0 20px 0;  /* No top margin */
    position: relative;
    top: -100px;  /* Moves the element 30px up */
}
#root > div:nth-child(1) > div.withScreencast > div > div > section > div.stMainBlockContainer.block-container.st-emotion-cache-13ln4jf.ea3mdgi5 > div > div > div > div:nth-child(6) > div > label {
    display: none;
}

#root > div:nth-child(1) > div.withScreencast > div > div > section > div.stMainBlockContainer.block-container.st-emotion-cache-13ln4jf.ea3mdgi5 > div > div > div > div:nth-child(5) {
    display: none;
}

}

.radio-container label {
    margin-right: 10px;
    font-weight: 500;
    color: #333;
}

.radio-container input[type="radio"] {
    accent-color: #005f77;
    margin: 0 10px;
    transition: transform 0.3s ease-in-out;
}

.radio-container input[type="radio"]:hover {
    transform: scale(1.1);
}

.radio-container input[type="radio"]:checked + label {
    color: #005f77;
    font-weight: 600;
}

.radio-container input[type="radio"]:not(:checked) + label:hover {
    color: #007a94;
}

.radio-container input[type="radio"]:checked {
    background-color: #005f77;
    border-radius: 50%;
    padding: 5px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
}

    .download-btn-container button {
        background-color: #005f77;
        color: white;
        padding: 12px 20px;
        font-size: 16px;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }

    .download-btn-container button:hover {
        background-color: #003f53;
    }
    #rescript{
        color: #2a5d84;
        text-align:center;
        margin-top:-30px}
    #root > div:nth-child(1) > div.withScreencast > div > div > section > div.stMainBlockContainer.block-container.st-emotion-cache-13ln4jf.ea3mdgi5 > div > div > div > div:nth-child(10) {
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
    margin: 0 auto;
}
    #root > div:nth-child(1) > div.withScreencast > div > div > section > div.stMainBlockContainer.block-container.st-emotion-cache-13ln4jf.ea3mdgi5 > div > div > div > div:nth-child(14) > div{
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
    margin: 0 auto;  }

    @media (max-width: 768px) {
        .script-container {
            padding: 15px;
        }

        .stTextArea textarea {
            height: 250px;
        }

        .radio-container {
            flex-direction: column;
            align-items: flex-start;
        }

        .download-btn-container {
            margin-top: 15px;
            
        }
    }

    </style>
    """, unsafe_allow_html=True)

def read_file(uploaded_file):
    content = None
    if uploaded_file.name.endswith('.txt'):
        content = uploaded_file.read().decode('utf-8')
    elif uploaded_file.name.endswith('.pdf'):
        with pdfplumber.open(uploaded_file) as pdf:
            content = ''.join([page.extract_text() for page in pdf.pages if page.extract_text()])
    elif uploaded_file.name.endswith('.docx'):
        doc = Document(uploaded_file)
        content = '\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
    else:
        st.write(f"Unsupported file type for {uploaded_file.name}. Please upload a .txt, .pdf, or .docx file.")
    return content


def choose_best_parts(scripts):
    optimized_script = ""
    dialogues = [script.split("\n") for script in scripts]
    previous_characters = set()
    max_lines = max(len(dialogue_list) for dialogue_list in dialogues)

    for line_index in range(max_lines):
        best_line = ""
        highest_score = 0

        for i in range(len(dialogues)):
            if line_index < len(dialogues[i]):
                line = dialogues[i][line_index]
                if line.strip().isupper():  # Character names in uppercase
                    if line.strip() not in previous_characters:
                        previous_characters.add(line.strip())
                    else:
                        continue
                for j in range(i + 1, len(dialogues)):
                    if line_index < len(dialogues[j]):
                        comparison_line = dialogues[j][line_index]
                        sequence_match = SequenceMatcher(None, line, comparison_line)
                        match_ratio = sequence_match.ratio()
                        if match_ratio > highest_score:
                            highest_score = match_ratio
                            best_line = line if len(line) > len(comparison_line) else comparison_line

        optimized_script += f"\n{best_line}"

    return optimized_script

def format_script(script):
    formatted_script = ""
    lines = script.split("\n")
    first_dialogue = True

    for line in lines:
        if line.strip():
            if line.strip().isupper():  # Character name
                formatted_script += f"<div class='character'>{line.strip()}</div>\n"
            elif line.strip().startswith('(') and line.strip().endswith(')'):  # Action
                formatted_script += f"<div class='action'>{line.strip()}</div>\n"
            else:  # Dialogue
                if first_dialogue:
                    formatted_script += f"<div class='dialogue center-dialogue'>{line.strip()}</div>\n"
                    first_dialogue = False
                else:
                    formatted_script += f"<div class='dialogue'>{line.strip()}</div>\n"
    
    return formatted_script

def main():
    apply_custom_css()
    

    st.title("Script Analyzer and Optimizer")

    st.header("Upload your Scripts")
    uploaded_files = st.file_uploader("Upload your script files", type=['txt', 'pdf', 'docx'], accept_multiple_files=True, label_visibility='hidden')
    
    if uploaded_files:
        scripts = []
        for uploaded_file in uploaded_files:
            content = read_file(uploaded_file)
            if content:
                scripts.append(content)
    

        if scripts:
            optimized_script = choose_best_parts(scripts)
            formatted_script = format_script(optimized_script)

            st.markdown("<div class='radio-container'>", unsafe_allow_html=True)
            mode = st.radio("Select Mode", ["OPTIMIZED SCRIPT", "EDIT"], index=0, label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)


            if mode == "OPTIMIZED SCRIPT":
                st.markdown(f"<div class='script-container'>{formatted_script}</div>", unsafe_allow_html=True)
                st.markdown("<div class='download-btn-container'>", unsafe_allow_html=True)
                st.download_button(
                    label="Download",
                    data=optimized_script,
                    file_name="optimized_script.txt",
                    mime="text/plain"
                )
               

            elif mode == "EDIT":
                st.markdown("<div class='edit-container'>", unsafe_allow_html=True)
                
                st.header("Rescript")
                edited_script = st.text_area("Edit the optimized script", value=optimized_script, height=300, key="edit_area", label_visibility="hidden", help="You can edit the optimized script here.", max_chars=5000, placeholder="Edit your script here...")

                # Live Preview for Edit Mode
                st.markdown(f"<div class='script-container'>{format_script(edited_script)}</div>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("<div class='download-btn-container'>", unsafe_allow_html=True)
                st.download_button(
                    label="Download",
                    data=edited_script,
                    file_name="edited_script.txt",
                    mime="text/plain"
                )
                st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()