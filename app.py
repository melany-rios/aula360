import streamlit as st

from data.datos_prueba import cursos, alumnos


# Configuración de la página
st.set_page_config(
    page_title="Aula360",
    page_icon="🎓",
    layout="wide"
)


# Título principal
st.title("🎓 Aula360")
st.subheader("Sistema de gestión y seguimiento docente")

st.divider()


# Información general
st.write("### Resumen")

col1, col2 = st.columns(2)

with col1:
    st.metric("Cursos y materias", len(cursos))

with col2:
    st.metric("Alumnos registrados", len(alumnos))


st.divider()


# Cursos disponibles
st.write("### Mis cursos")

for curso in cursos:
    st.write(
        f"**{curso['curso']} — {curso['materia']}**"
    )
