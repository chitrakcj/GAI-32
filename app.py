
import streamlit as st
import google.generativeai as genai
import os
import json
import time
from huggingface_hub import InferenceClient
from PIL import Image
import io

# Configuration and Initialization
st.set_page_config(
    page_title="ForgeVision AI | Architecture & Design",
    page_icon="⚒️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Advanced CSS for high-fidelity industrial dashboard
st.markdown("""
    <style>
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .stTextArea textarea {
        background-color: #1e293b !important;
        color: white !important;
        border: 1px solid #334155 !important;
        border-radius: 0.75rem !important;
    }
    .stSelectbox div[data-baseweb="select"] {
        background-color: #1e293b !important;
        border-radius: 0.75rem !important;
    }
    .stButton>button {
        width: 100%;
        background-color: #3b82f6 !important;
        color: white !important;
        border: none !important;
        padding: 0.85rem !important;
        font-weight: 700 !important;
        border-radius: 0.75rem !important;
        transition: all 0.2s ease-in-out !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    .stButton>button:hover {
        background-color: #2563eb !important;
        box-shadow: 0 0 25px rgba(59, 130, 246, 0.4) !important;
        transform: scale(1.02);
    }
    .spec-card {
        background-color: #111827;
        padding: 2rem;
        border-radius: 1.5rem;
        border: 1px solid #1f2937;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        height: 100%;
    }
    .blue-accent {
        color: #60a5fa;
        font-weight: 800;
    }
    .tech-header {
        font-family: 'Inter', sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.2em;
        font-size: 0.8rem;
        color: #94a3b8;
        margin-bottom: 0.5rem;
    }
    .tech-value {
        font-size: 1.15rem;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 1.25rem;
    }
    .innov-item {
        background: rgba(30, 41, 59, 0.5);
        padding: 0.75rem 1rem;
        border-radius: 0.75rem;
        border-left: 3px solid #3b82f6;
        margin-bottom: 0.75rem;
        font-size: 0.95rem;
    }
    .image-container {
        border-radius: 1.5rem;
        overflow: hidden;
        border: 1px solid #1f2937;
        background: #000;
        margin-bottom: 2rem;
    }
    /* Mermaid diagram custom styling */
    .mermaid {
        background: #1e293b;
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
    }
    </style>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({ startOnLoad: true, theme: 'dark' });
    </script>
""", unsafe_allow_html=True)

# API Setup
api_key = "AIzaSyAxrUrBFEp0qbb2lVBWPe0W89iH8ztiQKI"
hf_token = st.secrets["HF_TOKEN"]

if not api_key:
    st.error("Missing API_KEY environment variable.")
    st.stop()

# Initialize Gemini
genai.configure(api_key=api_key)
# Initialize HF Client
image_client = InferenceClient("black-forest-labs/FLUX.1-schnell", token=hf_token)

# Sidebar UI
with st.sidebar:
    st.markdown("### <span class='blue-accent'>FORGE</span>VISION <small>v3.5.1</small>", unsafe_allow_html=True)
    st.markdown("Precision Concept Engineering")
    st.divider()
    
    concept = st.text_area("Manufacturing Intent", placeholder="Describe your industrial concept...", height=120)
    industry = st.selectbox("Market Segment", ["Aerospace & Defense", "Heavy Automotive", "Precision Electronics", "Renewable Systems", "Industrial Robotics"])
    style = st.radio("Aesthetic Driver", ["High-Tech Prototype", "Sleek Minimalist", "Rugged Industrial", "Tactical Hardware"])
    
    st.divider()
    generate_btn = st.button("Synthesize & Render")
    
    st.sidebar.markdown("### Engine Status")
    st.sidebar.info("🧠 Logic: Gemini 3 Flash")
    st.sidebar.info("🎨 Render: HF Flux.1-Schnell")

# Main Navigation
tab_workspace, tab_arch = st.tabs(["🏗️ Concept Workspace", "📐 System Blueprint"])

with tab_workspace:
    if not generate_btn and 'result' not in st.session_state:
        st.title("Industrial Design Synthesis")
        st.markdown("#### Transforming complex manufacturing data into high-fidelity prototypes.")
        
        info_cols = st.columns(3)
        with info_cols[0]:
            st.markdown('<div class="spec-card"><h3 class="blue-accent">01. LOGIC</h3><p>Gemini 3 Flash parses technical requirements, selecting materials and energy topologies.</p></div>', unsafe_allow_html=True)
        with info_cols[1]:
            st.markdown('<div class="spec-card"><h3 class="blue-accent">02. SPECS</h3><p>System generates detailed BoM, physical dimensions, and cost estimates.</p></div>', unsafe_allow_html=True)
        with info_cols[2]:
            st.markdown('<div class="spec-card"><h3 class="blue-accent">03. RENDER</h3><p>Flux.1-Schnell produces photorealistic 4K concept imagery.</p></div>', unsafe_allow_html=True)

    if generate_btn and concept:
        if 'result' in st.session_state:
            del st.session_state.result
            
        with st.spinner("Synthesizing engineering logic..."):
            try:
                text_model = genai.GenerativeModel('gemini-3-flash-preview')
                logic_prompt = f"Design a manufacturing prototype for: '{concept}'. Vertical: {industry}. Style: {style}. Return JSON ONLY with fields: name, philosophy, innovations (list), specs (materials, dimensions, power, cost), image_prompt. Ensure image_prompt is highly descriptive."
                text_response = text_model.generate_content(logic_prompt, generation_config={"response_mime_type": "application/json"})
                
                # Robust JSON Sanitization
                raw_response = text_response.text.strip()
                if raw_response.startswith("```"):
                    # Extract content between backticks if model ignored 'json only' instruction
                    lines = raw_response.splitlines()
                    if lines[0].startswith("```"): lines = lines[1:]
                    if lines and lines[-1].startswith("```"): lines = lines[:-1]
                    raw_response = "\n".join(lines).strip()
                
                try:
                    design_data = json.loads(raw_response)
                except json.JSONDecodeError:
                    # Final attempt fallback using boundary searching
                    start = raw_response.find('{')
                    end = raw_response.rfind('}')
                    if start != -1 and end != -1:
                        design_data = json.loads(raw_response[start:end+1])
                    else:
                        raise ValueError("Failed to parse reasoning engine output as JSON.")

                # Handle List vs Object responses (Fixes the "list indices must be integers" error)
                if isinstance(design_data, list):
                    design_data = design_data[0] if len(design_data) > 0 else {}

                if not isinstance(design_data, dict) or 'image_prompt' not in design_data:
                    raise ValueError("Invalid technical blueprint structure received from model.")
                
                with st.spinner("Rendering visual prototype..."):
                    image = image_client.text_to_image(design_data['image_prompt'], width=1024, height=768)
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    st.session_state.result = {"design": design_data, "image": img_byte_arr.getvalue()}
            except Exception as e:
                st.error(f"Synthesis Failure: {str(e)}")

    if 'result' in st.session_state:
        res = st.session_state.result
        design = res["design"]
        st.markdown(f"## <span class='blue-accent'>01</span> Prototype Visualization", unsafe_allow_html=True)
        st.markdown('<div class="image-container">', unsafe_allow_html=True)
        st.image(res["image"], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.divider()
        col_narr, col_spec = st.columns([3, 2])
        with col_narr:
            st.markdown(f"## <span class='blue-accent'>02</span> Technical Brief", unsafe_allow_html=True)
            st.markdown(f'<div class="spec-card"><h2 style="color:#60a5fa;">{design.get("name", "Unnamed Concept")}</h2><p class="tech-header">Design Philosophy</p><p style="color:#cbd5e1;">{design.get("philosophy", "No philosophy provided.")}</p><p class="tech-header">Innovation Stack</p>{"".join([f"<div class='innov-item'>{i}</div>" for i in design.get("innovations", ["Standard Configuration"])])}</div>', unsafe_allow_html=True)
        with col_spec:
            st.markdown(f"## <span class='blue-accent'>03</span> Engineering Specs", unsafe_allow_html=True)
            specs = design.get('specs', {})
            st.markdown(f'<div class="spec-card"><p class="tech-header">Materials</p><p class="tech-value">{specs.get("materials", "TBD")}</p><p class="tech-header">Dimensions</p><p class="tech-value">{specs.get("dimensions", "Standard Scale")}</p><p class="tech-header">Power</p><p class="tech-value">{specs.get("power", "Passive")}</p><p class="tech-header">Est Cost</p><p class="tech-value">{specs.get("cost", "Market Rate")}</p></div>', unsafe_allow_html=True)

with tab_arch:
    st.title("System Architecture & Workflow")
    st.markdown("""
    ForgeVision utilizes a high-performance decoupled architecture. Detailed **Low-Level Design (LLD)** documents are available in `SYSTEM_DESIGN.md`.
    """)
    
    # 1. High Level Architecture
    st.markdown("#### 01. High-Level System Architecture")
    st.markdown("""
    <div class="mermaid">
    graph TD
        User[User Interface] -->|Concept Input| SL[Streamlit Controller]
        SL -->|Request Analysis| GMN[Gemini 3 Flash Logic Engine]
        GMN -->|Structured JSON| SL
        SL -->|Optimized Prompt| HF[HF Flux.1-Schnell Render Engine]
        HF -->|Binary Buffer| SL
        SL -->|Final Presentation| User
        
        style GMN fill:#3b82f6,stroke:#fff,stroke-width:2px,color:#fff
        style HF fill:#60a5fa,stroke:#fff,stroke-width:2px,color:#fff
        style SL fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:#fff
    </div>
    """, unsafe_allow_html=True)

    # 2. Sequence Workflow
    st.markdown("#### 02. Model Workflow & Data Transformation")
    st.markdown("""
    <div class="mermaid">
    sequenceDiagram
        participant U as User
        participant C as Controller (Streamlit)
        participant L as Logic (Gemini)
        participant R as Renderer (HF Flux)

        U->>C: Submit Idea (Text + Parameters)
        C->>L: System Instruct: "Act as Engineer"
        L->>L: Analyze Material Feasibility
        L->>C: Return Structured JSON (Specs + Visual Prompt)
        C->>R: API Call: Text-to-Image (Flux)
        R->>R: Latent Diffusion Synthesis
        R->>C: Return Image Buffer
        C->>U: Render Dashboard (Specs + 4K Image)
    </div>
    """, unsafe_allow_html=True)

    # 3. Component Breakdown
    st.markdown("#### 03. Component Responsibilities")
    arch_cols = st.columns(3)
    with arch_cols[0]:
        st.info("**Frontend (Streamlit)**\n- State Management\n- Asset Buffering\n- CSS-in-JS UI Injection\n- Multi-modal Presentation")
    with arch_cols[1]:
        st.info("**Reasoning Engine (Gemini)**\n- Semantic Parsing\n- Technical Schema Generation\n- Industry Constraints Check\n- Prompt Architecture")
    with arch_cols[2]:
        st.info("**Vision Engine (Hugging Face)**\n- Tensor Processing\n- Latent Space Mapping\n- Material Texture Synthesis\n- 1024x768 PNG Generation")

    st.markdown("#### 04. Data Schema Definition")
    st.code("""
{
  "project_lifecycle": {
    "step_1": "Raw User Intent (NLP)",
    "step_2": "Technical Decomposition (Gemini Logic)",
    "step_3": "Structured JSON Blueprint",
    "step_4": "Visual Realization (HF Diffusion)",
    "step_5": "Client-Side Assembly"
  },
  "output_fidelity": "1024x768 / PNG-32"
}
    """, language="json")

st.sidebar.markdown("---")
st.sidebar.caption("© 2025 ForgeVision AI | v3.5.1")
st.sidebar.caption("Architectural Review Mode Active")
