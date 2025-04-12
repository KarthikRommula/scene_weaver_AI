import streamlit as st # type: ignore
from difflib import SequenceMatcher
import pdfplumber # type: ignore
from docx import Document # type: ignore
from dotenv import load_dotenv
import os
import boto3
import json
import time

# Load environment variables
load_dotenv()

def apply_custom_css():
    st.markdown("""
<style>
    /* Base styles and typography */
    body {
        font-family: 'Inter', 'Roboto', sans-serif;
        margin: 0;
        padding: 0;
        color: #333;
        line-height: 1.6;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', 'Roboto', sans-serif;
        font-weight: 600;
        color: #2a5d84;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    
    /* Main container responsiveness */
    .main .block-container {
        max-width: 1200px;
        padding-top: 1.5rem;
        padding-right: 1.5rem;
        padding-left: 1.5rem;
        padding-bottom: 1.5rem;
    }
    
    /* App header styling */
    .app-header {
        background: linear-gradient(135deg, #2a5d84 0%, #005f77 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
.app-header {
    text-align: center;
}

.app-header h1 {
    color: white;
    margin: 0;
    font-size: 2.2rem;
    font-weight: 800;
    width: 100%;
}

.app-header p {
    margin: 0.5rem 0 0 0;
    opacity: 0.9;
    font-size: 1rem;
    width: 100%;
}

/* Ensuring both elements have equal width */
.app-header h1,
.app-header p {
    display: block;
    text-align: center;
}


    /* Script container styling */
    .script-container {
        font-family: 'Courier Prime', 'Courier New', monospace;
        white-space: pre-wrap;
        font-size: 16px;
        line-height: 1.8;
        background-color: #ffffff;
        padding: 25px;
        border-radius: 8px;
        border: 1px solid #ddd;
        width: 100%;
        overflow-wrap: break-word;
        margin-bottom: 25px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        min-height: 400px;
    }

    .script-container:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-color: #bbb;
    }

    /* Script elements styling */
    .dialogue {
        margin-left: 40px;
        margin-bottom: 0.5rem;
    }

    .character {
        font-weight: bold;
        color: #2a5d84;
        margin-top: 1rem;
        margin-bottom: 0.25rem;
    }

    .action {
        font-style: italic;
        color: #555;
        margin-bottom: 0.75rem;
    }

    .center-dialogue {
        text-align: center;
        font-style: italic;
        color: #005f77;
        margin: 1rem 0;
    }

    /* Text area styling */
    .stTextArea textarea {
        font-family: 'Courier Prime', 'Courier New', monospace;
        font-size: 16px;
        line-height: 1.8;
        width: 100%;
        padding: 16px;  /* Increased padding */
        border-radius: 8px;
        border: 1px solid #ccc;
        background-color: #ffffff;
        color: #333;
        resize: vertical;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }

    .stTextArea textarea:focus {
        border-color: #005f77;
        box-shadow: 0 0 0 2px rgba(0, 95, 119, 0.2);
        outline: none;
    }

    /* Button styling */
    .stButton>button {
        background-color: #005f77;
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .stButton>button:hover {
        background-color: #004a5e;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        transform: translateY(-1px);
    }
    
    .stButton>button:active {
        transform: translateY(0);
    }
    
    /* Download button container */
    .download-btn-container {
        margin-top: 1rem;
        display: flex;
        justify-content: center;
        gap: 1rem;
    }
    
    /* Card styling */
    .card {
        background-color: white;
        border-radius: 8px;
        padding: 1.8rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.2rem;
        transition: all 0.3s ease;
    }
    
    /* Enhanced Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 0.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 16px;
        border-radius: 6px;
        transition: all 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #005f77 !important;
        color: white !important;
        font-weight: 500;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }
    
    .stTabs [data-baseweb="tab-highlight"] {
        display: none;
    }
    
    .stTabs [data-baseweb="tab-content"] {
        padding: 1.5rem 0.5rem;
    }
    
    .card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
    }
    
    /* Info box styling */
    .info-box {
        background-color: #e8f4f8;
        border-left: 4px solid #005f77;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f5f7f9;
        border-radius: 6px 6px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #e8f4f8;
        border-bottom: 2px solid #005f77;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f5f7f9;
        border-right: 1px solid #eee;
    }
    
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        padding-top: 2rem;
        padding-right: 1rem;
        padding-left: 1rem;
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        font-weight: 600;
        color: #2a5d84;
    }
    
    /* Radio container styling */
    .radio-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0 0 20px 0;
        gap: 10px;
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
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem 0.5rem;
        }
        
        .app-header {
            padding: 1rem;
            margin-bottom: 1rem;
        }
        
        .app-header h1 {
            font-size: 1.8rem;
        }
        
        .script-container {
            padding: 15px;
            font-size: 14px;
        }
        
        .dialogue {
            margin-left: 20px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: auto;
            padding: 8px 12px;
            font-size: 14px;
        }
        
        .stButton>button {
            width: 100%;
        }
        
        .download-btn-container {
            flex-direction: column;
        }
        
        /* Fix sidebar on mobile */
        [data-testid="stSidebar"][aria-expanded="true"] {
            width: 80% !important;
        }
        
        [data-testid="stSidebar"][aria-expanded="false"] {
            margin-left: -100%;
        }
        
        /* Adjust columns for mobile */
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            margin-bottom: 1rem;
        }
        
        /* Fix radio buttons on mobile */
        .radio-container {
            flex-direction: column;
            align-items: flex-start;
        }
    }
    
    /* Fix for streamlit components */
    div[data-testid="stVerticalBlock"] div[style*="flex-direction: column"] {
        gap: 10px;
    }
    
    /* Status indicator styling */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 6px;
    }
    
    .status-success {
        background-color: #28a745;
    }
    
    .status-processing {
        background-color: #ffc107;
    }
    
    .status-error {
        background-color: #dc3545;
    }
    
    /* File uploader styling */
    [data-testid="stFileUploader"] {
        width: 100%;
    }
    
    [data-testid="stFileUploader"] section {
        padding: 1rem;
        border: 2px dashed #ccc;
        border-radius: 8px;
        background-color: #f9f9f9;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"] section:hover {
        border-color: #005f77;
        background-color: #f0f8ff;
    }
    
    /* Fix for specific elements */
    #root > div:nth-child(1) > div.withScreencast > div > div > section > div.stMainBlockContainer.block-container > div > div > div > div:nth-child(10),
    #root > div:nth-child(1) > div.withScreencast > div > div > section > div.stMainBlockContainer.block-container > div > div > div > div:nth-child(14) > div {
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
        margin: 0 auto;
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


def choose_best_parts(scripts, optimization_weights=None):
    """Advanced script optimization algorithm that combines multiple drafts into one cohesive script.
    
    Uses semantic similarity, context awareness, and natural language processing techniques to
    select the best parts from each draft while maintaining narrative consistency.
    
    Args:
        scripts (list): List of script drafts to combine
        optimization_weights (dict, optional): Weights for different scoring factors
            - base_score: Weight for length and detail
            - similarity: Weight for consensus with other drafts
            - context: Weight for narrative continuity
    """
    # Set default weights if none provided
    if optimization_weights is None:
        optimization_weights = {
            "base_score": 0.3,
            "similarity": 0.5,
            "context": 0.2
        }
    
    # Initialize the optimized script and parse each script into lines
    optimized_script = ""
    dialogues = [script.split("\n") for script in scripts]
    
    # Track characters and context for better continuity
    characters = set()
    character_context = {}
    scene_context = []
    previous_line_type = None
    max_lines = max(len(dialogue_list) for dialogue_list in dialogues)
    
    # Process each line across all scripts
    for line_index in range(max_lines):
        candidate_lines = []
        line_scores = []
        line_types = []
        line_origins = []  # Track which script each line came from
        
        # Collect all candidate lines at this position from different scripts
        for script_index in range(len(dialogues)):
            if line_index < len(dialogues[script_index]):
                line = dialogues[script_index][line_index].strip()
                if not line:  # Skip empty lines
                    continue
                    
                # Determine line type (character name, dialogue, action, etc.)
                if line.isupper():  # Character name
                    line_type = "character"
                    characters.add(line)
                    if line not in character_context:
                        character_context[line] = []
                elif line.startswith('(') and line.endswith(')'):  # Action/direction
                    line_type = "action"
                else:  # Dialogue or other content
                    line_type = "dialogue"
                    # If we have a current character, associate this dialogue with them
                    if previous_line_type == "character" and scene_context:
                        current_character = scene_context[-1]
                        character_context[current_character].append(line)
                
                # Calculate base score (longer, more detailed lines are generally preferred)
                base_score = len(line) / 100  # Normalize length score
                
                # Compare with other scripts for similarity
                similarity_scores = []
                for other_script_index in range(len(dialogues)):
                    if script_index != other_script_index and line_index < len(dialogues[other_script_index]):
                        comparison_line = dialogues[other_script_index][line_index].strip()
                        if comparison_line:
                            sequence_match = SequenceMatcher(None, line, comparison_line)
                            similarity_scores.append(sequence_match.ratio())
                
                # Average similarity with other scripts (higher is better for consensus)
                avg_similarity = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0.5
                
                # Context score - does this line maintain continuity with previous lines?
                context_score = 0.0
                if scene_context and line_type == "dialogue" and previous_line_type == "character":
                    current_character = scene_context[-1]
                    # Check if dialogue matches character's previous patterns
                    for prev_dialogue in character_context.get(current_character, []):
                        dialogue_match = SequenceMatcher(None, line, prev_dialogue).ratio()
                        context_score = max(context_score, dialogue_match * 0.5)  # Cap context influence
                
                # Calculate final score using the provided weights
                final_score = (
                    (base_score * optimization_weights["base_score"]) + 
                    (avg_similarity * optimization_weights["similarity"]) + 
                    (context_score * optimization_weights["context"])
                )
                
                candidate_lines.append(line)
                line_scores.append(final_score)
                line_types.append(line_type)
                line_origins.append(script_index)
        
        # Select the best line if we have candidates
        if candidate_lines:
            best_index = line_scores.index(max(line_scores))
            best_line = candidate_lines[best_index]
            best_line_type = line_types[best_index]
            
            # Update context tracking
            scene_context.append(best_line)
            previous_line_type = best_line_type
            
            # Add to optimized script
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

def get_bedrock_client():
    """Initialize and return the AWS Bedrock client"""
    try:
        # Create a Bedrock client
        bedrock_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.getenv('AWS_REGION'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        return bedrock_client
    except Exception as e:
        st.error(f"Error initializing AWS Bedrock client: {str(e)}")
        return None

def analyze_script_with_claude(script_content, prompt_type="analyze", analysis_focus=None, temperature=0.7, enhancement_focus=None):
    """Analyze script content using Claude 3.5 Sonnet via AWS Bedrock
    
    Args:
        script_content (str): The script content to analyze
        prompt_type (str): Type of analysis to perform (analyze, enhance, feedback)
        analysis_focus (str, optional): Specific aspect to focus analysis on
        temperature (float, optional): Creativity level for AI (0.0-1.0)
        enhancement_focus (list, optional): Areas to focus enhancement on   
    
    Returns:
        str: AI response with analysis or enhanced script
    """
    bedrock_client = get_bedrock_client()
    if not bedrock_client:
        return "Error connecting to Claude AI. Please check your AWS credentials."
    
    # Base prompt templates
    base_prompts = {
        "analyze": """You are an expert screenplay and script analyst. Analyze the following script and provide insights on:
1. Plot structure and pacing
2. Character development and dialogue quality
3. Themes and subtext
4. Areas for improvement
Provide the enhanced version of the script in the same language as the original.

Script:
{script}

Provide a comprehensive analysis with specific examples from the text.""",
        
        "enhance": """You are an expert screenplay writer. Enhance the following script by improving:
1. Dialogue to make it more natural and impactful
2. Scene descriptions to be more vivid and cinematic
3. Character interactions to create more tension and emotional depth
4. Overall pacing and flow

Maintain the original story and characters but elevate the quality of writing.

Script:
{script}

Provide the enhanced version of the script.""",
        
        "feedback": """You are an experienced script editor. Review the following script and provide constructive feedback on:
1. What works well in the script
2. What could be improved
3. Specific suggestions for revisions
4. Industry-standard formatting issues to fix

Script:
{script}

Provide detailed, actionable feedback that would help the writer improve this script."""
    }
    
    # Specialized analysis focus prompts
    analysis_focus_prompts = {
        "Comprehensive": base_prompts["analyze"],
        "Character Development": """You are an expert screenplay and script analyst specializing in character development. 

Analyze the following script with a focus on character development:
1. Character arcs and growth throughout the script
2. Character motivations and consistency
3. Depth and complexity of characters
4. Relationships between characters
5. Dialogue authenticity for each character

Script:
{script}

Provide a detailed analysis of the characters with specific examples from the text.""",
        
        "Dialogue Quality": """You are an expert screenplay and script analyst specializing in dialogue. 

Analyze the following script with a focus on dialogue quality:
1. Authenticity and naturalness of conversations
2. Character voice distinctiveness
3. Subtext and what's not being said
4. Pacing and rhythm of dialogue exchanges
5. How dialogue advances plot and reveals character

Script:
{script}

Provide a detailed analysis of the dialogue with specific examples from the text.""",
        
        "Plot Structure": """You are an expert screenplay and script analyst specializing in story structure. 

Analyze the following script with a focus on plot structure:
1. Act structure and key turning points
2. Pacing and momentum throughout the script
3. Conflict development and resolution
4. Subplot integration with the main plot
5. Effectiveness of the beginning and ending

Script:
{script}

Provide a detailed analysis of the plot structure with specific examples from the text."""
    }
    
    # Select the appropriate prompt template based on type and focus
    if prompt_type == "analyze" and analysis_focus:
        prompt_template = analysis_focus_prompts.get(analysis_focus, base_prompts["analyze"])
    else:
        prompt_template = base_prompts.get(prompt_type, base_prompts["analyze"])
    
    # Customize enhancement prompt if focus areas are provided
    if prompt_type == "enhance" and enhancement_focus and len(enhancement_focus) > 0:
        focus_areas = "\n".join([f"- {focus}" for focus in enhancement_focus])
        prompt_template = f"""You are an expert screenplay writer. Enhance the following script with a specific focus on these areas:
{focus_areas}

Maintain the original story, characters, and language of the script. If the script is in a non-English language like Telugu, Hindi, or any other language, your response MUST be in that same language. Do not translate the script to English.


Script:
{{script}}

Provide the enhanced version of the script in the same language as the original."""
    
    # Format the prompt with the script content
    formatted_prompt = prompt_template.format(script=script_content)
    
    try:
        # Prepare the request payload for Claude 3.5 Sonnet
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "temperature": float(temperature),  # Use the temperature parameter from the sidebar
            "messages": [
                {"role": "user", "content": formatted_prompt}
            ]
        }
        
        # Get the inference profile ARN from environment variables
        inference_profile_arn = os.getenv('INFERENCE_PROFILE_ARN')
        if not inference_profile_arn:
            return "Error: INFERENCE_PROFILE_ARN is not set in environment variables. Please check your .env file."
        
        # Make the API call to Claude via AWS Bedrock using the inference profile
        response = bedrock_client.invoke_model(
            body=json.dumps(request_body),
            modelId=inference_profile_arn,  # Use the inference profile ARN instead of direct model ID
            accept="application/json",
            contentType="application/json"
        )
        
        # Parse the response
        response_body = json.loads(response.get('body').read())
        ai_response = response_body.get('content', [{}])[0].get('text', "No response generated")
        
        return ai_response
    
    except Exception as e:
        st.error(f"Error calling Claude AI: {str(e)}")
        return f"Error: {str(e)}"

def main():
    apply_custom_css()
    
    # Create a modern header with logo and title
    st.markdown("""
    <div class="app-header">
       <h1><span style="color: #e8f4f8;">Genius</span>&nbsp;AI</h1>
        <p>AI-Powered Script Collaboration Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add a brief description of the platform
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <h4 style="color: #2a5d84; margin-top: 0;">About Genius AI</h4>
        <p>Genius AI streamlines collaborative scriptwriting by intelligently combining multiple drafts into a cohesive, polished scene. 
        Our advanced algorithm analyzes tone, style, and flow to create a seamless script that preserves the best elements from each contributor.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Define default settings that were previously in the sidebar
    optimization_mode = "Balanced"
    optimization_weights = {
        "base_score": 0.3,
        "similarity": 0.5,
        "context": 0.2
    }
    temperature = 0.7
    export_format = "Plain Text (.txt)"
    
    # Main content area
    st.header("Upload Your Scripts")
    
    # Add file upload with more context
    upload_col1, upload_col2 = st.columns([3, 1])
    with upload_col1:
        uploaded_files = st.file_uploader(
            "Upload multiple script drafts (TXT, PDF, DOCX)", 
            type=['txt', 'pdf', 'docx'], 
            accept_multiple_files=True,
            help="Upload multiple versions of the same scene to combine them into one optimized script."
        )
    
    with upload_col2:
        st.markdown("""
        <div class="info-box" style="height: 100%; display: flex; align-items: center; justify-content: center;">
            <p style="margin: 0; text-align: center;"><strong>Tip:</strong> Upload at least 2 drafts for best results</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Process uploaded files
    if uploaded_files:
        # Show file processing status with progress
        with st.status("Processing scripts...", expanded=True) as status:
            scripts = []
            file_names = []
            
            # Create a progress bar for file processing
            progress_bar = st.progress(0)
            total_files = len(uploaded_files)
            
            for i, uploaded_file in enumerate(uploaded_files):
                # Update progress
                progress = (i / total_files) * 100
                progress_bar.progress(int(progress))
                
                st.write(f"Reading {uploaded_file.name}...")
                content = read_file(uploaded_file)
                if content:
                    scripts.append(content)
                    file_names.append(uploaded_file.name)
            
            if scripts:
                # Complete the progress bar
                progress_bar.progress(100)
                
                st.write("Analyzing script similarities...")
                time.sleep(0.5)  # Simulate processing time
                
                st.write(f"Optimizing content using {optimization_mode} mode...")
                time.sleep(0.5)  # Simulate processing time
                
                # Use the optimization weights from the sidebar
                optimized_script = choose_best_parts(scripts, optimization_weights)
                formatted_script = format_script(optimized_script)
                
                st.write("Done!")
                status.update(label="All scripts processed successfully!", state="complete")
            else:
                status.update(label="No valid scripts found", state="error")
                st.error("Could not process any of the uploaded files. Please check the file formats and try again.")
        
        # Show script statistics
        if scripts:
            st.markdown("""<h3 style="color: #2a5d84; margin-top: 30px;">Script Statistics</h3>""", unsafe_allow_html=True)
            
            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
            
            with stat_col1:
                st.metric("Total Drafts", len(scripts))
            
            with stat_col2:
                # Calculate average script length
                avg_length = sum(len(script.split()) for script in scripts) / len(scripts)
                st.metric("Avg. Word Count", f"{int(avg_length)}")
            
            with stat_col3:
                # Count unique character names across all scripts
                character_count = len(set(line.strip() for script in scripts for line in script.split("\n") if line.strip().isupper()))
                st.metric("Characters", character_count)
            
            with stat_col4:
                # Calculate similarity between scripts
                if len(scripts) > 1:
                    similarities = []
                    for i in range(len(scripts)):
                        for j in range(i+1, len(scripts)):
                            similarity = SequenceMatcher(None, scripts[i], scripts[j]).ratio()
                            similarities.append(similarity)
                    avg_similarity = sum(similarities) / len(similarities)
                    st.metric("Draft Similarity", f"{int(avg_similarity * 100)}%")
                else:
                    st.metric("Draft Similarity", "N/A")
            
            # Create tabs for different functionalities with improved UI
            tabs = st.tabs(["📝 Optimized Script", "🔍 AI Analysis", "✨ AI Enhancement", "✏️ Edit Script", "📊 Compare Drafts"])
            
            # Tab 1: Optimized Script with improved UI
            with tabs[0]:
                st.markdown("""<h3 style="color: #2a5d84;">Optimized Script</h3>""", unsafe_allow_html=True)
                st.markdown("""<p style="color: #666;">This script combines the best elements from all uploaded drafts.</p>""", unsafe_allow_html=True)
                
                # Add a version info
                st.markdown(f"""<p style="color: #888; font-size: 12px;">Combined from {len(scripts)} drafts • {time.strftime('%B %d, %Y %H:%M')}</p>""", unsafe_allow_html=True)
                
                # Display the formatted script
                st.markdown(f"<div class='script-container'>{formatted_script}</div>", unsafe_allow_html=True)
                
                # Add download options in a more professional layout
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.download_button(
                        label="Download Optimized Script",
                        data=optimized_script,
                        file_name="optimized_script.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                # Removed Share Script button as requested
                with col2:
                    st.empty()
            
            # Tab 2: AI Analysis with Claude - Enhanced UI
            with tabs[1]:
                st.markdown("""<h3 style="color: #2a5d84;">AI Script Analysis</h3>""", unsafe_allow_html=True)
                st.markdown("""<p style="color: #666;">Get professional insights on your script's structure, characters, dialogue, and more.</p>""", unsafe_allow_html=True)
                
                # Add analysis options
                analysis_type = st.radio(
                    "Analysis Focus",
                    options=["Comprehensive", "Character Development", "Dialogue Quality", "Plot Structure"],
                    horizontal=True
                )
                
                # Create a container for the analysis results
                analysis_container = st.container()
                
                # Add a button to trigger the analysis
                if st.button("Analyze Script", key="analyze_btn", use_container_width=True):
                    with st.spinner("Genius AI is analyzing your script..."):
                        # Pass the analysis type and temperature to customize the analysis
                        analysis = analyze_script_with_claude(
                            script_content=optimized_script, 
                            prompt_type="analyze",
                            analysis_focus=analysis_type,
                            temperature=temperature
                        )
                        
                        # Store the analysis in session state for persistence
                        st.session_state.script_analysis = analysis
                
                # Display analysis results if available 
                with analysis_container:
                    if 'script_analysis' in st.session_state:
                        # Create a more visually appealing analysis display
                        st.markdown(f"""
                        <div class="card" style="margin-top: 20px;">
                            <h3 style="color: #2a5d84; margin-top: 0;">Script Analysis Results</h3>
                            <p style="font-size: 12px; color: #888;">Analysis focus: {analysis_type} • AI creativity: {temperature}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown(st.session_state.script_analysis)
                        
                        # Add download button for the analysis in a better position
                        st.download_button(
                            label="Download Analysis Report",
                            data=st.session_state.script_analysis,
                            file_name=f"script_analysis_{analysis_type.lower().replace(' ', '_')}.txt",
                            mime="text/plain"
                        )
            
            # Tab 3: AI Enhancement with Claude - Enhanced UI
            with tabs[2]:
                st.markdown("""<h3 style="color: #2a5d84;">AI Script Enhancement</h3>""", unsafe_allow_html=True)
                st.markdown("""<p style="color: #666;">Let Genius AI enhance your script with improved dialogue, descriptions, and character development.</p>""", unsafe_allow_html=True)
                
                # Add enhancement options
                enhancement_focus = st.multiselect(
                    "Enhancement Focus",
                    options=["Dialogue", "Character Development", "Scene Descriptions", "Emotional Impact", "Pacing"],
                    default=["Dialogue", "Scene Descriptions"],
                    help="Select areas to focus the enhancement on"
                )
                
                # Create a container for the enhanced script
                enhancement_container = st.container()
                
                # Add a button to trigger the enhancement
                if st.button("Enhance Script with Genius AI", key="enhance_btn", use_container_width=True):
                    with st.spinner("Genius AI is enhancing your script..."):
                        # Use the temperature from sidebar settings and enhancement focus
                        enhanced_script = analyze_script_with_claude(
                            script_content=optimized_script, 
                            prompt_type="enhance",
                            temperature=temperature,
                            enhancement_focus=enhancement_focus
                        )
                        
                        # Store the enhanced script in session state for persistence
                        st.session_state.enhanced_script = enhanced_script
                
                # Display enhanced script if available
                with enhancement_container:
                    if 'enhanced_script' in st.session_state:
                        st.markdown(f"""
                        <h3 style="color: #2a5d84; margin-top: 20px;">Enhanced Script</h3>
                        <p style="font-size: 12px; color: #888;">Focus areas: {', '.join(enhancement_focus)} • AI creativity: {temperature}</p>
                        """, unsafe_allow_html=True)
                        
                        # Create a toggle to show raw text or formatted view
                        view_mode = st.radio("View Mode", options=["Formatted View", "Raw Text"], horizontal=True)
                        
                        if view_mode == "Raw Text":
                            st.text_area("Enhanced Script", value=st.session_state.enhanced_script, height=400, key="enhanced_script_text", label_visibility="collapsed")
                        else:
                            # Format and display the enhanced script
                            st.markdown(f"<div class='script-container'>{format_script(st.session_state.enhanced_script)}</div>", unsafe_allow_html=True)
                        
                        # Add download options in a more professional layout
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            st.download_button(
                                label="Download Enhanced Script",
                                data=st.session_state.enhanced_script,
                                file_name="enhanced_script.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                        
                        # Add comparison functionality
                        with col2:
                            # Store comparison state in session state
                            if 'show_comparison' not in st.session_state:
                                st.session_state.show_comparison = False
                                
                            # Toggle comparison view when button is clicked
                            if st.button("Compare with Original", use_container_width=True):
                                st.session_state.show_comparison = not st.session_state.show_comparison
                        
                        # Show comparison if enabled
                        if 'show_comparison' in st.session_state and st.session_state.show_comparison:
                            st.markdown("""<h4 style="color: #2a5d84; margin-top: 20px;">Original vs Enhanced</h4>""", unsafe_allow_html=True)
                            
                            # Create dropdown to select which original script to compare with
                            selected_original = st.selectbox(
                                "Select original script to compare with:",
                                options=file_names,
                                index=0
                            )
                            selected_original_index = file_names.index(selected_original)
                            original_script_content = scripts[selected_original_index]
                            
                            # Create two columns for side-by-side comparison with improved readability
                            comp_col1, comp_col2 = st.columns(2)
                            
                            with comp_col1:
                                st.markdown(f"""<p style="font-weight: 500; color: #2a5d84;">Original Script: {selected_original}</p>""", unsafe_allow_html=True)
                                st.markdown(f"<div class='script-container' style='height: 600px; width: 100%; overflow-y: auto; background-color: #f9f9f9; font-size: 16px; line-height: 1.8;'>{format_script(original_script_content)}</div>", unsafe_allow_html=True)
                            
                            with comp_col2:
                                st.markdown("""<p style="font-weight: 500; color: #2a5d84;">Enhanced Script</p>""", unsafe_allow_html=True)
                                st.markdown(f"<div class='script-container' style='height: 600px; width: 100%; overflow-y: auto; background-color: #f0f7ff; font-size: 16px; line-height: 1.8;'>{format_script(st.session_state.enhanced_script)}</div>", unsafe_allow_html=True)
                            
                            # Calculate similarity between selected original and enhanced
                            similarity = SequenceMatcher(None, original_script_content, st.session_state.enhanced_script).ratio()
                            st.markdown(f"""<p>Similarity: <strong>{similarity:.2%}</strong></p>""", unsafe_allow_html=True)
                            
                            # Add a detailed diff view for better comparison
                            st.markdown("""<h4 style="color: #2a5d84; margin-top: 20px;">Detailed Changes</h4>""", unsafe_allow_html=True)
                            
                            # Split scripts into lines for comparison
                            original_lines = original_script_content.split('\n')
                            enhanced_lines = st.session_state.enhanced_script.split('\n')
                            
                            # Display line-by-line comparison with highlighting
                            diff_html = "<div style='font-family: monospace; white-space: pre-wrap; line-height: 1.5; padding: 10px; border: 1px solid #ddd; border-radius: 5px;'>"
                            
                            # Use difflib to get differences
                            import difflib
                            diff = difflib.ndiff(original_lines, enhanced_lines)
                            
                            for line in diff:
                                if line.startswith('+ '):
                                    diff_html += f"<div style='background-color: #e6ffe6; color: #006600;'>{line}</div>"
                                elif line.startswith('- '):
                                    diff_html += f"<div style='background-color: #ffe6e6; color: #990000;'>{line}</div>"
                                elif line.startswith('? '):
                                    continue  # Skip the hint lines
                                else:
                                    diff_html += f"<div>{line}</div>"
                            
                            diff_html += "</div>"
                            st.markdown(diff_html, unsafe_allow_html=True)

            # Tab 4: Edit Script - Enhanced UI
            with tabs[3]:
                st.markdown("""<h3 style="color: #2a5d84;">Script Editor</h3>""", unsafe_allow_html=True)
                st.markdown("""<p style="color: #666;">Make manual edits to your script with real-time preview.</p>""", unsafe_allow_html=True)
                
                # Create a more professional editor layout
                edit_col1, edit_col2 = st.columns([1, 1])
                
                # Add script selection option
                script_to_edit = st.radio(
                    "Select script to edit:",
                    options=["Optimized Script", "Enhanced Script (if available)"],
                    horizontal=True
                )
                
                # Determine which script to use based on selection
                if script_to_edit == "Enhanced Script (if available)" and 'enhanced_script' in st.session_state:
                    source_script = st.session_state.enhanced_script
                    script_source_name = "Enhanced Script"
                else:
                    source_script = optimized_script
                    script_source_name = "Optimized Script"
                
                with edit_col1:
                    st.markdown(f"""<p style="font-weight: 500; color: #2a5d84;">Edit {script_source_name}</p>""", unsafe_allow_html=True)
                    # Initialize session state variables if they don't exist
                    if 'script_content' not in st.session_state or st.session_state.get('last_script_source') != script_to_edit:
                        st.session_state.script_content = source_script
                        st.session_state.last_script_source = script_to_edit
                    if 'should_reset' not in st.session_state:
                        st.session_state.should_reset = False
                        
                    # Check if we need to reset the content
                    if st.session_state.should_reset:
                        st.session_state.script_content = source_script
                        st.session_state.should_reset = False
                    
                    # Use the tracked content to populate the text area
                    edited_script = st.text_area(
                        f"Edit the {script_source_name.lower()}", 
                        value=st.session_state.script_content,
                        height=600, 
                        key="edit_area", 
                        label_visibility="collapsed", 
                        help=f"You can edit the {script_source_name.lower()} here.", 
                        placeholder="Edit your script here..."
                    )
                    
                    # Update the stored content whenever the text area changes
                    st.session_state.script_content = edited_script
                
                with edit_col2:
                    st.markdown("""<p style="font-weight: 500; color: #2a5d84;">Live Preview</p>""", unsafe_allow_html=True)
                    # Live Preview for Edit Mode
                    st.markdown(f"<div class='script-container' style='height: 600px; width: 100%; overflow-y: auto;'>{format_script(edited_script)}</div>", unsafe_allow_html=True)
                
                # Add professional download and save options
                save_col1, save_col2, save_col3, save_col4 = st.columns([1, 1, 1, 1])
                with save_col1:
                    st.download_button(
                        label="Download",
                        data=edited_script,
                        file_name="edited_script.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
                # Add undo functionality
                with save_col2:
                    # Initialize undo history if it doesn't exist
                    if 'undo_history' not in st.session_state:
                        st.session_state.undo_history = []
                        st.session_state.current_undo_index = -1
                    
                    # Store the current state in undo history when content changes
                    if 'last_script_content' not in st.session_state:
                        st.session_state.last_script_content = edited_script
                    elif st.session_state.last_script_content != edited_script:
                        # Content has changed, add to undo history
                        st.session_state.undo_history.append(st.session_state.last_script_content)
                        if len(st.session_state.undo_history) > 20:  # Limit history size
                            st.session_state.undo_history.pop(0)
                        st.session_state.current_undo_index = len(st.session_state.undo_history) - 1
                        st.session_state.last_script_content = edited_script
                    
                    # Undo button
                    if st.button("Undo", use_container_width=True):
                        if st.session_state.undo_history and st.session_state.current_undo_index >= 0:
                            # Get the previous state
                            previous_state = st.session_state.undo_history[st.session_state.current_undo_index]
                            # Update the script content
                            st.session_state.script_content = previous_state
                            # Update the index
                            st.session_state.current_undo_index -= 1
                            st.rerun()
                
                with save_col3:
                    # Empty column for spacing
                    st.empty()
                    
                with save_col4:
                    # Make Revert to Original button functional
                    if st.button("Revert to Original", use_container_width=True):
                        # Store the original script in a separate session state variable
                        st.session_state.script_content = source_script
                        # Clear undo history when reverting to original
                        st.session_state.undo_history = []
                        st.session_state.current_undo_index = -1
                        # Set a flag to indicate we should reset on next render
                        st.session_state.should_reset = True
                        st.rerun()
            
            # Tab 5: New Compare Drafts feature
            with tabs[4]:
                st.markdown("""<h3 style="color: #2a5d84;">Draft Comparison</h3>""", unsafe_allow_html=True)
                st.markdown("""<p style="color: #666;">Compare different drafts to see similarities and differences.</p>""", unsafe_allow_html=True)
                
                # Create a draft selection interface
                comp_col1, comp_col2 = st.columns(2)
                
                with comp_col1:
                    draft1 = st.selectbox("Select First Draft", options=file_names, index=0)
                    draft1_index = file_names.index(draft1)
                    st.text_area("Draft 1 Content", value=scripts[draft1_index], height=400, key="draft1_content")
                
                with comp_col2:
                    draft2 = st.selectbox("Select Second Draft", options=file_names, index=min(1, len(file_names)-1))
                    draft2_index = file_names.index(draft2)
                    st.text_area("Draft 2 Content", value=scripts[draft2_index], height=400, key="draft2_content")
                
                # Calculate and display similarity metrics
                if draft1 != draft2:
                    similarity = SequenceMatcher(None, scripts[draft1_index], scripts[draft2_index]).ratio()
                    
                    st.markdown("""<h4 style="color: #2a5d84; margin-top: 20px;">Similarity Analysis</h4>""", unsafe_allow_html=True)
                    
                    # Display similarity as a progress bar
                    st.markdown(f"""<p>Overall similarity: <strong>{similarity:.2%}</strong></p>""", unsafe_allow_html=True)
                    st.progress(similarity)
                    
                    # Add more detailed comparison metrics
                    metric_col1, metric_col2, metric_col3 = st.columns(3)
                    
                    with metric_col1:
                        # Word count comparison
                        words1 = len(scripts[draft1_index].split())
                        words2 = len(scripts[draft2_index].split())
                        word_diff = words2 - words1
                        st.metric("Word Count", f"{words1} vs {words2}", delta=word_diff)
                    
                    with metric_col2:
                        # Character count
                        chars1 = set(line.strip() for line in scripts[draft1_index].split("\n") if line.strip().isupper())
                        chars2 = set(line.strip() for line in scripts[draft2_index].split("\n") if line.strip().isupper())
                        shared_chars = len(chars1.intersection(chars2))
                        total_chars = len(chars1.union(chars2))
                        st.metric("Shared Characters", f"{shared_chars}/{total_chars}", delta=f"{shared_chars/total_chars:.0%}" if total_chars > 0 else "N/A")
                    
                    with metric_col3:
                        # Line count comparison
                        lines1 = len([l for l in scripts[draft1_index].split("\n") if l.strip()])
                        lines2 = len([l for l in scripts[draft2_index].split("\n") if l.strip()])
                        line_diff = lines2 - lines1
                        st.metric("Line Count", f"{lines1} vs {lines2}", delta=line_diff)
                    
                    # Add a button to generate a detailed comparison report
                    if st.button("Generate Detailed Comparison Report", use_container_width=True):
                        # Create a detailed comparison report
                        st.markdown("""<h4 style="color: #2a5d84; margin-top: 20px;">Detailed Comparison Report</h4>""", unsafe_allow_html=True)
                        
                        # Generate report container with improved styling
                        report_container = st.container()
                        
                        with report_container:
                            # Create tabs for different aspects of the comparison (removed Content Analysis)
                            report_tabs = st.tabs(["Summary", "Structure Comparison", "Character Analysis"])
                            
                            with report_tabs[0]:
                                # Summary tab
                                st.markdown("""<h5 style="color: #2a5d84;">Comparison Summary</h5>""", unsafe_allow_html=True)
                                
                                # Create a summary card with key metrics
                                st.markdown(f"""
                                <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                                    <h6 style="margin-top: 0;">Draft Comparison: {draft1} vs {draft2}</h6>
                                    <p><strong>Overall Similarity:</strong> {similarity:.2%}</p>
                                    <p><strong>Word Count Difference:</strong> {word_diff} words ({words1} vs {words2})</p>
                                    <p><strong>Line Count Difference:</strong> {line_diff} lines ({lines1} vs {lines2})</p>
                                    <p><strong>Shared Characters:</strong> {shared_chars} of {total_chars} ({shared_chars/total_chars:.0%} if total_chars > 0 else "N/A")</p>
                                    <p><strong>Generated:</strong> {time.strftime('%B %d, %Y %H:%M')}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Add a visual representation of the similarity
                                st.markdown("""<h6 style="margin-top: 20px;">Visual Similarity</h6>""", unsafe_allow_html=True)
                                st.progress(similarity)
                            
                            # Content Analysis tab has been removed
                            
                            with report_tabs[1]:
                                # Structure Comparison tab
                                st.markdown("""<h5 style="color: #2a5d84;">Structure Comparison</h5>""", unsafe_allow_html=True)
                                
                                # Improved script structure detection algorithm
                                def count_elements(script):
                                    lines = script.split('\n')
                                    scenes = 0
                                    dialogue_lines = 0
                                    action_blocks = 0
                                    parentheticals = 0
                                    transitions = 0
                                    scene_headings = []
                                    characters = set()
                                    
                                    # Regex patterns for better detection
                                    import re
                                    scene_pattern = re.compile(r'^(INT|EXT|INT\./EXT|EXT\./INT|I/E|E/I)[. ]', re.IGNORECASE)
                                    transition_pattern = re.compile(r'^(FADE|DISSOLVE|CUT TO|SMASH|WIPE)', re.IGNORECASE)
                                    parenthetical_pattern = re.compile(r'^\(.+\)$')
                                    
                                    in_action_block = False
                                    current_scene = None
                                    
                                    for i, line in enumerate(lines):
                                        line = line.strip()
                                        if not line:
                                            in_action_block = False
                                            continue
                                        
                                        # Check for scene headings
                                        if scene_pattern.match(line) or (line.isupper() and ("INT." in line or "EXT." in line)):
                                            scenes += 1
                                            in_action_block = False
                                            current_scene = line
                                            scene_headings.append(current_scene)
                                        
                                        # Check for transitions
                                        elif transition_pattern.match(line) or (line.isupper() and any(t in line for t in ["FADE", "CUT", "DISSOLVE"])):
                                            transitions += 1
                                            in_action_block = False
                                        
                                        # Check for character names (all caps, not too long, not a scene heading or transition)
                                        elif line.isupper() and len(line.split()) <= 3 and not scene_pattern.match(line) and not transition_pattern.match(line):
                                            dialogue_lines += 1
                                            in_action_block = False
                                            characters.add(line)
                                        
                                        # Check for parentheticals
                                        elif parenthetical_pattern.match(line):
                                            parentheticals += 1
                                            in_action_block = False
                                        
                                        # Everything else is likely action
                                        elif line and not line.isupper() and not parenthetical_pattern.match(line):
                                            if not in_action_block:
                                                action_blocks += 1
                                                in_action_block = True
                                    
                                    return {
                                        "scenes": scenes,
                                        "scene_headings": scene_headings,
                                        "dialogue_lines": dialogue_lines,
                                        "action_blocks": action_blocks,
                                        "parentheticals": parentheticals,
                                        "transitions": transitions,
                                        "characters": characters
                                    }
                                
                                # Get structure counts with improved algorithm
                                structure1 = count_elements(scripts[draft1_index])
                                structure2 = count_elements(scripts[draft2_index])
                                
                                # Display structure comparison with enhanced metrics
                                st.markdown("""<h6 style="color: #2a5d84; margin-top: 15px;">Script Structure Metrics</h6>""", unsafe_allow_html=True)
                                
                                # Create two rows of columns for more detailed metrics
                                struct_col1, struct_col2, struct_col3 = st.columns(3)
                                
                                with struct_col1:
                                    scene_diff = structure2["scenes"] - structure1["scenes"]
                                    st.metric("Scene Count", f"{structure1['scenes']} vs {structure2['scenes']}", delta=scene_diff)
                                
                                with struct_col2:
                                    dialogue_diff = structure2["dialogue_lines"] - structure1["dialogue_lines"]
                                    st.metric("Dialogue Lines", f"{structure1['dialogue_lines']} vs {structure2['dialogue_lines']}", delta=dialogue_diff)
                                
                                with struct_col3:
                                    action_diff = structure2["action_blocks"] - structure1["action_blocks"]
                                    st.metric("Action Blocks", f"{structure1['action_blocks']} vs {structure2['action_blocks']}", delta=action_diff)
                                
                                # Second row for additional metrics
                                struct_col4, struct_col5, struct_col6 = st.columns(3)
                                
                                with struct_col4:
                                    parenthetical_diff = structure2["parentheticals"] - structure1["parentheticals"]
                                    st.metric("Parentheticals", f"{structure1['parentheticals']} vs {structure2['parentheticals']}", delta=parenthetical_diff)
                                
                                with struct_col5:
                                    transition_diff = structure2["transitions"] - structure1["transitions"]
                                    st.metric("Transitions", f"{structure1['transitions']} vs {structure2['transitions']}", delta=transition_diff)
                                
                                with struct_col6:
                                    char_count1 = len(structure1["characters"])
                                    char_count2 = len(structure2["characters"])
                                    char_diff = char_count2 - char_count1
                                    st.metric("Character Count", f"{char_count1} vs {char_count2}", delta=char_diff)
                                
                                # Scene-by-scene comparison
                                st.markdown("""<h6 style="color: #2a5d84; margin-top: 20px;">Scene Breakdown</h6>""", unsafe_allow_html=True)
                                
                                # Calculate scene similarity
                                scene_headings1 = structure1["scene_headings"]
                                scene_headings2 = structure2["scene_headings"]
                                
                                # Create scene comparison data
                                scene_data = []
                                max_scenes = max(len(scene_headings1), len(scene_headings2))
                                
                                for i in range(max_scenes):
                                    scene1 = scene_headings1[i] if i < len(scene_headings1) else "N/A"
                                    scene2 = scene_headings2[i] if i < len(scene_headings2) else "N/A"
                                    
                                    if scene1 != "N/A" and scene2 != "N/A":
                                        similarity = SequenceMatcher(None, scene1, scene2).ratio()
                                        status = "Same" if similarity > 0.8 else "Similar" if similarity > 0.5 else "Different"
                                    else:
                                        similarity = 0
                                        status = "Missing in " + (draft1 if scene1 == "N/A" else draft2)
                                    
                                    scene_data.append({
                                        "Scene #": i+1,
                                        f"{draft1}": scene1,
                                        f"{draft2}": scene2,
                                        "Status": status,
                                        "Similarity": f"{similarity:.0%}"
                                    })
                                
                                # Display scene comparison as a dataframe
                                st.dataframe(scene_data, use_container_width=True)
                            
                            with report_tabs[2]:
                                # Character Analysis tab
                                st.markdown("""<h5 style="color: #2a5d84;">Character Analysis</h5>""", unsafe_allow_html=True)
                                
                                # Enhanced character analysis with more context
                                def extract_characters(script):
                                    lines = script.split('\n')
                                    characters = {}
                                    character_contexts = {}
                                    
                                    # Regex patterns for better detection
                                    import re
                                    scene_pattern = re.compile(r'^(INT|EXT|INT\./EXT|EXT\./INT|I/E|E/I)[. ]', re.IGNORECASE)
                                    
                                    current_character = None
                                    current_scene = None
                                    
                                    for i, line in enumerate(lines):
                                        line = line.strip()
                                        if not line:
                                            continue
                                        
                                        # Track scene headings
                                        if scene_pattern.match(line) or (line.isupper() and ("INT." in line or "EXT." in line)):
                                            current_scene = line
                                        
                                        # Identify character names
                                        elif line.isupper() and len(line.split()) <= 3 and not scene_pattern.match(line) and not any(t in line for t in ["FADE", "CUT", "DISSOLVE"]):
                                            current_character = line
                                            
                                            # Count character appearances
                                            if current_character in characters:
                                                characters[current_character] += 1
                                            else:
                                                characters[current_character] = 1
                                                character_contexts[current_character] = []
                                            
                                            # Store scene context for this character
                                            if current_scene and current_scene not in character_contexts[current_character]:
                                                character_contexts[current_character].append(current_scene)
                                    
                                    # Calculate additional character metrics
                                    character_metrics = {}
                                    for char, count in characters.items():
                                        character_metrics[char] = {
                                            "line_count": count,
                                            "scene_count": len(character_contexts[char]),
                                            "scenes": character_contexts[char]
                                        }
                                    
                                    return character_metrics
                                
                                # Get enhanced character metrics
                                chars1_dict = extract_characters(scripts[draft1_index])
                                chars2_dict = extract_characters(scripts[draft2_index])
                                
                                # Get all character names
                                all_chars = set(chars1_dict.keys()).union(set(chars2_dict.keys()))
                                
                                # Display character comparison with improved metrics
                                st.markdown("""<h6 style="color: #2a5d84;">Character Analysis</h6>""", unsafe_allow_html=True)
                                
                                # Create a more detailed table for character comparison
                                char_data = []
                                for char in all_chars:
                                    # Get metrics or default values
                                    metrics1 = chars1_dict.get(char, {"line_count": 0, "scene_count": 0, "scenes": []})
                                    metrics2 = chars2_dict.get(char, {"line_count": 0, "scene_count": 0, "scenes": []})
                                    
                                    # Extract counts
                                    count1 = metrics1["line_count"] if isinstance(metrics1, dict) else 0
                                    count2 = metrics2["line_count"] if isinstance(metrics2, dict) else 0
                                    scene_count1 = metrics1["scene_count"] if isinstance(metrics1, dict) else 0
                                    scene_count2 = metrics2["scene_count"] if isinstance(metrics2, dict) else 0
                                    
                                    # Calculate differences
                                    line_diff = count2 - count1
                                    scene_diff = scene_count2 - scene_count1
                                    
                                    # Calculate importance score (% of total dialogue lines)
                                    total_lines1 = structure1["dialogue_lines"]
                                    total_lines2 = structure2["dialogue_lines"]
                                    importance1 = (count1 / total_lines1 * 100) if total_lines1 > 0 else 0
                                    importance2 = (count2 / total_lines2 * 100) if total_lines2 > 0 else 0
                                    
                                    # Add to data table
                                    char_data.append({
                                        "Character": char,
                                        f"Lines in {draft1}": count1,
                                        f"Lines in {draft2}": count2,
                                        "Line Diff": line_diff,
                                        f"Scenes in {draft1}": scene_count1,
                                        f"Scenes in {draft2}": scene_count2,
                                        "Scene Diff": scene_diff,
                                        f"Importance in {draft1}": f"{importance1:.1f}%",
                                        f"Importance in {draft2}": f"{importance2:.1f}%"
                                    })
                                
                                # Sort by total lines
                                char_data.sort(key=lambda x: x[f"Lines in {draft1}"] + x[f"Lines in {draft2}"], reverse=True)
                                
                                # Display as a dataframe with improved formatting
                                st.dataframe(char_data, use_container_width=True)
                                
                                # Character presence visualization
                                st.markdown("""<h6 style="color: #2a5d84; margin-top: 15px;">Character Presence Comparison</h6>""", unsafe_allow_html=True)
                                
                                # Get top characters for visualization
                                top_chars = [item["Character"] for item in char_data[:min(5, len(char_data))]]
                                
                                # Create data for visualization
                                chart_data = []
                                for char in top_chars:
                                    metrics1 = chars1_dict.get(char, {"line_count": 0})
                                    metrics2 = chars2_dict.get(char, {"line_count": 0})
                                    
                                    count1 = metrics1["line_count"] if isinstance(metrics1, dict) else 0
                                    count2 = metrics2["line_count"] if isinstance(metrics2, dict) else 0
                                    
                                    chart_data.append({"Character": char, draft1: count1, draft2: count2})
                                
                                # Convert to DataFrame for charting
                                import pandas as pd
                                chart_df = pd.DataFrame(chart_data)
                                
                                # Display bar chart if we have data
                                if not chart_df.empty and "Character" in chart_df.columns:
                                    st.bar_chart(chart_df.set_index("Character"))
                                elif not chart_df.empty:
                                    st.warning("Unable to create chart: 'Character' column not found")
                                else:
                                    st.info("No character data available for visualization")
                            
                            # Add download button for the report
                            report_text = f"""# Detailed Comparison Report
## {draft1} vs {draft2}

### Summary
- Overall Similarity: {similarity:.2%}
- Word Count: {words1} vs {words2} (Difference: {word_diff})
- Line Count: {lines1} vs {lines2} (Difference: {line_diff})
- Shared Characters: {shared_chars} of {total_chars} ({(shared_chars/total_chars)*100:.0f}% if total_chars > 0 else "N/A")

### Generated on {time.strftime('%B %d, %Y %H:%M')}
"""
                            
                            st.download_button(
                                label="Download Comparison Report",
                                data=report_text,
                                file_name=f"comparison_report_{draft1}_{draft2}.txt",
                                mime="text/plain",
                                use_container_width=True
                            )

if __name__ == "__main__":
    main()