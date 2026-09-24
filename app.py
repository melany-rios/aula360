import streamlit as st
import pandas as pd
from datetime import date, time


# ============================================================
# DATOS DE PRUEBA
# ============================================================

from data.datos_prueba import (
    materias,
    cursos,
    asignaciones,
    alumnos,
    asistencias
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Aula360",
    page_icon="🎓",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

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

if "calificaciones" not in st.session_state:
    st.session_state.calificaciones = []

if "evaluaciones" not in st.session_state:
    st.session_state.evaluaciones = []

if "calificaciones_cuatrimestre" not in st.session_state:
    st.session_state.calificaciones_cuatrimestre = []

if "eventos_calendario" not in st.session_state:
    st.session_state.eventos_calendario = []

if "horarios" not in st.session_state:
    st.session_state.horarios = []


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def obtener_nuevo_id(lista):

    if not lista:
        return 1

    return max(item["id"] for item in lista) + 1


def obtener_curso(asignacion_id):

    asignacion = next(
        (
            item
            for item in st.session_state.asignaciones
            if item["id"] == asignacion_id
        ),
        None
    )

    if asignacion is None:
        return None

    return next(
        (
            curso
            for curso in st.session_state.cursos
            if curso["id"] == asignacion["curso_id"]
        ),
        None
    )


def obtener_materia(asignacion_id):

    asignacion = next(
        (
            item
            for item in st.session_state.asignaciones
            if item["id"] == asignacion_id
        ),
        None
    )

    if asignacion is None:
        return None

    return next(
        (
            materia
            for materia in st.session_state.materias
            if materia["id"] == asignacion["materia_id"]
        ),
        None
    )


def obtener_alumnos_asignacion(asignacion_id):

    return [
        alumno
        for alumno in st.session_state.alumnos
        if alumno["asignacion_id"] == asignacion_id
    ]


def obtener_nombre_asignacion(asignacion_id):

    curso = obtener_curso(asignacion_id)
    materia = obtener_materia(asignacion_id)

    if curso is None or materia is None:
        return "Asignación desconocida"

    return f"{curso['nombre']} - {materia['nombre']}"


def obtener_asignaciones_disponibles():

    resultado = []

    for asignacion in st.session_state.asignaciones:

        curso = obtener_curso(asignacion["id"])
        materia = obtener_materia(asignacion["id"])

        if curso and materia:

            resultado.append(
                {
                    "id": asignacion["id"],
                    "nombre": (
                        f"{curso['nombre']} - "
                        f"{materia['nombre']}"
                    )
                }
            )

    return resultado


def calcular_porcentaje_asistencia(
    alumno_id,
    asignacion_id
):

    registros = [
        asistencia
        for asistencia in st.session_state.asistencias
        if asistencia["alumno_id"] == alumno_id
        and asistencia["asignacion_id"] == asignacion_id
    ]

    if not registros:
        return 0

    presentes = sum(
        1
        for registro in registros
        if registro["estado"] in [
            "presente",
            "justificado"
        ]
    )

    return round(
        (presentes / len(registros)) * 100,
        2
    )


def buscar_calificacion_cuatrimestre(
    alumno_id,
    asignacion_id,
    cuatrimestre
):

    for registro in (
        st.session_state.calificaciones_cuatrimestre
    ):

        if (
            registro["alumno_id"] == alumno_id
            and registro["asignacion_id"] == asignacion_id
            and registro["cuatrimestre"] == cuatrimestre
        ):

            return registro

    return None


def obtener_nota_numerica(
    alumno_id,
    asignacion_id,
    cuatrimestre
):

    registro = buscar_calificacion_cuatrimestre(
        alumno_id,
        asignacion_id,
        cuatrimestre
    )

    if registro is None:
        return None

    return registro.get("nota_numerica")


def calcular_nota_final(
    alumno_id,
    asignacion_id
):

    nota_1 = obtener_nota_numerica(
        alumno_id,
        asignacion_id,
        1
    )

    nota_2 = obtener_nota_numerica(
        alumno_id,
        asignacion_id,
        2
    )

    if nota_1 is not None and nota_2 is not None:

        return round(
            (nota_1 + nota_2) / 2,
            2
        )

    return None


def obtener_eventos_fecha(fecha):

    fecha_texto = fecha.strftime(
        "%Y-%m-%d"
    )

    return [
        evento
        for evento in st.session_state.eventos_calendario
        if evento["fecha"] == fecha_texto
    ]


def obtener_horarios_dia(dia):

    return [
        horario
        for horario in st.session_state.horarios
        if horario["dia"] == dia
    ]


def horario_se_superpone(
    dia,
    hora_inicio,
    hora_fin,
    horario_excluir_id=None
):

    for horario in st.session_state.horarios:

        if horario["dia"] != dia:
            continue

        if horario_excluir_id is not None:
            if horario["id"] == horario_excluir_id:
                continue

        inicio_existente = time(
            int(horario["hora_inicio"].split(":")[0]),
            int(horario["hora_inicio"].split(":")[1])
        )

        fin_existente = time(
            int(horario["hora_fin"].split(":")[0]),
            int(horario["hora_fin"].split(":")[1])
        )

        if (
            hora_inicio < fin_existente
            and hora_fin > inicio_existente
        ):

            return True

    return False


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🎓 Aula360")

opciones_menu = [
    "🏠 Inicio",
    "⚙️ Administración",
    "👥 Alumnos",
    "🗓️ Calendario",
    "🕐 Horarios",
    "📅 Asistencia",
    "📝 Calificaciones",
    "📋 Observaciones",
    "📊 Estadísticas"
]

menu = st.sidebar.radio(
    "Menú principal",
    opciones_menu
)


# ============================================================
# SELECTOR DE CURSO Y MATERIA
# ============================================================

asignaciones_disponibles = (
    obtener_asignaciones_disponibles()
)

if asignaciones_disponibles:

    nombres_asignaciones = [
        item["nombre"]
        for item in asignaciones_disponibles
    ]

    asignacion_seleccionada_nombre = (
        st.sidebar.selectbox(
            "Curso y materia",
            nombres_asignaciones
        )
    )

    asignacion_actual = next(
        (
            item
            for item in asignaciones_disponibles
            if item["nombre"]
            == asignacion_seleccionada_nombre
        ),
        None
    )

    if asignacion_actual:
        asignacion_actual_id = (
            asignacion_actual["id"]
        )
    else:
        asignacion_actual_id = None

else:

    asignacion_actual_id = None


# ============================================================
# INICIO
# ============================================================

if menu == "🏠 Inicio":

    st.title("🎓 Aula360")

    st.subheader(
        "Sistema de gestión y seguimiento docente"
    )

    st.write(
        """
        Bienvenida a **Aula360**, una aplicación para
        centralizar la información de tus cursos y materias.
        """
    )

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Cursos",
        len(st.session_state.cursos)
    )

    col2.metric(
        "Materias",
        len(st.session_state.materias)
    )

    col3.metric(
        "Alumnos",
        len(st.session_state.alumnos)
    )

    col4.metric(
        "Eventos calendario",
        len(st.session_state.eventos_calendario)
    )

    st.divider()

    if asignacion_actual_id:

        curso = obtener_curso(
            asignacion_actual_id
        )

        materia = obtener_materia(
            asignacion_actual_id
        )

        st.subheader(
            "📌 Asignación seleccionada"
        )

        col1, col2 = st.columns(2)

        with col1:
            st.write(
                f"**Curso:** {curso['nombre']}"
            )

        with col2:
            st.write(
                f"**Materia:** {materia['nombre']}"
            )

        alumnos_asignacion = (
            obtener_alumnos_asignacion(
                asignacion_actual_id
            )
        )

        st.write(
            f"**Cantidad de alumnos:** "
            f"{len(alumnos_asignacion)}"
        )


# ============================================================
# ADMINISTRACIÓN
# ============================================================

elif menu == "⚙️ Administración":

    st.title("⚙️ Administración")

    tab_cursos, tab_materias, tab_asignaciones = (
        st.tabs(
            [
                "🏫 Cursos",
                "📚 Materias",
                "🔗 Asignaciones"
            ]
        )
    )

    # ========================================================
    # CURSOS
    # ========================================================

    with tab_cursos:

        st.subheader(
            "🏫 Gestión de cursos"
        )

        accion = st.radio(
            "Acción",
            [
                "Agregar curso",
                "Modificar curso",
                "Eliminar curso",
                "Ver cursos"
            ],
            horizontal=True
        )

        if accion == "Agregar curso":

            nombre_curso = st.text_input(
                "Nombre del curso",
                placeholder="Ejemplo: 5° 2°"
            )

            if st.button(
                "Agregar curso"
            ):

                if not nombre_curso.strip():

                    st.warning(
                        "Ingresá el nombre del curso."
                    )

                else:

                    existe = any(
                        curso["nombre"].lower()
                        == nombre_curso.strip().lower()
                        for curso
                        in st.session_state.cursos
                    )

                    if existe:

                        st.error(
                            "Ese curso ya existe."
                        )

                    else:

                        nuevo_curso = {
                            "id":
                                obtener_nuevo_id(
                                    st.session_state.cursos
                                ),
                            "nombre":
                                nombre_curso.strip()
                        }

                        st.session_state.cursos.append(
                            nuevo_curso
                        )

                        st.success(
                            "Curso agregado correctamente."
                        )

                        st.rerun()

        elif accion == "Modificar curso":

            if st.session_state.cursos:

                cursos_nombres = [
                    curso["nombre"]
                    for curso
                    in st.session_state.cursos
                ]

                seleccionado = st.selectbox(
                    "Seleccioná el curso",
                    cursos_nombres
                )

                curso = next(
                    curso
                    for curso
                    in st.session_state.cursos
                    if curso["nombre"]
                    == seleccionado
                )

                nuevo_nombre = st.text_input(
                    "Nuevo nombre",
                    value=curso["nombre"]
                )

                if st.button(
                    "Guardar cambios"
                ):

                    if nuevo_nombre.strip():

                        curso["nombre"] = (
                            nuevo_nombre.strip()
                        )

                        st.success(
                            "Curso modificado correctamente."
                        )

                        st.rerun()

            else:

                st.info(
                    "No hay cursos registrados."
                )

        elif accion == "Eliminar curso":

            if st.session_state.cursos:

                cursos_nombres = [
                    curso["nombre"]
                    for curso
                    in st.session_state.cursos
                ]

                seleccionado = st.selectbox(
                    "Seleccioná el curso",
                    cursos_nombres
                )

                if st.button(
                    "Eliminar curso"
                ):

                    curso = next(
                        curso
                        for curso
                        in st.session_state.cursos
                        if curso["nombre"]
                        == seleccionado
                    )

                    st.session_state.cursos.remove(
                        curso
                    )

                    st.success(
                        "Curso eliminado correctamente."
                    )

                    st.rerun()

        else:

            if st.session_state.cursos:

                st.dataframe(
                    pd.DataFrame(
                        st.session_state.cursos
                    ),
                    use_container_width=True,
                    hide_index=True
                )

    # ========================================================
    # MATERIAS
    # ========================================================

    with tab_materias:

        st.subheader(
            "📚 Gestión de materias"
        )

        accion = st.radio(
            "Acción",
            [
                "Agregar materia",
                "Modificar materia",
                "Eliminar materia",
                "Ver materias"
            ],
            horizontal=True
        )

        if accion == "Agregar materia":

            nombre_materia = st.text_input(
                "Nombre de la materia",
                placeholder="Ejemplo: Redes II"
            )

            if st.button(
                "Agregar materia"
            ):

                if not nombre_materia.strip():

                    st.warning(
                        "Ingresá el nombre de la materia."
                    )

                else:

                    existe = any(
                        materia["nombre"].lower()
                        == nombre_materia.strip().lower()
                        for materia
                        in st.session_state.materias
                    )

                    if existe:

                        st.error(
                            "Esa materia ya existe."
                        )

                    else:

                        nueva_materia = {
                            "id":
                                obtener_nuevo_id(
                                    st.session_state.materias
                                ),
                            "nombre":
                                nombre_materia.strip()
                        }

                        st.session_state.materias.append(
                            nueva_materia
                        )

                        st.success(
                            "Materia agregada correctamente."
                        )

                        st.rerun()

        elif accion == "Modificar materia":

            if st.session_state.materias:

                nombres = [
                    materia["nombre"]
                    for materia
                    in st.session_state.materias
                ]

                seleccionada = st.selectbox(
                    "Seleccioná la materia",
                    nombres
                )

                materia = next(
                    materia
                    for materia
                    in st.session_state.materias
                    if materia["nombre"]
                    == seleccionada
                )

                nuevo_nombre = st.text_input(
                    "Nuevo nombre",
                    value=materia["nombre"]
                )

                if st.button(
                    "Guardar cambios"
                ):

                    if nuevo_nombre.strip():

                        materia["nombre"] = (
                            nuevo_nombre.strip()
                        )

                        st.success(
                            "Materia modificada correctamente."
                        )

                        st.rerun()

        elif accion == "Eliminar materia":

            if st.session_state.materias:

                nombres = [
                    materia["nombre"]
                    for materia
                    in st.session_state.materias
                ]

                seleccionada = st.selectbox(
                    "Seleccioná la materia",
                    nombres
                )

                if st.button(
                    "Eliminar materia"
                ):

                    materia = next(
                        materia
                        for materia
                        in st.session_state.materias
                        if materia["nombre"]
                        == seleccionada
                    )

                    st.session_state.materias.remove(
                        materia
                    )

                    st.success(
                        "Materia eliminada correctamente."
                    )

                    st.rerun()

        else:

            if st.session_state.materias:

                st.dataframe(
                    pd.DataFrame(
                        st.session_state.materias
                    ),
                    use_container_width=True,
                    hide_index=True
                )

    # ========================================================
    # ASIGNACIONES
    # ========================================================

    with tab_asignaciones:

        st.subheader(
            "🔗 Asignar materias a cursos"
        )

        cursos_nombres = [
            curso["nombre"]
            for curso
            in st.session_state.cursos
        ]

        materias_nombres = [
            materia["nombre"]
            for materia
            in st.session_state.materias
        ]

        if cursos_nombres and materias_nombres:

            curso_nombre = st.selectbox(
                "Curso",
                cursos_nombres
            )

            materia_nombre = st.selectbox(
                "Materia",
                materias_nombres
            )

            if st.button(
                "Crear asignación"
            ):

                curso = next(
                    curso
                    for curso
                    in st.session_state.cursos
                    if curso["nombre"]
                    == curso_nombre
                )

                materia = next(
                    materia
                    for materia
                    in st.session_state.materias
                    if materia["nombre"]
                    == materia_nombre
                )

                existe = any(
                    asignacion["curso_id"]
                    == curso["id"]
                    and
                    asignacion["materia_id"]
                    == materia["id"]
                    for asignacion
                    in st.session_state.asignaciones
                )

                if existe:

                    st.warning(
                        "Esta materia ya está asignada "
                        "a ese curso."
                    )

                else:

                    nueva_asignacion = {
                        "id":
                            obtener_nuevo_id(
                                st.session_state.asignaciones
                            ),
                        "curso_id":
                            curso["id"],
                        "materia_id":
                            materia["id"]
                    }

                    st.session_state.asignaciones.append(
                        nueva_asignacion
                    )

                    st.success(
                        "Asignación creada correctamente."
                    )

                    st.rerun()

        st.divider()

        st.subheader(
            "Asignaciones actuales"
        )

        datos_asignaciones = []

        for asignacion in (
            st.session_state.asignaciones
        ):

            curso = obtener_curso(
                asignacion["id"]
            )

            materia = obtener_materia(
                asignacion["id"]
            )

            if curso and materia:

                datos_asignaciones.append(
                    {
                        "ID":
                            asignacion["id"],
                        "Curso":
                            curso["nombre"],
                        "Materia":
                            materia["nombre"]
                    }
                )

        if datos_asignaciones:

            st.dataframe(
                pd.DataFrame(
                    datos_asignaciones
                ),
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            opciones = [
                f"{item['Curso']} - "
                f"{item['Materia']}"
                for item
                in datos_asignaciones
            ]

            seleccion = st.selectbox(
                "Asignación a eliminar",
                opciones
            )

            if st.button(
                "Eliminar asignación"
            ):

                asignacion = next(
                    item
                    for item
                    in datos_asignaciones
                    if (
                        f"{item['Curso']} - "
                        f"{item['Materia']}"
                    ) == seleccion
                )

                st.session_state.asignaciones = [
                    item
                    for item
                    in st.session_state.asignaciones
                    if item["id"]
                    != asignacion["ID"]
                ]

                st.success(
                    "Asignación eliminada correctamente."
                )

                st.rerun()


# ============================================================
# ALUMNOS
# ============================================================

elif menu == "👥 Alumnos":

    st.title("👥 Alumnos")

    if asignacion_actual_id is None:

        st.warning(
            "Primero debés crear una asignación "
            "de curso y materia."
        )

    else:

        curso = obtener_curso(
            asignacion_actual_id
        )

        materia = obtener_materia(
            asignacion_actual_id
        )

        st.subheader(
            f"{curso['nombre']} - "
            f"{materia['nombre']}"
        )

        tab_agregar, tab_lista = st.tabs(
            [
                "➕ Agregar alumno",
                "📋 Lista de alumnos"
            ]
        )

        with tab_agregar:

            nombre = st.text_input(
                "Nombre"
            )

            apellido = st.text_input(
                "Apellido"
            )

            if st.button(
                "Agregar alumno"
            ):

                if (
                    not nombre.strip()
                    or not apellido.strip()
                ):

                    st.warning(
                        "Completá nombre y apellido."
                    )

                else:

                    nuevo_alumno = {
                        "id":
                            obtener_nuevo_id(
                                st.session_state.alumnos
                            ),
                        "nombre":
                            nombre.strip(),
                        "apellido":
                            apellido.strip(),
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

        with tab_lista:

            alumnos_actuales = (
                obtener_alumnos_asignacion(
                    asignacion_actual_id
                )
            )

            if alumnos_actuales:

                datos = []

                for alumno in alumnos_actuales:

                    datos.append(
                        {
                            "ID":
                                alumno["id"],
                            "Apellido":
                                alumno["apellido"],
                            "Nombre":
                                alumno["nombre"],
                            "Asistencia":
                                (
                                    f"{calcular_porcentaje_asistencia("
                                    f"alumno['id'], "
                                    f"asignacion_actual_id"
                                    f")}%"
                                )
                        }
                    )

                st.dataframe(
                    pd.DataFrame(datos),
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info(
                    "Todavía no hay alumnos registrados."
                )


# ============================================================
# CALENDARIO
# ============================================================

elif menu == "🗓️ Calendario":

    st.title(
        "🗓️ Calendario docente"
    )

    st.write(
        """
        Registrá feriados, artículos, exámenes, mesas,
        actos, suspensiones y cualquier otra situación
        particular de una fecha.
        """
    )

    tab_cargar, tab_ver = st.tabs(
        [
            "➕ Registrar evento",
            "📋 Ver calendario"
        ]
    )

    # ========================================================
    # CARGAR EVENTO
    # ========================================================

    with tab_cargar:

        st.subheader(
            "➕ Nuevo evento"
        )

        fecha_evento = st.date_input(
            "Fecha",
            value=date.today()
        )

        tipos_evento = [
            "Feriado",
            "Receso",
            "Sin actividad escolar",
            "Artículo docente",
            "Examen",
            "Mesa de examen",
            "Acto / actividad institucional",
            "Reunión",
            "Otro"
        ]

        tipo_evento = st.selectbox(
            "Tipo de evento",
            tipos_evento
        )

        alcance = st.radio(
            "Alcance",
            [
                "Todas mis clases",
                "Un curso y materia específicos"
            ],
            horizontal=True
        )

        asignacion_evento_id = None

        if (
            alcance
            == "Un curso y materia específicos"
        ):

            if asignaciones_disponibles:

                nombres = [
                    item["nombre"]
                    for item
                    in asignaciones_disponibles
                ]

                seleccion = st.selectbox(
                    "Curso y materia",
                    nombres,
                    key="calendario_asignacion"
                )

                asignacion_evento = next(
                    item
                    for item
                    in asignaciones_disponibles
                    if item["nombre"]
                    == seleccion
                )

                asignacion_evento_id = (
                    asignacion_evento["id"]
                )

            else:

                st.warning(
                    "No hay asignaciones disponibles."
                )

        descripcion = st.text_area(
            "Nota / detalle",
            placeholder=(
                "Ejemplo: Examen de Software II. "
                "No se dicta la clase habitual."
            )
        )

        afecta_clases = st.checkbox(
            "Este evento afecta el dictado "
            "normal de clases",
            value=True
        )

        if st.button(
            "Guardar evento",
            type="primary"
        ):

            nuevo_evento = {
                "id":
                    obtener_nuevo_id(
                        st.session_state.eventos_calendario
                    ),
                "fecha":
                    fecha_evento.strftime(
                        "%Y-%m-%d"
                    ),
                "tipo":
                    tipo_evento,
                "alcance":
                    alcance,
                "asignacion_id":
                    asignacion_evento_id,
                "descripcion":
                    descripcion.strip(),
                "afecta_clases":
                    afecta_clases
            }

            st.session_state.eventos_calendario.append(
                nuevo_evento
            )

            st.success(
                "Evento registrado correctamente."
            )

            st.rerun()

    # ========================================================
    # VER CALENDARIO
    # ========================================================

    with tab_ver:

        st.subheader(
            "📋 Eventos registrados"
        )

        if st.session_state.eventos_calendario:

            eventos_mostrar = []

            for evento in sorted(
                st.session_state.eventos_calendario,
                key=lambda x: x["fecha"]
            ):

                if evento["asignacion_id"]:

                    asignacion_nombre = (
                        obtener_nombre_asignacion(
                            evento["asignacion_id"]
                        )
                    )

                else:

                    asignacion_nombre = (
                        "Todas mis clases"
                    )

                eventos_mostrar.append(
                    {
                        "Fecha":
                            evento["fecha"],
                        "Tipo":
                            evento["tipo"],
                        "Curso / materia":
                            asignacion_nombre,
                        "Detalle":
                            evento["descripcion"],
                        "Afecta clases":
                            (
                                "Sí"
                                if evento[
                                    "afecta_clases"
                                ]
                                else "No"
                            )
                    }
                )

            st.dataframe(
                pd.DataFrame(
                    eventos_mostrar
                ),
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            st.subheader(
                "🗑️ Eliminar evento"
            )

            opciones_eventos = []

            for evento in (
                st.session_state.eventos_calendario
            ):

                if evento["asignacion_id"]:

                    asignacion_nombre = (
                        obtener_nombre_asignacion(
                            evento["asignacion_id"]
                        )
                    )

                else:

                    asignacion_nombre = (
                        "Todas mis clases"
                    )

                texto = (
                    f"{evento['fecha']} | "
                    f"{evento['tipo']} | "
                    f"{asignacion_nombre}"
                )

                opciones_eventos.append(
                    texto
                )

            evento_seleccionado = (
                st.selectbox(
                    "Seleccioná el evento",
                    opciones_eventos
                )
            )

            if st.button(
                "Eliminar evento"
            ):

                indice = (
                    opciones_eventos.index(
                        evento_seleccionado
                    )
                )

                st.session_state.eventos_calendario.pop(
                    indice
                )

                st.success(
                    "Evento eliminado correctamente."
                )

                st.rerun()

        else:

            st.info(
                "Todavía no hay eventos registrados."
            )


# ============================================================
# HORARIOS
# ============================================================

elif menu == "🕐 Horarios":

    st.title(
        "🕐 Horario docente"
    )

    st.write(
        """
        Organizá tus clases semanales. Podés tener varias
        clases el mismo día y dejar días completos sin clases.
        """
    )

    tab_semana, tab_agregar, tab_modificar, tab_eliminar = (
        st.tabs(
            [
                "📅 Vista semanal",
                "➕ Agregar",
                "✏️ Modificar",
                "🗑️ Eliminar"
            ]
        )
    )

    dias_semana = [
        "Lunes",
        "Martes",
        "Miércoles",
        "Jueves",
        "Viernes"
    ]

    # ========================================================
    # VISTA SEMANAL
    # ========================================================

    with tab_semana:

        st.subheader(
            "📅 Mi semana"
        )

        columnas = st.columns(
            len(dias_semana)
        )

        for indice, dia in enumerate(
            dias_semana
        ):

            with columnas[indice]:

                st.markdown(
                    f"### {dia}"
                )

                horarios_dia = sorted(
                    obtener_horarios_dia(dia),
                    key=lambda x: x["hora_inicio"]
                )

                if not horarios_dia:

                    st.info(
                        "Sin clases registradas."
                    )

                else:

                    for horario in horarios_dia:

                        asignacion_nombre = (
                            obtener_nombre_asignacion(
                                horario[
                                    "asignacion_id"
                                ]
                            )
                        )

                        st.markdown(
                            f"**{asignacion_nombre}**"
                        )

                        st.write(
                            f"🕐 "
                            f"{horario['hora_inicio']} - "
                            f"{horario['hora_fin']}"
                        )

                        st.divider()

    # ========================================================
    # AGREGAR HORARIO
    # ========================================================

    with tab_agregar:

        st.subheader(
            "➕ Agregar horario"
        )

        if asignaciones_disponibles:

            nombres_asignaciones = [
                item["nombre"]
                for item
                in asignaciones_disponibles
            ]

            asignacion_nombre = st.selectbox(
                "Curso y materia",
                nombres_asignaciones,
                key="agregar_horario_asignacion"
            )

            asignacion_horario = next(
                item
                for item
                in asignaciones_disponibles
                if item["nombre"]
                == asignacion_nombre
            )

            dia = st.selectbox(
                "Día",
                dias_semana,
                key="agregar_horario_dia"
            )

            col1, col2 = st.columns(2)

            with col1:

                hora_inicio = st.time_input(
                    "Hora de inicio",
                    value=time(14, 0),
                    key="agregar_hora_inicio"
                )

            with col2:

                hora_fin = st.time_input(
                    "Hora de finalización",
                    value=time(15, 20),
                    key="agregar_hora_fin"
                )

            if st.button(
                "Guardar horario",
                type="primary",
                key="guardar_horario"
            ):

                if hora_fin <= hora_inicio:

                    st.error(
                        "La hora de finalización debe ser "
                        "posterior a la hora de inicio."
                    )

                elif horario_se_superpone(
                    dia,
                    hora_inicio,
                    hora_fin
                ):

                    st.error(
                        "Ese horario se superpone con otra "
                        "clase que ya tenés registrada."
                    )

                else:

                    nuevo_horario = {
                        "id":
                            obtener_nuevo_id(
                                st.session_state.horarios
                            ),
                        "asignacion_id":
                            asignacion_horario["id"],
                        "dia":
                            dia,
                        "hora_inicio":
                            hora_inicio.strftime(
                                "%H:%M"
                            ),
                        "hora_fin":
                            hora_fin.strftime(
                                "%H:%M"
                            )
                    }

                    st.session_state.horarios.append(
                        nuevo_horario
                    )

                    st.success(
                        "Horario agregado correctamente."
                    )

                    st.rerun()

        else:

            st.warning(
                "Primero necesitás crear cursos, "
                "materias y asignaciones."
            )

    # ========================================================
    # MODIFICAR HORARIO
    # ========================================================

    with tab_modificar:

        st.subheader(
            "✏️ Modificar horario"
        )

        if st.session_state.horarios:

            opciones_horarios = []

            for horario in (
                st.session_state.horarios
            ):

                opciones_horarios.append(
                    {
                        "id":
                            horario["id"],
                        "texto":
                            (
                                f"{horario['dia']} | "
                                f"{obtener_nombre_asignacion("
                                f"horario['asignacion_id']"
                                f")} | "
                                f"{horario['hora_inicio']} - "
                                f"{horario['hora_fin']}"
                            )
                    }
                )

            textos_horarios = [
                item["texto"]
                for item in opciones_horarios
            ]

            horario_seleccionado_texto = (
                st.selectbox(
                    "Seleccioná el horario a modificar",
                    textos_horarios,
                    key="horario_modificar_seleccion"
                )
            )

            horario_seleccionado = next(
                horario
                for horario
                in st.session_state.horarios
                if (
                    f"{horario['dia']} | "
                    f"{obtener_nombre_asignacion("
                    f"horario['asignacion_id']"
                    f")} | "
                    f"{horario['hora_inicio']} - "
                    f"{horario['hora_fin']}"
                )
                == horario_seleccionado_texto
            )

            st.divider()

            nombres_asignaciones = [
                item["nombre"]
                for item
                in asignaciones_disponibles
            ]

            asignacion_actual_horario = next(
                item
                for item
                in asignaciones_disponibles
                if item["id"]
                == horario_seleccionado[
                    "asignacion_id"
                ]
            )

            indice_asignacion = (
                nombres_asignaciones.index(
                    asignacion_actual_horario[
                        "nombre"
                    ]
                )
            )

            nueva_asignacion_nombre = (
                st.selectbox(
                    "Curso y materia",
                    nombres_asignaciones,
                    index=indice_asignacion,
                    key="modificar_asignacion"
                )
            )

            nueva_asignacion = next(
                item
                for item
                in asignaciones_disponibles
                if item["nombre"]
                == nueva_asignacion_nombre
            )

            indice_dia = dias_semana.index(
                horario_seleccionado["dia"]
            )

            nuevo_dia = st.selectbox(
                "Día",
                dias_semana,
                index=indice_dia,
                key="modificar_dia"
            )

            hora_inicio_actual = time(
                int(
                    horario_seleccionado[
                        "hora_inicio"
                    ].split(":")[0]
                ),
                int(
                    horario_seleccionado[
                        "hora_inicio"
                    ].split(":")[1]
                )
            )

            hora_fin_actual = time(
                int(
                    horario_seleccionado[
                        "hora_fin"
                    ].split(":")[0]
                ),
                int(
                    horario_seleccionado[
                        "hora_fin"
                    ].split(":")[1]
                )
            )

            col1, col2 = st.columns(2)

            with col1:

                nueva_hora_inicio = st.time_input(
                    "Hora de inicio",
                    value=hora_inicio_actual,
                    key="modificar_hora_inicio"
                )

            with col2:

                nueva_hora_fin = st.time_input(
                    "Hora de finalización",
                    value=hora_fin_actual,
                    key="modificar_hora_fin"
                )

            if st.button(
                "💾 Guardar modificación",
                type="primary",
                key="guardar_modificacion_horario"
            ):

                if nueva_hora_fin <= nueva_hora_inicio:

                    st.error(
                        "La hora de finalización debe ser "
                        "posterior a la hora de inicio."
                    )

                elif horario_se_superpone(
                    nuevo_dia,
                    nueva_hora_inicio,
                    nueva_hora_fin,
                    horario_seleccionado["id"]
                ):

                    st.error(
                        "El nuevo horario se superpone con "
                        "otra clase que ya tenés registrada."
                    )

                else:

                    horario_seleccionado[
                        "asignacion_id"
                    ] = nueva_asignacion["id"]

                    horario_seleccionado[
                        "dia"
                    ] = nuevo_dia

                    horario_seleccionado[
                        "hora_inicio"
                    ] = nueva_hora_inicio.strftime(
                        "%H:%M"
                    )

                    horario_seleccionado[
                        "hora_fin"
                    ] = nueva_hora_fin.strftime(
                        "%H:%M"
                    )

                    st.success(
                        "Horario modificado correctamente."
                    )

                    st.rerun()

        else:

            st.info(
                "Todavía no hay horarios registrados."
            )

    # ========================================================
    # ELIMINAR HORARIO
    # ========================================================

    with tab_eliminar:

        st.subheader(
            "🗑️ Eliminar horario"
        )

        if st.session_state.horarios:

            opciones_eliminar = []

            for horario in (
                st.session_state.horarios
            ):

                opciones_eliminar.append(
                    {
                        "id":
                            horario["id"],
                        "texto":
                            (
                                f"{horario['dia']} | "
                                f"{obtener_nombre_asignacion("
                                f"horario['asignacion_id']"
                                f")} | "
                                f"{horario['hora_inicio']} - "
                                f"{horario['hora_fin']}"
                            )
                    }
                )

            textos_eliminar = [
                item["texto"]
                for item in opciones_eliminar
            ]

            seleccion_eliminar = st.selectbox(
                "Seleccioná el horario",
                textos_eliminar,
                key="horario_eliminar_seleccion"
            )

            horario_eliminar = next(
                item
                for item
                in opciones_eliminar
                if item["texto"]
                == seleccion_eliminar
            )

            if st.button(
                "🗑️ Eliminar horario",
                key="eliminar_horario"
            ):

                st.session_state.horarios = [
                    horario
                    for horario
                    in st.session_state.horarios
                    if horario["id"]
                    != horario_eliminar["id"]
                ]

                st.success(
                    "Horario eliminado correctamente."
                )

                st.rerun()

        else:

            st.info(
                "Todavía no hay horarios registrados."
            )


# ============================================================
# ASISTENCIA
# ============================================================

elif menu == "📅 Asistencia":

    st.title(
        "📅 Asistencia"
    )

    if asignacion_actual_id is None:

        st.warning(
            "Seleccioná un curso y materia."
        )

    else:

        curso = obtener_curso(
            asignacion_actual_id
        )

        materia = obtener_materia(
            asignacion_actual_id
        )

        st.subheader(
            f"{curso['nombre']} - "
            f"{materia['nombre']}"
        )

        fecha_asistencia = st.date_input(
            "Fecha de asistencia",
            value=date.today()
        )

        # ----------------------------------------------------
        # CALENDARIO
        # ----------------------------------------------------

        eventos_fecha = obtener_eventos_fecha(
            fecha_asistencia
        )

        eventos_relevantes = []

        for evento in eventos_fecha:

            if (
                evento["asignacion_id"] is None
                or evento["asignacion_id"]
                == asignacion_actual_id
            ):

                eventos_relevantes.append(
                    evento
                )

        if eventos_relevantes:

            st.info(
                "📌 Hay eventos registrados "
                "para esta fecha."
            )

            for evento in eventos_relevantes:

                st.write(
                    f"**{evento['tipo']}**: "
                    f"{evento['descripcion']}"
                )

                if evento["afecta_clases"]:

                    st.warning(
                        "Este evento está marcado como "
                        "afectando el dictado de clases."
                    )

        # ----------------------------------------------------
        # HORARIO
        # ----------------------------------------------------

        nombres_dias = [
            "Lunes",
            "Martes",
            "Miércoles",
            "Jueves",
            "Viernes",
            "Sábado",
            "Domingo"
        ]

        dia_fecha = nombres_dias[
            fecha_asistencia.weekday()
        ]

        horario_fecha = [
            horario
            for horario
            in st.session_state.horarios
            if horario["dia"] == dia_fecha
            and horario["asignacion_id"]
            == asignacion_actual_id
        ]

        if horario_fecha:

            horarios_texto = ", ".join(
                [
                    (
                        f"{h['hora_inicio']} - "
                        f"{h['hora_fin']}"
                    )
                    for h in horario_fecha
                ]
            )

            st.caption(
                f"🕐 Según tu horario, esta materia "
                f"tiene clase el {dia_fecha}: "
                f"{horarios_texto}"
            )

        else:

            st.caption(
                f"ℹ️ No hay un horario registrado "
                f"para {materia['nombre']} el "
                f"{dia_fecha}."
            )

        st.divider()

        # ----------------------------------------------------
        # ALUMNOS
        # ----------------------------------------------------

        alumnos_actuales = (
            obtener_alumnos_asignacion(
                asignacion_actual_id
            )
        )

        if not alumnos_actuales:

            st.info(
                "No hay alumnos registrados."
            )

        else:

            estados = [
                "presente",
                "ausente",
                "justificado"
            ]

            valores_asistencia = {}

            for alumno in alumnos_actuales:

                registro_existente = next(
                    (
                        asistencia
                        for asistencia
                        in st.session_state.asistencias
                        if (
                            asistencia["alumno_id"]
                            == alumno["id"]
                            and
                            asistencia["asignacion_id"]
                            == asignacion_actual_id
                            and
                            asistencia["fecha"]
                            == fecha_asistencia.strftime(
                                "%Y-%m-%d"
                            )
                        )
                    ),
                    None
                )

                estado_actual = (
                    registro_existente["estado"]
                    if registro_existente
                    else "presente"
                )

                valores_asistencia[
                    alumno["id"]
                ] = st.selectbox(
                    f"{alumno['apellido']}, "
                    f"{alumno['nombre']}",
                    estados,
                    index=estados.index(
                        estado_actual
                    ),
                    key=(
                        f"asistencia_"
                        f"{alumno['id']}_"
                        f"{fecha_asistencia}"
                    )
                )

            if st.button(
                "💾 Guardar asistencia",
                type="primary"
            ):

                fecha_texto = (
                    fecha_asistencia.strftime(
                        "%Y-%m-%d"
                    )
                )

                for alumno in alumnos_actuales:

                    estado = valores_asistencia[
                        alumno["id"]
                    ]

                    registro_existente = next(
                        (
                            asistencia
                            for asistencia
                            in st.session_state.asistencias
                            if (
                                asistencia[
                                    "alumno_id"
                                ]
                                == alumno["id"]
                                and
                                asistencia[
                                    "asignacion_id"
                                ]
                                == asignacion_actual_id
                                and
                                asistencia[
                                    "fecha"
                                ]
                                == fecha_texto
                            )
                        ),
                        None
                    )

                    if registro_existente:

                        registro_existente[
                            "estado"
                        ] = estado

                    else:

                        nuevo_registro = {
                            "id":
                                obtener_nuevo_id(
                                    st.session_state.asistencias
                                ),
                            "alumno_id":
                                alumno["id"],
                            "asignacion_id":
                                asignacion_actual_id,
                            "fecha":
                                fecha_texto,
                            "estado":
                                estado
                        }

                        st.session_state.asistencias.append(
                            nuevo_registro
                        )

                st.success(
                    "Asistencia guardada correctamente."
                )

                st.rerun()

        # ----------------------------------------------------
        # RESUMEN
        # ----------------------------------------------------

        st.divider()

        st.subheader(
            "📊 Resumen de asistencia"
        )

        datos_resumen = []

        for alumno in alumnos_actuales:

            datos_resumen.append(
                {
                    "Alumno":
                        (
                            f"{alumno['apellido']}, "
                            f"{alumno['nombre']}"
                        ),
                    "Asistencia":
                        (
                            f"{calcular_porcentaje_asistencia("
                            f"alumno['id'], "
                            f"asignacion_actual_id"
                            f")}%"
                        )
                }
            )

        if datos_resumen:

            st.dataframe(
                pd.DataFrame(
                    datos_resumen
                ),
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# CALIFICACIONES
# ============================================================

elif menu == "📝 Calificaciones":

    st.title(
        "📝 Calificaciones"
    )

    if asignacion_actual_id is None:

        st.warning(
            "Seleccioná un curso y materia."
        )

    else:

        curso = obtener_curso(
            asignacion_actual_id
        )

        materia = obtener_materia(
            asignacion_actual_id
        )

        st.subheader(
            f"{curso['nombre']} - "
            f"{materia['nombre']}"
        )

        tab_evaluaciones, tab_cuatrimestres = (
            st.tabs(
                [
                    "📋 Evaluaciones",
                    "📊 Cuatrimestres"
                ]
            )
        )

        # ====================================================
        # EVALUACIONES
        # ====================================================

        with tab_evaluaciones:

            st.subheader(
                "📋 Evaluaciones"
            )

            tipos_evaluacion = [
                "Evaluación escrita",
                "Evaluación oral",
                "Trabajo práctico individual",
                "Trabajo práctico grupal",
                "Revisión de carpeta"
            ]

            with st.form(
                "form_nueva_evaluacion"
            ):

                nombre_evaluacion = st.text_input(
                    "Nombre de la evaluación",
                    placeholder=(
                        "Ejemplo: TP N°1 - "
                        "Sistemas Operativos"
                    )
                )

                tipo_evaluacion = st.selectbox(
                    "Tipo de evaluación",
                    tipos_evaluacion
                )

                fecha_evaluacion = st.date_input(
                    "Fecha",
                    value=date.today()
                )

                guardar_evaluacion = (
                    st.form_submit_button(
                        "Crear evaluación"
                    )
                )

            if guardar_evaluacion:

                if not nombre_evaluacion.strip():

                    st.warning(
                        "Ingresá un nombre "
                        "para la evaluación."
                    )

                else:

                    nueva_evaluacion = {
                        "id":
                            obtener_nuevo_id(
                                st.session_state.evaluaciones
                            ),
                        "asignacion_id":
                            asignacion_actual_id,
                        "nombre":
                            nombre_evaluacion.strip(),
                        "tipo":
                            tipo_evaluacion,
                        "fecha":
                            fecha_evaluacion.strftime(
                                "%Y-%m-%d"
                            )
                    }

                    st.session_state.evaluaciones.append(
                        nueva_evaluacion
                    )

                    st.success(
                        "Evaluación creada correctamente."
                    )

                    st.rerun()

            st.divider()

            evaluaciones_actuales = [
                evaluacion
                for evaluacion
                in st.session_state.evaluaciones
                if evaluacion[
                    "asignacion_id"
                ] == asignacion_actual_id
            ]

            if evaluaciones_actuales:

                for evaluacion in (
                    evaluaciones_actuales
                ):

                    with st.expander(
                        (
                            f"{evaluacion['nombre']} "
                            f"— {evaluacion['tipo']} "
                            f"— {evaluacion['fecha']}"
                        )
                    ):

                        alumnos_actuales = (
                            obtener_alumnos_asignacion(
                                asignacion_actual_id
                            )
                        )

                        resultados = {}

                        for alumno in alumnos_actuales:

                            resultado_existente = next(
                                (
                                    resultado
                                    for resultado
                                    in st.session_state.calificaciones
                                    if (
                                        resultado[
                                            "alumno_id"
                                        ]
                                        == alumno["id"]
                                        and
                                        resultado[
                                            "evaluacion_id"
                                        ]
                                        == evaluacion[
                                            "id"
                                        ]
                                    )
                                ),
                                None
                            )

                            if (
                                evaluacion["tipo"]
                                == "Revisión de carpeta"
                            ):

                                opciones_resultado = [
                                    "Sin registrar",
                                    "Completa",
                                    "Incompleta"
                                ]

                                resultado_actual = (
                                    resultado_existente[
                                        "resultado"
                                    ]
                                    if resultado_existente
                                    else "Sin registrar"
                                )

                                resultados[
                                    alumno["id"]
                                ] = st.selectbox(
                                    (
                                        f"{alumno['apellido']}, "
                                        f"{alumno['nombre']}"
                                    ),
                                    opciones_resultado,
                                    index=(
                                        opciones_resultado.index(
                                            resultado_actual
                                        )
                                    ),
                                    key=(
                                        f"eval_"
                                        f"{evaluacion['id']}_"
                                        f"{alumno['id']}"
                                    )
                                )

                            else:

                                opciones_nota = (
                                    ["Sin registrar"]
                                    + list(range(1, 11))
                                )

                                nota_actual = (
                                    resultado_existente[
                                        "resultado"
                                    ]
                                    if resultado_existente
                                    else None
                                )

                                if nota_actual is None:
                                    indice = 0
                                else:
                                    indice = (
                                        opciones_nota.index(
                                            nota_actual
                                        )
                                    )

                                resultados[
                                    alumno["id"]
                                ] = st.selectbox(
                                    (
                                        f"{alumno['apellido']}, "
                                        f"{alumno['nombre']}"
                                    ),
                                    opciones_nota,
                                    index=indice,
                                    key=(
                                        f"eval_"
                                        f"{evaluacion['id']}_"
                                        f"{alumno['id']}"
                                    )
                                )

                        if st.button(
                            "💾 Guardar resultados",
                            key=(
                                f"guardar_eval_"
                                f"{evaluacion['id']}"
                            )
                        ):

                            for (
                                alumno_id,
                                resultado
                            ) in resultados.items():

                                existente = next(
                                    (
                                        registro
                                        for registro
                                        in st.session_state.calificaciones
                                        if (
                                            registro[
                                                "alumno_id"
                                            ]
                                            == alumno_id
                                            and
                                            registro[
                                                "evaluacion_id"
                                            ]
                                            == evaluacion[
                                                "id"
                                            ]
                                        )
                                    ),
                                    None
                                )

                                if (
                                    resultado
                                    == "Sin registrar"
                                ):

                                    if existente:

                                        st.session_state.calificaciones.remove(
                                            existente
                                        )

                                else:

                                    if existente:

                                        existente[
                                            "resultado"
                                        ] = resultado

                                    else:

                                        st.session_state.calificaciones.append(
                                            {
                                                "id":
                                                    obtener_nuevo_id(
                                                        st.session_state.calificaciones
                                                    ),
                                                "alumno_id":
                                                    alumno_id,
                                                "evaluacion_id":
                                                    evaluacion[
                                                        "id"
                                                    ],
                                                "resultado":
                                                    resultado
                                            }
                                        )

                            st.success(
                                "Resultados guardados."
                            )

                            st.rerun()

            else:

                st.info(
                    "Todavía no hay evaluaciones creadas."
                )

        # ====================================================
        # CUATRIMESTRES
        # ====================================================

        with tab_cuatrimestres:

            st.subheader(
                "📊 Calificaciones por cuatrimestre"
            )

            st.write(
                """
                La calificación conceptual y la numérica
                se registran por separado.
                """
            )

            alumnos_actuales = (
                obtener_alumnos_asignacion(
                    asignacion_actual_id
                )
            )

            conceptos = [
                "Sin registrar",
                "Excelente",
                "Muy Bueno",
                "Bueno",
                "Regular",
                "En proceso"
            ]

            # ------------------------------------------------
            # PRIMER CUATRIMESTRE
            # ------------------------------------------------

            st.markdown(
                "### 1️⃣ Primer cuatrimestre"
            )

            datos_primer_cuatrimestre = {}

            for alumno in alumnos_actuales:

                registro = (
                    buscar_calificacion_cuatrimestre(
                        alumno["id"],
                        asignacion_actual_id,
                        1
                    )
                )

                concepto_actual = (
                    registro["nota_conceptual"]
                    if registro
                    else "Sin registrar"
                )

                nota_actual = (
                    registro["nota_numerica"]
                    if registro
                    else None
                )

                opciones_nota = (
                    ["Sin registrar"]
                    + list(range(1, 11))
                )

                if nota_actual is None:

                    indice_nota = 0

                else:

                    indice_nota = (
                        opciones_nota.index(
                            nota_actual
                        )
                    )

                col1, col2, col3 = (
                    st.columns(
                        [3, 2, 2]
                    )
                )

                with col1:

                    st.write(
                        f"**{alumno['apellido']}, "
                        f"{alumno['nombre']}**"
                    )

                with col2:

                    concepto = st.selectbox(
                        "Conceptual",
                        conceptos,
                        index=conceptos.index(
                            concepto_actual
                        ),
                        key=(
                            f"concepto_1_"
                            f"{alumno['id']}"
                        ),
                        label_visibility="collapsed"
                    )

                with col3:

                    nota = st.selectbox(
                        "Nota",
                        opciones_nota,
                        index=indice_nota,
                        key=(
                            f"nota_1_"
                            f"{alumno['id']}"
                        ),
                        label_visibility="collapsed"
                    )

                datos_primer_cuatrimestre[
                    alumno["id"]
                ] = {
                    "concepto":
                        concepto,
                    "nota":
                        (
                            None
                            if nota
                            == "Sin registrar"
                            else nota
                        )
                }

            if st.button(
                "💾 Guardar primer cuatrimestre",
                type="primary"
            ):

                for (
                    alumno_id,
                    datos
                ) in datos_primer_cuatrimestre.items():

                    existente = (
                        buscar_calificacion_cuatrimestre(
                            alumno_id,
                            asignacion_actual_id,
                            1
                        )
                    )

                    if (
                        datos["concepto"]
                        == "Sin registrar"
                        and
                        datos["nota"] is None
                    ):

                        if existente:

                            st.session_state.calificaciones_cuatrimestre.remove(
                                existente
                            )

                    else:

                        if existente:

                            existente[
                                "nota_conceptual"
                            ] = datos["concepto"]

                            existente[
                                "nota_numerica"
                            ] = datos["nota"]

                        else:

                            st.session_state.calificaciones_cuatrimestre.append(
                                {
                                    "id":
                                        obtener_nuevo_id(
                                            st.session_state.calificaciones_cuatrimestre
                                        ),
                                    "alumno_id":
                                        alumno_id,
                                    "asignacion_id":
                                        asignacion_actual_id,
                                    "cuatrimestre":
                                        1,
                                    "nota_conceptual":
                                        datos["concepto"],
                                    "nota_numerica":
                                        datos["nota"]
                                }
                            )

                st.success(
                    "Primer cuatrimestre guardado."
                )

                st.rerun()

            st.divider()

            # ------------------------------------------------
            # SEGUNDO CUATRIMESTRE
            # ------------------------------------------------

            st.markdown(
                "### 2️⃣ Segundo cuatrimestre"
            )

            datos_segundo_cuatrimestre = {}

            for alumno in alumnos_actuales:

                registro = (
                    buscar_calificacion_cuatrimestre(
                        alumno["id"],
                        asignacion_actual_id,
                        2
                    )
                )

                concepto_actual = (
                    registro["nota_conceptual"]
                    if registro
                    else "Sin registrar"
                )

                nota_actual = (
                    registro["nota_numerica"]
                    if registro
                    else None
                )

                opciones_nota = (
                    ["Sin registrar"]
                    + list(range(1, 11))
                )

                if nota_actual is None:

                    indice_nota = 0

                else:

                    indice_nota = (
                        opciones_nota.index(
                            nota_actual
                        )
                    )

                col1, col2, col3 = (
                    st.columns(
                        [3, 2, 2]
                    )
                )

                with col1:

                    st.write(
                        f"**{alumno['apellido']}, "
                        f"{alumno['nombre']}**"
                    )

                with col2:

                    concepto = st.selectbox(
                        "Conceptual",
                        conceptos,
                        index=conceptos.index(
                            concepto_actual
                        ),
                        key=(
                            f"concepto_2_"
                            f"{alumno['id']}"
                        ),
                        label_visibility="collapsed"
                    )

                with col3:

                    nota = st.selectbox(
                        "Nota",
                        opciones_nota,
                        index=indice_nota,
                        key=(
                            f"nota_2_"
                            f"{alumno['id']}"
                        ),
                        label_visibility="collapsed"
                    )

                datos_segundo_cuatrimestre[
                    alumno["id"]
                ] = {
                    "concepto":
                        concepto,
                    "nota":
                        (
                            None
                            if nota
                            == "Sin registrar"
                            else nota
                        )
                }

            if st.button(
                "💾 Guardar segundo cuatrimestre",
                type="primary"
            ):

                for (
                    alumno_id,
                    datos
                ) in datos_segundo_cuatrimestre.items():

                    existente = (
                        buscar_calificacion_cuatrimestre(
                            alumno_id,
                            asignacion_actual_id,
                            2
                        )
                    )

                    if (
                        datos["concepto"]
                        == "Sin registrar"
                        and
                        datos["nota"] is None
                    ):

                        if existente:

                            st.session_state.calificaciones_cuatrimestre.remove(
                                existente
                            )

                    else:

                        if existente:

                            existente[
                                "nota_conceptual"
                            ] = datos["concepto"]

                            existente[
                                "nota_numerica"
                            ] = datos["nota"]

                        else:

                            st.session_state.calificaciones_cuatrimestre.append(
                                {
                                    "id":
                                        obtener_nuevo_id(
                                            st.session_state.calificaciones_cuatrimestre
                                        ),
                                    "alumno_id":
                                        alumno_id,
                                    "asignacion_id":
                                        asignacion_actual_id,
                                    "cuatrimestre":
                                        2,
                                    "nota_conceptual":
                                        datos["concepto"],
                                    "nota_numerica":
                                        datos["nota"]
                                }
                            )

                st.success(
                    "Segundo cuatrimestre guardado."
                )

                st.rerun()

            st.divider()

            # ------------------------------------------------
            # RESUMEN
            # ------------------------------------------------

            st.markdown(
                "### 📊 Resumen de calificaciones"
            )

            resumen = []

            for alumno in alumnos_actuales:

                registro_1 = (
                    buscar_calificacion_cuatrimestre(
                        alumno["id"],
                        asignacion_actual_id,
                        1
                    )
                )

                registro_2 = (
                    buscar_calificacion_cuatrimestre(
                        alumno["id"],
                        asignacion_actual_id,
                        2
                    )
                )

                nota_1 = (
                    registro_1["nota_numerica"]
                    if registro_1
                    else None
                )

                nota_2 = (
                    registro_2["nota_numerica"]
                    if registro_2
                    else None
                )

                nota_final = (
                    calcular_nota_final(
                        alumno["id"],
                        asignacion_actual_id
                    )
                )

                resumen.append(
                    {
                        "Alumno":
                            (
                                f"{alumno['apellido']}, "
                                f"{alumno['nombre']}"
                            ),
                        "1° Cuatrimestre":
                            (
                                nota_1
                                if nota_1 is not None
                                else "Pendiente"
                            ),
                        "2° Cuatrimestre":
                            (
                                nota_2
                                if nota_2 is not None
                                else "Pendiente"
                            ),
                        "Nota final":
                            (
                                nota_final
                                if nota_final is not None
                                else "Pendiente"
                            )
                    }
                )

            if resumen:

                st.dataframe(
                    pd.DataFrame(
                        resumen
                    ),
                    use_container_width=True,
                    hide_index=True
                )


# ============================================================
# OBSERVACIONES
# ============================================================

elif menu == "📋 Observaciones":

    st.title(
        "📋 Observaciones"
    )

    st.info(
        "Este módulo será desarrollado "
        "en la siguiente etapa."
    )


# ============================================================
# ESTADÍSTICAS
# ============================================================

elif menu == "📊 Estadísticas":

    st.title(
        "📊 Estadísticas"
    )

    st.info(
        "Este módulo será desarrollado posteriormente."
    )
