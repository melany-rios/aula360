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

    # Los presentes y justificados cuentan como asistencia
    porcentaje = (
        (presentes + justificados)
        / len(registros)
    ) * 100

    return round(porcentaje, 1)


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

opciones_asignaciones = {}

for asignacion in st.session_state.asignaciones:

    curso = obtener_curso(asignacion["id"])
    materia = obtener_materia(asignacion["id"])

    texto = f"{curso['nombre']} — {materia['nombre']}"

    opciones_asignaciones[texto] = asignacion["id"]


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


# ==========================================
# INICIO
# ==========================================

if pagina == "🏠 Inicio":

    st.title("🎓 Aula360")
    st.subheader("Sistema de gestión y seguimiento docente")

    st.divider()

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


# ==========================================
# ALUMNOS
# ==========================================

elif pagina == "👥 Alumnos":

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

    # ------------------------------------------
    # AGREGAR ALUMNO
    # ------------------------------------------

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
                        for alumno in st.session_state.alumnos
                    ]

                    nuevo_id = max(ids, default=0) + 1

                    nuevo_alumno = {
                        "id": nuevo_id,
                        "nombre": nombre.strip(),
                        "apellido": apellido.strip(),
                        "asignacion_id": asignacion_actual_id
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

    # ------------------------------------------
    # BUSCADOR
    # ------------------------------------------

    st.write("### 🔎 Buscar alumno")

    texto_busqueda = st.text_input(
        "Ingresá nombre o apellido",
        placeholder="Ejemplo: Gómez"
    )

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

        tabla_alumnos = pd.DataFrame(datos_tabla)

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

    # ------------------------------------------
    # MODIFICAR / ELIMINAR
    # ------------------------------------------

    st.write("### ⚙️ Administrar alumno")

    if alumnos_curso:

        opciones_alumnos = {
            f"{alumno['apellido']}, {alumno['nombre']}": alumno["id"]
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
            for alumno in st.session_state.alumnos
            if alumno["id"] == alumno_id
        )

        col1, col2 = st.columns(2)

        # --------------------------------------
        # MODIFICAR
        # --------------------------------------

        with col1:

            st.write("#### ✏️ Modificar")

            with st.form("form_modificar_alumno"):

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

        # --------------------------------------
        # ELIMINAR
        # --------------------------------------

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
                        for alumno in st.session_state.alumnos
                        if alumno["id"] != alumno_id
                    ]

                    # También eliminamos sus asistencias
                    st.session_state.asistencias = [
                        registro
                        for registro in st.session_state.asistencias
                        if registro["alumno_id"] != alumno_id
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

    # ==========================================
    # ASISTENCIA
    # ==========================================

    if pagina == "📅 Asistencia":

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
                    for registro in st.session_state.asistencias
                    if registro["alumno_id"] == alumno["id"]
                    and registro["asignacion_id"] == asignacion_actual_id
                    and registro["fecha"] == str(fecha_asistencia)
                ]

                if registros_existentes:

                    estado_guardado = registros_existentes[0]["estado"]

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

                    nuevos_estados[alumno["id"]] = st.selectbox(
                        alumno["apellido"] + ", "
                        + alumno["nombre"],
                        estados,
                        index=estados.index(
                            registro["estado"]
                        ),
                        key=f"asistencia_{alumno['id']}"
                    )

                guardar_asistencia = st.form_submit_button(
                    "💾 Guardar asistencia"
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

                        # Buscar registro existente
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

                            registro_existente["estado"] = estado

                        else:

                            ids = [
                                registro["id"]
                                for registro
                                in st.session_state.asistencias
                            ]

                            nuevo_id = max(
                                ids,
                                default=0
                            ) + 1

                            st.session_state.asistencias.append(
                                {
                                    "id": nuevo_id,
                                    "alumno_id": alumno["id"],
                                    "asignacion_id": asignacion_actual_id,
                                    "fecha": str(fecha_asistencia),
                                    "estado": estado
                                }
                            )

                    st.success(
                        "Asistencia guardada correctamente."
                    )

                    st.rerun()

            st.divider()

            # --------------------------------------
            # PORCENTAJES
            # --------------------------------------

            st.write("### 📊 Porcentaje de asistencia")

            datos_asistencia = []

            for alumno in alumnos_curso:

                porcentaje = calcular_porcentaje_asistencia(
                    alumno["id"],
                    asignacion_actual_id
                )

                if porcentaje is None:
                    porcentaje_texto = "Sin registros"
                else:
                    porcentaje_texto = f"{porcentaje}%"

                datos_asistencia.append(
                    {
                        "Apellido": alumno["apellido"],
                        "Nombre": alumno["nombre"],
                        "Asistencia": porcentaje_texto
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

        st.title("📝 Calificaciones")

        st.subheader(
            f"{curso_actual['nombre']} — "
            f"{materia_actual['nombre']}"
        )

        st.info(
            "El módulo de calificaciones "
            "se desarrollará próximamente."
        )

    # ==========================================
    # OBSERVACIONES
    # ==========================================

    elif pagina == "📋 Observaciones":

        st.title("📋 Observaciones")

        st.subheader(
            f"{curso_actual['nombre']} — "
            f"{materia_actual['nombre']}"
        )

        st.info(
            "El módulo de observaciones "
            "se desarrollará próximamente."
        )

    # ==========================================
    # ESTADÍSTICAS
    # ==========================================

    elif pagina == "📊 Estadísticas":

        st.title("📊 Estadísticas")

        st.subheader(
            f"{curso_actual['nombre']} — "
            f"{materia_actual['nombre']}"
        )

        st.info(
            "El módulo de estadísticas "
            "se desarrollará próximamente."
        )
