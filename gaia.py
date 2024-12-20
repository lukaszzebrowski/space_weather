import streamlit as st
import streamlit.components.v1 as components

st.title("Test odliczania JS")

html_code = """
<h4 style='text-align: right;'>Kolejne odświeżenie za: <span id='countdown'>60</span>s</h4>
<script>
var timeleft = 60;
var downloadTimer = setInterval(function(){
    timeleft--;
    if (timeleft <= 0) {
        clearInterval(downloadTimer);
    }
    var el = document.getElementById("countdown");
    if (el) {
        el.textContent = timeleft;
    }
}, 1000);
</script>
"""

components.html(html_code, height=200)
