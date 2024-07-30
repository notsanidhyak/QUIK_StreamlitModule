# import os
# import streamlit as st
# from src.buildModel import *
# from src.searchQuery import *
# from src.utils import *
# from subprocess import check_output
# from dotenv import load_dotenv
# import tkinter as tk
# from tkinter import filedialog
# load_dotenv()
# root = tk.Tk()
# root.withdraw()
# root.wm_attributes('-topmost', 1)

# st.set_page_config(page_title="QUIK", layout="wide", page_icon="📂")

# # Initialize directories
# model_dir = os.getenv('MODEL_DIR')

# # st.write(st.session_state)

# def display_results(smart_results_toggle, misspell_flag, scores, query, original_query, num_search_results=5, num_chars=200, context_window=400):
#     """Display the search results in a tabular format."""
#     if misspell_flag == 3:
#         return

#     num_search_results = min(num_search_results, len(scores))
#     st.write(f"Searching for top {num_search_results} search results on \"{original_query}\"\n")
#     scores = scores[:num_search_results]
#     ct = len(scores)
#     for (id, score) in scores: 
#         if score != 0.0:
#             ct-=1
#             snippet = get_snippet(document_filenames[id], query, num_chars)
#             if smart_results_toggle:
#                 context = get_context(original_query, get_snippet(document_filenames[id], query, context_window))
#             st.markdown("---")
#             cols1, cols2 = st.columns([1, 1])
#             cols1.write(f"📄 Document: {document_filenames[id]}")
#             if cols2.button('Open Document', key=str(document_filenames[id])):
#                 try:
#                     check_output(f'start "" "{document_filenames[id]}"', shell=True)
#                 except:
#                     cols1.error("Document could not be opened.")
#             st.write(f"🔢 Relevancy Score: {str(score)[:5]}")
#             if smart_results_toggle:
#                 st.write(f"💡 Smart Result: {context}")
#             st.write(f"📚 Snippet: {snippet}\n")
#     if ct == len(scores):
#         st.warning("🟪 No search results found! Check for possible typos in your query.\n")

# def search_bar():
#     """Main function to display the search engine interface."""
#     col1, col2 = st.columns([1, 1])
    
#     col1.title("Search :blue[QUIK]")
#     loginbutton(col2)
#     load_model()

#     if "logged_in" in st.session_state and st.session_state["logged_in"]:
#         # Admin panel
#         st.write("**📜 System logs would appear here...**")
#         st.markdown("---")
#         if "recently_built" in st.session_state:
#             st.success("Build logs saved to `buildLogs.txt`")
#         st.sidebar.title("Quik Admin Panel")
#         st.sidebar.write("🔓 Logged in as admin")
#         st.sidebar.markdown("---")
#         upload_section()
#         st.sidebar.markdown("---")

#     else:
#         # Search bar with spell checker and search results customization
#         st.sidebar.header("🔍 Curate Search Results")
#         st.sidebar.markdown("---")
#         num_search_results = st.sidebar.slider(
#             "Select max number of results to be shown",
#             min_value=1,
#             max_value=10,
#             value=5,
#             step=1)
#         st.sidebar.markdown("---")
#         num_chars = st.sidebar.slider(
#             "Select number of chars in the search snippet",
#             min_value=10,
#             max_value=50,
#             value=20,
#             step=10
#         )
#         st.sidebar.markdown("---")
#         smart_results_toggle = st.sidebar.toggle("Enable smart results (Beta)", True)
#         context_window = 400
#         if smart_results_toggle:
#             context_window = st.sidebar.slider(
#                 "Select context window char size",
#                 min_value=100,
#                 max_value=1000,
#                 value=400,
#                 step=100
#             )
#         st.sidebar.markdown("---")
#         spell_toggle = st.sidebar.toggle("Enable auto spell correct", True)
#         st.sidebar.markdown("---")
#         query = st.text_input("Enter your search query:", max_chars=500, placeholder="Press Search to see results...")
#         misspell_flag = 1
#         if query.strip() != "":
#             if spell_toggle:
#                 misspell_flag, query = handle_misspell(query)

#         # Search functionality
#         if st.button("Search"):
#             st.session_state["Search"] = True
#             if query.strip() == "":
#                 st.warning("Please enter a query first.")
#                 st.markdown("---")
#             else:
#                 st.subheader("Search Results")
#                 if spell_toggle:
#                     try:
#                         if misspell_flag==2:
#                             st.markdown(f"*Did you mean: {query}?*")
#                         elif misspell_flag==3:
#                             st.warning(f"*Looks like there are some misspelled words in your query. Please try again!*")
#                     except:
#                         pass

#         if "Search" in st.session_state and st.session_state["Search"]:
#             scores, query_terms = do_search(query)
#             display_results(smart_results_toggle, misspell_flag, scores, query_terms, original_query=query, num_search_results=num_search_results, num_chars=num_chars, context_window=context_window)
#             st.markdown("---")

# def loginbutton(col2):
#     """Display the login button on the top right corner of the page."""
#     with col2:
#         st.markdown("""
#         <style>.element-container:has(#button-after) + div button {
#             position: absolute;
#             right: 0;
#             top: 50%;
#             transform: translateY(-50%);
#         }</style>""", unsafe_allow_html=True)
#         with col2:
#             st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
#             if "logged_in" in st.session_state and st.session_state["logged_in"]:
#                 if st.button('Admin Logout', key="admin_logout_button"):
#                     st.session_state.pop("logged_in")
#                     st.rerun()
#             else:
#                 if st.button('Admin Login', key="admin_login_button"):
#                     if "trying_to_log_in" in st.session_state:
#                         st.session_state.pop("trying_to_log_in")
#                         st.rerun()
#                     else:
#                         login_sidebar()
#                         st.session_state["trying_to_log_in"] = True

# def login_sidebar():
#     """Display the login form in the sidebar."""
#     st.sidebar.title("Quik Admin Login")

#     username = st.sidebar.text_input("Username")
#     password = st.sidebar.text_input("Password", type="password")
#     if st.sidebar.button("Login"):
#         ADMIN_USER_ID = os.getenv('ADMIN_USER_ID')
#         ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
#         if username == ADMIN_USER_ID and password == ADMIN_PASSWORD:
#             st.session_state["logged_in"] = True
#             st.session_state.pop("trying_to_log_in")
#             st.sidebar.empty()
#             st.rerun()
#         else:
#             st.sidebar.error("🔐 Invalid username or password")

# def select_folder():
#    """TKinter dialog to select a folder."""
#    root = tk.Tk()
#    root.withdraw()
#    folder_path = filedialog.askdirectory(master=root)
#    root.destroy()
#    return folder_path

# def upload_section():
#     """Display the upload section for the video search engine."""
#     st.sidebar.subheader("Upload Folder to Database")
#     st.sidebar.write('Please select a folder for the model')

#     if st.sidebar.button('Browse'):
#         video_dir = filedialog.askdirectory(master=root)
#         if video_dir != "":
#             st.session_state["video_dir"] = video_dir
#             st.sidebar.text_input('Selected folder:', video_dir)
#         else:
#             st.session_state.pop("video_dir", None)
#             st.session_state.pop("recently_built", None)
#             st.sidebar.warning("Please select a folder first.") 

#     if "video_dir" in st.session_state:
#         if "recently_built" in st.session_state:
#             st.session_state.pop("recently_built")
#         if st.sidebar.button("Build Model", key="upload_button"):
#             buildpl = st.empty()
#             buildpl.warning("🚀 Building in progress...")
#             video_dir = st.session_state["video_dir"]
#             initialize(video_dir)
#             buildpl.empty()
#             st.session_state.pop("video_dir")
#             st.session_state["recently_built"] = True
#             st.rerun()
    
#     if "recently_built" in st.session_state:
#         st.sidebar.success(f"✅ Model built successfully and saved at {model_dir}admin/latest.pkl")

# # Login session state initialization
# if "logged_in" not in st.session_state:
#     st.session_state["logged_in"] = False

# # Handle login and admin panel
# if "trying_to_log_in" in st.session_state:
#     login_sidebar()

# search_bar() # Display the search bar (This handles the main functionality of the search engine)