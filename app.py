import streamlit as st
import pandas as pd

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

    # ------------------------------------------
    # INFORMACIÓN GENERAL
    # ------------------------------------------

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Total de alumnos",
            len(alumnos_curso)
        )

    with col2:
        st.metric(
            "Curso",
            curso_actual["curso"]
        )

    st.divider()

    # ------------------------------------------
    # BUSCADOR
    # ------------------------------------------

    st.write("### 🔎 Buscar alumno")

    texto_busqueda = st.text_input(
        "Ingresá nombre o apellido",
        placeholder="Ejemplo: Gómez"
    )

    # Filtrar alumnos
    alumnos_filtrados = alumnos_curso

    if texto_busqueda:

        texto_busqueda = texto_busqueda.lower()

        alumnos_filtrados = [
            alumno
            for alumno in alumnos_curso
            if texto_busqueda in alumno["nombre"].lower()
            or texto_busqueda in alumno["apellido"].lower()
        ]

    # ------------------------------------------
    # LISTADO
    # ------------------------------------------

   if alumnos_filtrados:

    datos_tabla = [
        {
            "Apellido": alumno["apellido"],
            "Nombre": alumno["nombre"]
        }
        for alumno in alumnos_filtrados
    ]

    tabla_alumnos = pd.DataFrame(datos_tabla)

    st.dataframe(
        tabla_alumnos,
        use_container_width=True,
        hide_index=True
    )

    # ------------------------------------------
    # FICHA DEL ALUMNO
    # ------------------------------------------

    st.write("### 👤 Ficha del alumno")

    if alumnos_curso:

        opciones_alumnos = [
            f"{alumno['apellido']}, {alumno['nombre']}"
            for alumno in alumnos_curso
        ]

        alumno_seleccionado = st.selectbox(
            "Seleccionar alumno",
            opciones_alumnos
        )

        # Buscar alumno
        alumno_actual = next(
            alumno
            for alumno in alumnos_curso
            if f"{alumno['apellido']}, {alumno['nombre']}"
            == alumno_seleccionado
        )

        st.write(
            f"## {alumno_actual['nombre']} "
            f"{alumno_actual['apellido']}"
        )

        st.caption(
            f"{curso_actual['curso']} — "
            f"{curso_actual['materia']}"
        )

        st.divider()

        # Indicadores del alumno
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Asistencia",
                "—"
            )

        with col2:
            st.metric(
                "Promedio",
                "—"
            )

        with col3:
            st.metric(
                "Trabajos",
                "—"
            )

        with col4:
            st.metric(
                "Observaciones",
                "—"
            )

    else:

        st.info(
            "No hay alumnos registrados."
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
