import streamlit as st
import pandas as pd
from datetime import date

from data.datos_prueba import (
    materias,
    cursos,
    asignaciones,
    alumnos,
    asistencias
)


# ==========================================
# CONFIGURACIÓN
# ==========================================

st.set_page_config(
    page_title="Aula360",
    page_icon="🎓",
    layout="wide"
)


# ==========================================
# INICIALIZAR DATOS EN SESSION STATE
# ==========================================

if "alumnos" not in st.session_state:
    st.session_state.alumnos = alumnos.copy()

if "asistencias" not in st.session_state:
    st.session_state.asistencias = asistencias.copy()

if "materias" not in st.session_state:
    st.session_state.materias = materias.copy()

if "cursos" not in st.session_state:
    st.session_state.cursos = cursos.copy()

if "asignaciones" not in st.session_state:
    st.session_state.asignaciones = asignaciones.copy()


# ==========================================
# FUNCIONES AUXILIARES
# ==========================================

def obtener_curso(asignacion_id):

    asignacion = next(
        asignacion
        for asignacion in st.session_state.asignaciones
        if asignacion["id"] == asignacion_id
    )

    curso = next(
        curso
        for curso in st.session_state.cursos
        if curso["id"] == asignacion["curso_id"]
    )

    return curso


def obtener_materia(asignacion_id):

    asignacion = next(
        asignacion
        for asignacion in st.session_state.asignaciones
        if asignacion["id"] == asignacion_id
    )

    materia = next(
        materia
        for materia in st.session_state.materias
        if materia["id"] == asignacion["materia_id"]
    )

    return materia


def obtener_alumnos_asignacion(asignacion_id):

    return [
        alumno
        for alumno in st.session_state.alumnos
        if alumno["asignacion_id"] == asignacion_id
    ]


def calcular_porcentaje_asistencia(alumno_id, asignacion_id):

    registros = [
        registro
        for registro in st.session_state.asistencias
        if registro["alumno_id"] == alumno_id
        and registro["asignacion_id"] == asignacion_id
    ]

    if not registros:
        return None

    presentes = sum(
        1
        for registro in registros
        if registro["estado"] == "presente"
    )

    justificados = sum(
        1
        for registro in registros
        if registro["estado"] == "justificado"
    )

    porcentaje = (
        (presentes + justificados)
        / len(registros)
    ) * 100

    return round(porcentaje, 1)


def obtener_nuevo_id(lista):

    ids = [
        elemento["id"]
        for elemento in lista
    ]

    return max(ids, default=0) + 1


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
        "⚙️ Administración",
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

opciones_asignaciones = {}

for asignacion in st.session_state.asignaciones:

    curso = obtener_curso(asignacion["id"])
    materia = obtener_materia(asignacion["id"])

    texto = f"{curso['nombre']} — {materia['nombre']}"

    opciones_asignaciones[texto] = asignacion["id"]


# Solo mostramos selector si existen asignaciones

if opciones_asignaciones:

    asignacion_seleccionada = st.sidebar.selectbox(
        "Seleccionar",
        list(opciones_asignaciones.keys())
    )

    asignacion_actual_id = opciones_asignaciones[
        asignacion_seleccionada
    ]

    curso_actual = obtener_curso(
        asignacion_actual_id
    )

    materia_actual = obtener_materia(
        asignacion_actual_id
    )

    alumnos_curso = obtener_alumnos_asignacion(
        asignacion_actual_id
    )

else:

    asignacion_actual_id = None
    curso_actual = None
    materia_actual = None
    alumnos_curso = []


# ==========================================
# INICIO
# ==========================================

if pagina == "🏠 Inicio":

    st.title("🎓 Aula360")
    st.subheader("Sistema de gestión y seguimiento docente")

    st.divider()

    if asignacion_actual_id is not None:

        st.write(
            f"### {curso_actual['nombre']} — "
            f"{materia_actual['nombre']}"
        )

        st.write(
            "Seleccioná una sección del menú para comenzar."
        )

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

    else:

        st.warning(
            "No hay cursos y materias asignados. "
            "Ingresá a Administración para comenzar."
        )


# ==========================================
# ADMINISTRACIÓN
# ==========================================

elif pagina == "⚙️ Administración":

    st.title("⚙️ Administración")

    st.write(
        "Desde esta sección podés administrar los cursos, "
        "las materias y las asignaciones de materias a cursos."
    )

    st.divider()

    pestaña_cursos, pestaña_materias, pestaña_asignaciones = st.tabs(
        [
            "🏫 Cursos",
            "📚 Materias",
            "🔗 Asignaciones"
        ]
    )


    # ======================================
    # CURSOS
    # ======================================

    with pestaña_cursos:

        st.subheader("🏫 Cursos")

        st.write(
            "Administrá los cursos que tenés a cargo."
        )

        st.divider()

        # AGREGAR CURSO

        with st.expander("➕ Agregar curso"):

            with st.form("form_agregar_curso"):

                nombre_curso = st.text_input(
                    "Nombre del curso",
                    placeholder="Ejemplo: 5° 2°"
                )

                guardar_curso = st.form_submit_button(
                    "Agregar curso"
                )

                if guardar_curso:

                    nombre_curso = nombre_curso.strip()

                    if not nombre_curso:

                        st.warning(
                            "Ingresá el nombre del curso."
                        )

                    else:

                        curso_existente = any(
                            curso["nombre"].lower()
                            == nombre_curso.lower()
                            for curso
                            in st.session_state.cursos
                        )

                        if curso_existente:

                            st.warning(
                                "Ese curso ya existe."
                            )

                        else:

                            nuevo_curso = {
                                "id": obtener_nuevo_id(
                                    st.session_state.cursos
                                ),
                                "nombre": nombre_curso
                            }

                            st.session_state.cursos.append(
                                nuevo_curso
                            )

                            st.success(
                                "Curso agregado correctamente."
                            )

                            st.rerun()


        st.divider()

        # LISTADO DE CURSOS

        st.write("### 📋 Cursos registrados")

        datos_cursos = []

        for curso in st.session_state.cursos:

            cantidad_asignaciones = sum(
                1
                for asignacion
                in st.session_state.asignaciones
                if asignacion["curso_id"] == curso["id"]
            )

            cantidad_alumnos = sum(
                len(
                    obtener_alumnos_asignacion(
                        asignacion["id"]
                    )
                )
                for asignacion
                in st.session_state.asignaciones
                if asignacion["curso_id"] == curso["id"]
            )

            datos_cursos.append(
                {
                    "ID": curso["id"],
                    "Curso": curso["nombre"],
                    "Materias": cantidad_asignaciones,
                    "Alumnos": cantidad_alumnos
                }
            )

        if datos_cursos:

            tabla_cursos = pd.DataFrame(
                datos_cursos
            )

            st.dataframe(
                tabla_cursos,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No hay cursos registrados."
            )


        st.divider()

        # MODIFICAR CURSO

        st.write("### ✏️ Modificar curso")

        if st.session_state.cursos:

            opciones_cursos = {
                curso["nombre"]: curso["id"]
                for curso
                in st.session_state.cursos
            }

            curso_seleccionado = st.selectbox(
                "Seleccionar curso",
                list(opciones_cursos.keys()),
                key="curso_modificar"
            )

            curso_id = opciones_cursos[
                curso_seleccionado
            ]

            curso_actual_admin = next(
                curso
                for curso
                in st.session_state.cursos
                if curso["id"] == curso_id
            )

            with st.form("form_modificar_curso"):

                nuevo_nombre_curso = st.text_input(
                    "Nombre del curso",
                    value=curso_actual_admin["nombre"]
                )

                modificar_curso = st.form_submit_button(
                    "Guardar cambios"
                )

                if modificar_curso:

                    nuevo_nombre_curso = (
                        nuevo_nombre_curso.strip()
                    )

                    if not nuevo_nombre_curso:

                        st.warning(
                            "El nombre no puede quedar vacío."
                        )

                    else:

                        curso_existente = any(
                            curso["id"] != curso_id
                            and curso["nombre"].lower()
                            == nuevo_nombre_curso.lower()
                            for curso
                            in st.session_state.cursos
                        )

                        if curso_existente:

                            st.warning(
                                "Ya existe otro curso con ese nombre."
                            )

                        else:

                            curso_actual_admin[
                                "nombre"
                            ] = nuevo_nombre_curso

                            st.success(
                                "Curso modificado correctamente."
                            )

                            st.rerun()


        st.divider()

        # ELIMINAR CURSO

        st.write("### 🗑️ Eliminar curso")

        if st.session_state.cursos:

            st.warning(
                "Al eliminar un curso también se eliminarán "
                "sus asignaciones. Los alumnos asociados "
                "a esas asignaciones también serán eliminados."
            )

            curso_eliminar_nombre = st.selectbox(
                "Seleccionar curso a eliminar",
                list(opciones_cursos.keys()),
                key="curso_eliminar"
            )

            curso_eliminar_id = opciones_cursos[
                curso_eliminar_nombre
            ]

            confirmar_curso = st.checkbox(
                "Confirmo que quiero eliminar este curso",
                key="confirmar_eliminar_curso"
            )

            if st.button(
                "🗑️ Eliminar curso",
                key="boton_eliminar_curso"
            ):

                if confirmar_curso:

                    asignaciones_eliminar = [
                        asignacion["id"]
                        for asignacion
                        in st.session_state.asignaciones
                        if asignacion["curso_id"]
                        == curso_eliminar_id
                    ]

                    st.session_state.asignaciones = [
                        asignacion
                        for asignacion
                        in st.session_state.asignaciones
                        if asignacion["curso_id"]
                        != curso_eliminar_id
                    ]

                    st.session_state.alumnos = [
                        alumno
                        for alumno
                        in st.session_state.alumnos
                        if alumno["asignacion_id"]
                        not in asignaciones_eliminar
                    ]

                    st.session_state.asistencias = [
                        registro
                        for registro
                        in st.session_state.asistencias
                        if registro["asignacion_id"]
                        not in asignaciones_eliminar
                    ]

                    st.session_state.cursos = [
                        curso
                        for curso
                        in st.session_state.cursos
                        if curso["id"] != curso_eliminar_id
                    ]

                    st.success(
                        "Curso eliminado correctamente."
                    )

                    st.rerun()

                else:

                    st.warning(
                        "Confirmá la eliminación."
                    )


    # ======================================
    # MATERIAS
    # ======================================

    with pestaña_materias:

        st.subheader("📚 Materias")

        st.write(
            "Administrá las materias que dictás."
        )

        st.divider()

        # AGREGAR MATERIA

        with st.expander("➕ Agregar materia"):

            with st.form("form_agregar_materia"):

                nombre_materia = st.text_input(
                    "Nombre de la materia",
                    placeholder="Ejemplo: Programación"
                )

                guardar_materia = st.form_submit_button(
                    "Agregar materia"
                )

                if guardar_materia:

                    nombre_materia = (
                        nombre_materia.strip()
                    )

                    if not nombre_materia:

                        st.warning(
                            "Ingresá el nombre de la materia."
                        )

                    else:

                        materia_existente = any(
                            materia["nombre"].lower()
                            == nombre_materia.lower()
                            for materia
                            in st.session_state.materias
                        )

                        if materia_existente:

                            st.warning(
                                "Esa materia ya existe."
                            )

                        else:

                            nueva_materia = {
                                "id": obtener_nuevo_id(
                                    st.session_state.materias
                                ),
                                "nombre": nombre_materia
                            }

                            st.session_state.materias.append(
                                nueva_materia
                            )

                            st.success(
                                "Materia agregada correctamente."
                            )

                            st.rerun()


        st.divider()

        # LISTADO DE MATERIAS

        st.write("### 📋 Materias registradas")

        datos_materias = []

        for materia in st.session_state.materias:

            cantidad_asignaciones = sum(
                1
                for asignacion
                in st.session_state.asignaciones
                if asignacion["materia_id"]
                == materia["id"]
            )

            datos_materias.append(
                {
                    "ID": materia["id"],
                    "Materia": materia["nombre"],
                    "Cursos": cantidad_asignaciones
                }
            )

        if datos_materias:

            tabla_materias = pd.DataFrame(
                datos_materias
            )

            st.dataframe(
                tabla_materias,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No hay materias registradas."
            )


        st.divider()

        # MODIFICAR MATERIA

        st.write("### ✏️ Modificar materia")

        if st.session_state.materias:

            opciones_materias = {
                materia["nombre"]: materia["id"]
                for materia
                in st.session_state.materias
            }

            materia_seleccionada = st.selectbox(
                "Seleccionar materia",
                list(opciones_materias.keys()),
                key="materia_modificar"
            )

            materia_id = opciones_materias[
                materia_seleccionada
            ]

            materia_actual_admin = next(
                materia
                for materia
                in st.session_state.materias
                if materia["id"] == materia_id
            )

            with st.form("form_modificar_materia"):

                nuevo_nombre_materia = st.text_input(
                    "Nombre de la materia",
                    value=materia_actual_admin["nombre"]
                )

                modificar_materia = st.form_submit_button(
                    "Guardar cambios"
                )

                if modificar_materia:

                    nuevo_nombre_materia = (
                        nuevo_nombre_materia.strip()
                    )

                    if not nuevo_nombre_materia:

                        st.warning(
                            "El nombre no puede quedar vacío."
                        )

                    else:

                        materia_existente = any(
                            materia["id"] != materia_id
                            and materia["nombre"].lower()
                            == nuevo_nombre_materia.lower()
                            for materia
                            in st.session_state.materias
                        )

                        if materia_existente:

                            st.warning(
                                "Ya existe otra materia con ese nombre."
                            )

                        else:

                            materia_actual_admin[
                                "nombre"
                            ] = nuevo_nombre_materia

                            st.success(
                                "Materia modificada correctamente."
                            )

                            st.rerun()


        st.divider()

        # ELIMINAR MATERIA

        st.write("### 🗑️ Eliminar materia")

        if st.session_state.materias:

            st.warning(
                "Si eliminás una materia, también se eliminarán "
                "sus asignaciones y los alumnos asociados."
            )

            materia_eliminar_nombre = st.selectbox(
                "Seleccionar materia a eliminar",
                list(opciones_materias.keys()),
                key="materia_eliminar"
            )

            materia_eliminar_id = opciones_materias[
                materia_eliminar_nombre
            ]

            confirmar_materia = st.checkbox(
                "Confirmo que quiero eliminar esta materia",
                key="confirmar_eliminar_materia"
            )

            if st.button(
                "🗑️ Eliminar materia",
                key="boton_eliminar_materia"
            ):

                if confirmar_materia:

                    asignaciones_eliminar = [
                        asignacion["id"]
                        for asignacion
                        in st.session_state.asignaciones
                        if asignacion["materia_id"]
                        == materia_eliminar_id
                    ]

                    st.session_state.asignaciones = [
                        asignacion
                        for asignacion
                        in st.session_state.asignaciones
                        if asignacion["materia_id"]
                        != materia_eliminar_id
                    ]

                    st.session_state.alumnos = [
                        alumno
                        for alumno
                        in st.session_state.alumnos
                        if alumno["asignacion_id"]
                        not in asignaciones_eliminar
                    ]

                    st.session_state.asistencias = [
                        registro
                        for registro
                        in st.session_state.asistencias
                        if registro["asignacion_id"]
                        not in asignaciones_eliminar
                    ]

                    st.session_state.materias = [
                        materia
                        for materia
                        in st.session_state.materias
                        if materia["id"] != materia_eliminar_id
                    ]

                    st.success(
                        "Materia eliminada correctamente."
                    )

                    st.rerun()

                else:

                    st.warning(
                        "Confirmá la eliminación."
                    )


    # ======================================
    # ASIGNACIONES
    # ======================================

    with pestaña_asignaciones:

        st.subheader("🔗 Asignaciones")

        st.write(
            "Una asignación relaciona un curso con una materia. "
            "Por ejemplo: 5° 1° — Sistemas Informáticos."
        )

        st.divider()

        # AGREGAR ASIGNACIÓN

        with st.expander("➕ Asignar materia a un curso"):

            if (
                st.session_state.cursos
                and st.session_state.materias
            ):

                opciones_cursos_asignacion = {
                    curso["nombre"]: curso["id"]
                    for curso
                    in st.session_state.cursos
                }

                opciones_materias_asignacion = {
                    materia["nombre"]: materia["id"]
                    for materia
                    in st.session_state.materias
                }

                with st.form(
                    "form_agregar_asignacion"
                ):

                    curso_asignacion = st.selectbox(
                        "Curso",
                        list(
                            opciones_cursos_asignacion.keys()
                        )
                    )

                    materia_asignacion = st.selectbox(
                        "Materia",
                        list(
                            opciones_materias_asignacion.keys()
                        )
                    )

                    guardar_asignacion = st.form_submit_button(
                        "Crear asignación"
                    )

                    if guardar_asignacion:

                        curso_id = (
                            opciones_cursos_asignacion[
                                curso_asignacion
                            ]
                        )

                        materia_id = (
                            opciones_materias_asignacion[
                                materia_asignacion
                            ]
                        )

                        asignacion_existente = any(
                            asignacion["curso_id"]
                            == curso_id
                            and asignacion["materia_id"]
                            == materia_id
                            for asignacion
                            in st.session_state.asignaciones
                        )

                        if asignacion_existente:

                            st.warning(
                                "Esa materia ya está asignada "
                                "a ese curso."
                            )

                        else:

                            nueva_asignacion = {
                                "id": obtener_nuevo_id(
                                    st.session_state.asignaciones
                                ),
                                "curso_id": curso_id,
                                "materia_id": materia_id
                            }

                            st.session_state.asignaciones.append(
                                nueva_asignacion
                            )

                            st.success(
                                "Asignación creada correctamente."
                            )

                            st.rerun()

            else:

                st.info(
                    "Primero necesitás tener al menos "
                    "un curso y una materia."
                )


        st.divider()

        # LISTADO DE ASIGNACIONES

        st.write("### 📋 Asignaciones actuales")

        datos_asignaciones = []

        for asignacion in st.session_state.asignaciones:

            curso = obtener_curso(
                asignacion["id"]
            )

            materia = obtener_materia(
                asignacion["id"]
            )

            cantidad_alumnos = len(
                obtener_alumnos_asignacion(
                    asignacion["id"]
                )
            )

            datos_asignaciones.append(
                {
                    "ID": asignacion["id"],
                    "Curso": curso["nombre"],
                    "Materia": materia["nombre"],
                    "Alumnos": cantidad_alumnos
                }
            )

        if datos_asignaciones:

            tabla_asignaciones = pd.DataFrame(
                datos_asignaciones
            )

            st.dataframe(
                tabla_asignaciones,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No hay asignaciones registradas."
            )


        st.divider()

        # ELIMINAR ASIGNACIÓN

        st.write("### 🗑️ Eliminar asignación")

        if st.session_state.asignaciones:

            opciones_eliminar_asignacion = {}

            for asignacion in st.session_state.asignaciones:

                curso = obtener_curso(
                    asignacion["id"]
                )

                materia = obtener_materia(
                    asignacion["id"]
                )

                texto = (
                    f"{curso['nombre']} — "
                    f"{materia['nombre']}"
                )

                opciones_eliminar_asignacion[
                    texto
                ] = asignacion["id"]

            asignacion_eliminar_nombre = st.selectbox(
                "Seleccionar asignación",
                list(
                    opciones_eliminar_asignacion.keys()
                ),
                key="asignacion_eliminar"
            )

            asignacion_eliminar_id = (
                opciones_eliminar_asignacion[
                    asignacion_eliminar_nombre
                ]
            )

            alumnos_asignacion_eliminar = (
                obtener_alumnos_asignacion(
                    asignacion_eliminar_id
                )
            )

            if alumnos_asignacion_eliminar:

                st.warning(
                    f"Esta asignación tiene "
                    f"{len(alumnos_asignacion_eliminar)} "
                    "alumnos asociados. "
                    "Al eliminarla también se eliminarán "
                    "esos alumnos y sus asistencias."
                )

            confirmar_asignacion = st.checkbox(
                "Confirmo que quiero eliminar esta asignación",
                key="confirmar_eliminar_asignacion"
            )

            if st.button(
                "🗑️ Eliminar asignación",
                key="boton_eliminar_asignacion"
            ):

                if confirmar_asignacion:

                    st.session_state.asignaciones = [
                        asignacion
                        for asignacion
                        in st.session_state.asignaciones
                        if asignacion["id"]
                        != asignacion_eliminar_id
                    ]

                    st.session_state.alumnos = [
                        alumno
                        for alumno
                        in st.session_state.alumnos
                        if alumno["asignacion_id"]
                        != asignacion_eliminar_id
                    ]

                    st.session_state.asistencias = [
                        registro
                        for registro
                        in st.session_state.asistencias
                        if registro["asignacion_id"]
                        != asignacion_eliminar_id
                    ]

                    st.success(
                        "Asignación eliminada correctamente."
                    )

                    st.rerun()

                else:

                    st.warning(
                        "Confirmá la eliminación."
                    )


# ==========================================
# ALUMNOS
# ==========================================

elif pagina == "👥 Alumnos":

    if asignacion_actual_id is None:

        st.warning(
            "No hay ninguna asignación disponible."
        )

    else:

        st.title("👥 Alumnos")

        st.subheader(
            f"{curso_actual['nombre']} — "
            f"{materia_actual['nombre']}"
        )

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Total de alumnos",
                len(alumnos_curso)
            )

        with col2:
            st.metric(
                "Materia",
                materia_actual["nombre"]
            )

        st.divider()

        # AGREGAR ALUMNO

        with st.expander("➕ Agregar alumno"):

            with st.form("form_agregar_alumno"):

                nombre = st.text_input("Nombre")

                apellido = st.text_input("Apellido")

                guardar = st.form_submit_button(
                    "Agregar alumno"
                )

                if guardar:

                    if nombre.strip() and apellido.strip():

                        ids = [
                            alumno["id"]
                            for alumno
                            in st.session_state.alumnos
                        ]

                        nuevo_id = max(
                            ids,
                            default=0
                        ) + 1

                        nuevo_alumno = {
                            "id": nuevo_id,
                            "nombre": nombre.strip(),
                            "apellido": apellido.strip(),
                            "asignacion_id":
                                asignacion_actual_id
                        }

                        st.session_state.alumnos.append(
                            nuevo_alumno
                        )

                        st.success(
                            "Alumno agregado correctamente."
                        )

                        st.rerun()

                    else:

                        st.warning(
                            "Completá nombre y apellido."
                        )

        st.divider()

        # BUSCADOR

        st.write("### 🔎 Buscar alumno")

        texto_busqueda = st.text_input(
            "Ingresá nombre o apellido",
            placeholder="Ejemplo: Gómez"
        )

        alumnos_filtrados = alumnos_curso

        if texto_busqueda:

            texto_busqueda = (
                texto_busqueda.lower()
            )

            alumnos_filtrados = [
                alumno
                for alumno in alumnos_curso
                if texto_busqueda
                in alumno["nombre"].lower()
                or texto_busqueda
                in alumno["apellido"].lower()
            ]

        # LISTADO

        st.write("### 📋 Listado de alumnos")

        if alumnos_filtrados:

            datos_tabla = [
                {
                    "ID": alumno["id"],
                    "Apellido": alumno["apellido"],
                    "Nombre": alumno["nombre"]
                }
                for alumno in alumnos_filtrados
            ]

            tabla_alumnos = pd.DataFrame(
                datos_tabla
            )

            st.dataframe(
                tabla_alumnos,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.warning(
                "No se encontraron alumnos."
            )

        st.divider()

        # MODIFICAR / ELIMINAR

        st.write("### ⚙️ Administrar alumno")

        if alumnos_curso:

            opciones_alumnos = {
                f"{alumno['apellido']}, "
                f"{alumno['nombre']}":
                alumno["id"]
                for alumno in alumnos_curso
            }

            alumno_seleccionado = st.selectbox(
                "Seleccionar alumno",
                list(opciones_alumnos.keys()),
                key="alumno_admin"
            )

            alumno_id = opciones_alumnos[
                alumno_seleccionado
            ]

            alumno_actual = next(
                alumno
                for alumno
                in st.session_state.alumnos
                if alumno["id"] == alumno_id
            )

            col1, col2 = st.columns(2)

            # MODIFICAR

            with col1:

                st.write("#### ✏️ Modificar")

                with st.form(
                    "form_modificar_alumno"
                ):

                    nuevo_nombre = st.text_input(
                        "Nombre",
                        value=alumno_actual["nombre"]
                    )

                    nuevo_apellido = st.text_input(
                        "Apellido",
                        value=alumno_actual["apellido"]
                    )

                    modificar = st.form_submit_button(
                        "Guardar cambios"
                    )

                    if modificar:

                        if (
                            nuevo_nombre.strip()
                            and nuevo_apellido.strip()
                        ):

                            alumno_actual["nombre"] = (
                                nuevo_nombre.strip()
                            )

                            alumno_actual["apellido"] = (
                                nuevo_apellido.strip()
                            )

                            st.success(
                                "Datos modificados correctamente."
                            )

                            st.rerun()

                        else:

                            st.warning(
                                "Completá nombre y apellido."
                            )

            # ELIMINAR

            with col2:

                st.write("#### 🗑️ Eliminar")

                st.warning(
                    "Esta acción eliminará al alumno "
                    "del listado de esta materia."
                )

                confirmar = st.checkbox(
                    "Confirmo que quiero eliminar este alumno",
                    key="confirmar_eliminar"
                )

                if st.button(
                    "Eliminar alumno",
                    type="secondary"
                ):

                    if confirmar:

                        st.session_state.alumnos = [
                            alumno
                            for alumno
                            in st.session_state.alumnos
                            if alumno["id"] != alumno_id
                        ]

                        st.session_state.asistencias = [
                            registro
                            for registro
                            in st.session_state.asistencias
                            if registro["alumno_id"]
                            != alumno_id
                        ]

                        st.success(
                            "Alumno eliminado correctamente."
                        )

                        st.rerun()

                    else:

                        st.warning(
                            "Confirmá la eliminación."
                        )

        else:

            st.info(
                "No hay alumnos registrados."
            )


# ==========================================
# ASISTENCIA
# ==========================================

elif pagina == "📅 Asistencia":

    if asignacion_actual_id is None:

        st.warning(
            "No hay ninguna asignación disponible."
        )

    else:

        st.title("📅 Asistencia")

        st.subheader(
            f"{curso_actual['nombre']} — "
            f"{materia_actual['nombre']}"
        )

        st.divider()

        fecha_asistencia = st.date_input(
            "Fecha",
            value=date.today()
        )

        st.write("### Registrar asistencia")

        if alumnos_curso:

            estados = [
                "Presente",
                "Ausente",
                "Justificado"
            ]

            registros_asistencia = []

            for alumno in alumnos_curso:

                estado_actual = "Presente"

                registros_existentes = [
                    registro
                    for registro
                    in st.session_state.asistencias
                    if registro["alumno_id"]
                    == alumno["id"]
                    and registro["asignacion_id"]
                    == asignacion_actual_id
                    and registro["fecha"]
                    == str(fecha_asistencia)
                ]

                if registros_existentes:

                    estado_guardado = (
                        registros_existentes[0]["estado"]
                    )

                    if estado_guardado == "ausente":

                        estado_actual = "Ausente"

                    elif estado_guardado == "justificado":

                        estado_actual = "Justificado"

                registros_asistencia.append(
                    {
                        "alumno": alumno,
                        "estado": estado_actual
                    }
                )

            with st.form("form_asistencia"):

                nuevos_estados = {}

                for registro in registros_asistencia:

                    alumno = registro["alumno"]

                    nuevos_estados[
                        alumno["id"]
                    ] = st.selectbox(
                        alumno["apellido"]
                        + ", "
                        + alumno["nombre"],
                        estados,
                        index=estados.index(
                            registro["estado"]
                        ),
                        key=f"asistencia_"
                        f"{alumno['id']}"
                    )

                guardar_asistencia = (
                    st.form_submit_button(
                        "💾 Guardar asistencia"
                    )
                )

                if guardar_asistencia:

                    for alumno in alumnos_curso:

                        estado_texto = nuevos_estados[
                            alumno["id"]
                        ]

                        if estado_texto == "Presente":

                            estado = "presente"

                        elif estado_texto == "Ausente":

                            estado = "ausente"

                        else:

                            estado = "justificado"

                        registro_existente = next(
                            (
                                registro
                                for registro
                                in st.session_state.asistencias
                                if registro["alumno_id"]
                                == alumno["id"]
                                and registro["asignacion_id"]
                                == asignacion_actual_id
                                and registro["fecha"]
                                == str(fecha_asistencia)
                            ),
                            None
                        )

                        if registro_existente:

                            registro_existente[
                                "estado"
                            ] = estado

                        else:

                            nuevo_id = (
                                obtener_nuevo_id(
                                    st.session_state.asistencias
                                )
                            )

                            st.session_state.asistencias.append(
                                {
                                    "id": nuevo_id,
                                    "alumno_id":
                                        alumno["id"],
                                    "asignacion_id":
                                        asignacion_actual_id,
                                    "fecha":
                                        str(
                                            fecha_asistencia
                                        ),
                                    "estado": estado
                                }
                            )

                    st.success(
                        "Asistencia guardada correctamente."
                    )

                    st.rerun()

            st.divider()

            st.write(
                "### 📊 Porcentaje de asistencia"
            )

            datos_asistencia = []

            for alumno in alumnos_curso:

                porcentaje = (
                    calcular_porcentaje_asistencia(
                        alumno["id"],
                        asignacion_actual_id
                    )
                )

                if porcentaje is None:

                    porcentaje_texto = (
                        "Sin registros"
                    )

                else:

                    porcentaje_texto = (
                        f"{porcentaje}%"
                    )

                datos_asistencia.append(
                    {
                        "Apellido":
                            alumno["apellido"],
                        "Nombre":
                            alumno["nombre"],
                        "Asistencia":
                            porcentaje_texto
                    }
                )

            tabla_asistencia = pd.DataFrame(
                datos_asistencia
            )

            st.dataframe(
                tabla_asistencia,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No hay alumnos registrados "
                "para esta materia."
            )


# ==========================================
# CALIFICACIONES
# ==========================================

elif pagina == "📝 Calificaciones":

    if asignacion_actual_id is None:

        st.warning(
            "No hay ninguna asignación disponible."
        )

    else:

        st.title("📝 Calificaciones")

        st.subheader(
            f"{curso_actual['nombre']} — "
            f"{materia_actual['nombre']}"
        )

        st.divider()

        st.info(
            "El módulo de calificaciones "
            "se desarrollará próximamente."
        )


# ==========================================
# OBSERVACIONES
# ==========================================

elif pagina == "📋 Observaciones":

    if asignacion_actual_id is None:

        st.warning(
            "No hay ninguna asignación disponible."
        )

    else:

        st.title("📋 Observaciones")

        st.subheader(
            f"{curso_actual['nombre']} — "
            f"{materia_actual['nombre']}"
        )

        st.divider()

        st.info(
            "El módulo de observaciones "
            "se desarrollará próximamente."
        )


# ==========================================
# ESTADÍSTICAS
# ==========================================

elif pagina == "📊 Estadísticas":

    if asignacion_actual_id is None:

        st.warning(
            "No hay ninguna asignación disponible."
        )

    else:

        st.title("📊 Estadísticas")

        st.subheader(
            f"{curso_actual['nombre']} — "
            f"{materia_actual['nombre']}"
        )

        st.divider()

        st.info(
            "El módulo de estadísticas "
            "se desarrollará próximamente."
        )
