import streamlit as st

from data.datos_prueba import cursos, alumnos


# ==========================================
# CONFIGURACIÓN
# ==========================================

st.set_page_config(
    page_title="Aula360",
    page_icon="🎓",
    layout="wide"
)


# ==========================================
# BARRA LATERAL
# ==========================================

st.sidebar.title("🎓 Aula360")
st.sidebar.caption("Gestión y seguimiento docente")

st.sidebar.divider()

pagina = st.sidebar.radio(
    "Menú principal",
    [
        "🏠 Inicio",
        "👥 Alumnos",
        "📅 Asistencia",
        "📝 Calificaciones",
        "📋 Observaciones",
        "📊 Estadísticas"
    ]
)

st.sidebar.divider()


# ==========================================
# SELECCIÓN DE CURSO Y MATERIA
# ==========================================

st.sidebar.subheader("Curso y materia")

opciones_cursos = [
    f"{curso['curso']} — {curso['materia']}"
    for curso in cursos
]

curso_seleccionado = st.sidebar.selectbox(
    "Seleccionar",
    opciones_cursos
)


# Buscar el curso seleccionado
curso_actual = next(
    curso
    for curso in cursos
    if f"{curso['curso']} — {curso['materia']}" == curso_seleccionado
)


# ==========================================
# ALUMNOS DEL CURSO SELECCIONADO
# ==========================================

alumnos_curso = [
    alumno
    for alumno in alumnos
    if alumno["curso_id"] == curso_actual["id"]
]


# ==========================================
# PÁGINA PRINCIPAL
# ==========================================

if pagina == "🏠 Inicio":

    st.title("🎓 Aula360")
    st.subheader("Sistema de gestión y seguimiento docente")

    st.divider()

    st.write(
        f"### {curso_actual['curso']} — {curso_actual['materia']}"
    )

    st.write(
        "Seleccioná una sección del menú para comenzar."
    )

    # Indicadores
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Alumnos",
            len(alumnos_curso)
        )

    with col2:
        st.metric(
            "Asistencia",
            "—"
        )

    with col3:
        st.metric(
            "Promedio",
            "—"
        )

    st.divider()

    st.write("### Accesos rápidos")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("📅 Registrar asistencia")

    with col2:
        st.info("📝 Registrar calificaciones")

    with col3:
        st.info("📋 Agregar observación")


# ==========================================
# ALUMNOS
# ==========================================

elif pagina == "👥 Alumnos":

    st.title("👥 Alumnos")

    st.subheader(
        f"{curso_actual['curso']} — {curso_actual['materia']}"
    )

    st.divider()

    if alumnos_curso:

        for alumno in alumnos_curso:

            st.write(
                f"**{alumno['apellido']}, {alumno['nombre']}**"
            )

    else:

        st.info(
            "No hay alumnos registrados para este curso."
        )


# ==========================================
# ASISTENCIA
# ==========================================

elif pagina == "📅 Asistencia":

    st.title("📅 Asistencia")

    st.subheader(
        f"{curso_actual['curso']} — {curso_actual['materia']}"
    )

    st.info(
        "El módulo de asistencia se desarrollará en el próximo paso."
    )


# ==========================================
# CALIFICACIONES
# ==========================================

elif pagina == "📝 Calificaciones":

    st.title("📝 Calificaciones")

    st.subheader(
        f"{curso_actual['curso']} — {curso_actual['materia']}"
    )

    st.info(
        "El módulo de calificaciones se desarrollará próximamente."
    )


# ==========================================
# OBSERVACIONES
# ==========================================

elif pagina == "📋 Observaciones":

    st.title("📋 Observaciones")

    st.subheader(
        f"{curso_actual['curso']} — {curso_actual['materia']}"
    )

    st.info(
        "El módulo de observaciones se desarrollará próximamente."
    )


# ==========================================
# ESTADÍSTICAS
# ==========================================

elif pagina == "📊 Estadísticas":

    st.title("📊 Estadísticas")

    st.subheader(
        f"{curso_actual['curso']} — {curso_actual['materia']}"
    )

    st.info(
        "El módulo de estadísticas se desarrollará próximamente."
    )
