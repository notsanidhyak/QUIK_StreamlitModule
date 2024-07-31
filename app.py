import os
import streamlit as st
from src.buildModel import *
from src.searchQuery import *
from src.utils import *
from subprocess import check_output
from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication, QFileDialog
load_dotenv()

st.set_page_config(page_title="QUIK", layout="wide", page_icon="📂")

# Initialize directories
model_dir = os.getenv('MODEL_DIR')

# st.write(st.session_state)

def display_results(smart_results_toggle, misspell_flag, scores, query, original_query, num_search_results=5, num_chars=200, context_window=400):
    """Display the search results in a tabular format."""
    if misspell_flag == 3:
        return

    try:
        num_search_results = min(num_search_results, len(scores))
        st.write(f"Searching for top {num_search_results} search results on \"{original_query}\"\n")
        scores = scores[:num_search_results]
        ct = len(scores)
        for (id, score) in scores: 
            if score != 0.0:
                ct-=1
                snippet = get_snippet(document_filenames[id], query, num_chars)
                if smart_results_toggle:
                    context = get_context(original_query, get_snippet(document_filenames[id], query, context_window))
                st.markdown("---")
                cols1, cols2 = st.columns([1, 1])
                cols1.write(f"📄 Document: {document_filenames[id]}")
                if cols2.button('Open Document', key=str(document_filenames[id])):
                    try:
                        check_output(f'start "" "{document_filenames[id]}"', shell=True)
                    except:
                        cols1.error("Document could not be opened.")
                st.write(f"🔢 Relevancy Score: {str(score)[:5]}")
                if smart_results_toggle:
                    st.write(f"💡 Smart Result: {context}")
                st.write(f"📚 Snippet: {snippet}\n")
        if ct == len(scores):
            st.warning("🟪 No search results found! Check for possible typos in your query.\n")
    except Exception as e:
        st.warning("Search Again!")

def search_bar():
    """Main function to display the search engine interface."""

    col1, col2 = st.columns([1, 1])
    col1.title("Search :blue[QUIK]")
    loginbutton(col2)

    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        # Admin panel
        st.write("**📜 System logs would appear here...**")
        st.markdown("---")
        if "recently_built" in st.session_state:
            st.success("Build logs saved to `buildLogs.txt`")
        st.sidebar.title("Build / Delete Models")
        st.sidebar.markdown("---")
        upload_section()
        st.sidebar.markdown("---")
        delete_section()

    else:
        # Search bar with spell checker and search results customization
        st.sidebar.header("🔍 Curate Search Results")
        st.sidebar.markdown("---")
        num_search_results = st.sidebar.slider(
            "Select max number of results to be shown",
            min_value=1,
            max_value=10,
            value=5,
            step=1)
        st.sidebar.markdown("---")
        num_chars = st.sidebar.slider(
            "Select number of chars in the search snippet",
            min_value=10,
            max_value=50,
            value=20,
            step=10
        )
        st.sidebar.markdown("---")
        smart_results_toggle = st.sidebar.toggle("Enable smart results (Beta)", True)
        context_window = 400
        if smart_results_toggle:
            context_window = st.sidebar.slider(
                "Select context window char size",
                min_value=100,
                max_value=1000,
                value=400,
                step=100
            )
        st.sidebar.markdown("---")
        spell_toggle = st.sidebar.toggle("Enable auto spell correct", True)
        st.sidebar.markdown("---")
        query = st.text_input("Enter your search query:", max_chars=500, placeholder="Press Search to see results...")
        misspell_flag = 1
        if query.strip() != "":
            if spell_toggle:
                misspell_flag, query = handle_misspell(query)

        # Search functionality
        if st.button("Search"):
            st.session_state["Search"] = True
            if query.strip() == "":
                st.warning("Please enter a query first.")
                st.markdown("---")
            else:
                st.subheader("Search Results")
                if spell_toggle:
                    try:
                        if misspell_flag==2:
                            st.markdown(f"*Did you mean: {query}?*")
                        elif misspell_flag==3:
                            st.warning(f"*Looks like there are some misspelled words in your query. Please try again!*")
                    except:
                        pass

        if "Search" in st.session_state and st.session_state["Search"]:
            scores, query_terms = do_search(query)
            if query.strip() != "":
                display_results(smart_results_toggle, misspell_flag, scores, query_terms, original_query=query, num_search_results=num_search_results, num_chars=num_chars, context_window=context_window)
                st.markdown("---")

def loginbutton(col2):
    """Display the login button on the top right corner of the page."""
    with col2:
        st.markdown("""
        <style>.element-container:has(#button-after) + div button {
            position: absolute;
            right: 0;
            top: 50%;
            transform: translateY(-50%);
        }</style>""", unsafe_allow_html=True)
        with col2:
            st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
            if "logged_in" in st.session_state and st.session_state["logged_in"]:
                if st.button('Back to Search', key="admin_logout_button"):
                    st.session_state.pop("logged_in")
                    st.rerun()
            else:
                if st.button('Load/Edit Model', key="load_model_button"):
                    if "trying_to_log_in" in st.session_state:
                        st.session_state.pop("trying_to_log_in")
                        st.rerun()
                    else:
                        login_sidebar()   
                        st.session_state["trying_to_log_in"] = True

def load_model_page():
    """Display the load model page in the sidebar."""
    list = os.listdir(f"{model_dir}User")
    st.session_state["model_name"] = st.sidebar.selectbox("Select model to load", list)
    load_model(user="User", model_name=st.session_state["model_name"])
    st.sidebar.success(f"📂 Model loaded: {st.session_state['model_name']}")
    st.sidebar.markdown("---")

def login_sidebar():
    """Display the login form in the sidebar."""
    st.sidebar.title("Load available models")
    load_model_page()
    st.sidebar.markdown("*Want to build/delete a model?*")
    if st.sidebar.button("Build/Delete Models", key="edit_button"):
        st.session_state["logged_in"] = True
        st.session_state.pop("trying_to_log_in")
        st.sidebar.empty()
        st.rerun()
    st.sidebar.markdown("---")

def upload_section():
    """Display the upload section for the video search engine."""
    st.sidebar.subheader("Build a new model")
    st.sidebar.write('Please select a folder for the model')

    if st.sidebar.button('Browse'):
        st.session_state["browse"] = True
        myapp = QApplication([])
        st.session_state["video_dir"] = QFileDialog.getExistingDirectory(None, "Select Directory")
        myapp.quit()

    # Display selected folder and model name input
    if "video_dir" in st.session_state:
        st.sidebar.text_input('Selected folder:', st.session_state["video_dir"], disabled=True)
        model_name = st.sidebar.text_input('Enter model name:', value="latest")
        
        # Handle empty model name
        if not model_name.strip():
            st.sidebar.error("Model name cannot be empty.")
        else:
            st.session_state["new_model_name"] = model_name
            
            # Build model if button is pressed
            if st.sidebar.button("Build Model", key="upload_button"):
                if not st.session_state["video_dir"]:
                    st.sidebar.error("Please select a folder first.")
                else:
                    buildpl = st.empty()
                    buildpl.warning("🚀 Building in progress...")
                    try:
                        if not model_name.endswith(".pkl"):
                            model_name += ".pkl"
                        initialize(st.session_state["video_dir"], model_name)
                        st.session_state["recently_built"] = True
                        st.success(f"✅ Model built successfully and saved at {model_dir}admin/{model_name}.pkl")
                    except Exception as e:
                        st.error(f"❌ Error building model: {e}")
                    finally:
                        buildpl.empty()
                        st.session_state.pop("video_dir", None)
                        st.rerun()
    
    if "recently_built" in st.session_state:
        if "first_build" in st.session_state:
            st.session_state.pop("first_build")
            st.rerun()
        st.success(f"✅ Model built successfully and saved as {st.session_state.get('new_model_name', 'latest')}.pkl")
        st.session_state.pop("recently_built")

def delete_section():
    """Display the delete section for the video search engine."""
    st.sidebar.subheader("Delete a model")
    st.sidebar.write('Please select a model to delete')

    list = os.listdir(f"{model_dir}User")
    st.session_state["model_name"] = st.sidebar.selectbox("Select model to delete", list)

    if st.sidebar.button("Delete Model", key="delete_button"):
        try:
            os.remove(f"{model_dir}User/{st.session_state['model_name']}")
            st.success(f"✅ Model deleted: {st.session_state['model_name']}")
        except Exception as e:
            st.error(f"❌ Error deleting model: {e}")
    st.sidebar.markdown("---")

def main():
    if "model_name" not in st.session_state:
        try:
            list = os.listdir(f"{model_dir}User")
            st.session_state["model_name"] = list[0]
            load_model(user="User", model_name=st.session_state["model_name"])
            st.success(f"📂 Model loaded: {st.session_state['model_name']}. To load another model click on 'Load Model' on the top-right!")
        except Exception as e:
            pass
                
    if "model_name" not in st.session_state or ("model_name" in st.session_state and st.session_state["model_name"] == None):
        st.title("Search :blue[QUIK]")
        st.markdown("---")
        st.subheader(f"Welcome to QUIK! 👋 Your Local Search Engine.")
        st.write("\n")
        st.markdown("*Begin by building your first model. Click on 'Build Model' below to get started!*")
        st.write("\n")
        if st.button("Build Model"):
            st.session_state["first_build"] = True
            st.rerun()
        st.markdown("---")
        st.markdown("<p style='text-align: center; color: grey;'>© Centum T&S 2024</p>", unsafe_allow_html=True)
    else:
        search_bar()

# Login session state initialization
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Handle login and admin panel
if "trying_to_log_in" in st.session_state:
    login_sidebar()

# Handle first build
if "first_build" in st.session_state and st.session_state["first_build"] == True:
    upload_section()

# Main function
main()