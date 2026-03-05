# streamlit run app.py
import streamlit as st
from graph_reasoning.reas import get_labels_dict, get_results

@st.cache_data
def make_opts():
    dict_labels = get_labels_dict()
    
    return dict_labels


dict_labels = make_opts()


st.title("Get connection between the following entities:")

opts = list(dict_labels.keys())

a = st.selectbox("Entity 1 (Person / Place / Institution / Book)", options=opts, index=None, placeholder="Choose Initial Entity...")
b = st.selectbox("Entity 2 (Person / Place / Institution / Book)", options=opts, index=None, placeholder="Choose Final Entity...")

run = st.button("Run")

# Output textbox
result_placeholder = st.empty()

if run:
    if a is None or b is None:
        result_placeholder.text_area("Result", "Pick both values first.", height=180)
    elif a == b:
        result_placeholder.text_area("Result", "Pick two different values.", height=180)
    else:
        # Shrink list after successful use
        st.session_state.options = [x for x in opts if x not in (a, b)]
        result_placeholder.text_area("Result","processing...", height=180)
        res_md = get_results(a, b)  # make sure this returns a Markdown string
        with result_placeholder.container():
            st.markdown(res_md)  # render as Markdown [web:1]
else:
    result_placeholder.text_area("Result", "", height=180)
