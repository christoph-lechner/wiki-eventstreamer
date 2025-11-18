import streamlit as st

st.set_page_config(page_title="Hello", page_icon=":material/waving_hand:")
st.title("Welcome to the Wiki Edits Analysis Dashboard")
st.write(
    """
    **👈 To explore Wiki Edits, select one panel from the sidebar**
    Available panels:
    * [Time Trend](/plot_timetrend)
    * [Breakdown](/edits_breakdown)
    * [Database Statistics](/db_stat)
    """
)

# Preload Python modules that take a while to compile in a new venv.
# Otherwise, when users switch to another page, it seems that Streamlit
# is slow, when in reality this is just an artifact of loading/compiling
# large modules from zero.
with st.spinner("Preloading Python modules for other pages..."):
    import numpy  # noqa: ICN001 F401
    import pandas  # noqa: ICN001 F401
