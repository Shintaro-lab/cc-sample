import streamlit as st

def switch_theme(mode: str):
    """テーマを切り替えて反映する"""
    config = {
        'light': {
            'primaryColor': '#FF4B4B',
            'backgroundColor': '#FFFFFF',
            'secondaryBackgroundColor': '#F0F2F6',
            'textColor': '#31333F'
        },
        'dark': {
            'primaryColor': '#FF6B6B',
            'backgroundColor': '#1E1E1E',
            'secondaryBackgroundColor': '#121212',
            'textColor': '#FFFFFF'
        }
    }
    
    selected = config[mode]
    st.markdown(f"""
        <style>
        .stApp {{
            background-color: {selected['backgroundColor']};
            color: {selected['textColor']};
        }}
        .stAppHeader {{
            background-color: {selected['backgroundColor']};
        }}
        .stSidebar {{
            background-color: {selected['secondaryBackgroundColor']};
            color: {selected['textColor']};
        }}
        .stButton button {{
            color: {selected['textColor']};
            background-color: {selected['backgroundColor']};
            border-color: {selected['primaryColor']};
        }}
        .stFormSubmitButton button {{
            background-color: {selected['backgroundColor']};
            color: {selected['textColor']};
            border-color: {selected['primaryColor']};
        }}
        .stSelectbox {{
            color: {selected['textColor']};
        }}
        .stSelectbox label {{
            color: {selected['textColor']} !important;
        }}
        .stTextInput {{
            color: {selected['textColor']};
        }}
        .stTextInput label {{
            color: {selected['textColor']} !important;
        }}
        .stTabs [role=tablist] button {{
            color: {selected['textColor']} !important;
        }}
        .stHeader {{
            background-color: {selected['backgroundColor']};
            color: {selected['textColor']};
        }}
        </style>
    """, unsafe_allow_html=True)
