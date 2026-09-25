import streamlit as st
import pandas as pd
import calendar
from datetime import date, datetime, time

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

if "materias" not in st.session_state:
    st.session_state.materias = [dict(x) for x in materias]

if "cursos" not in st.session_state:
    st.session_state.cursos = [dict(x) for x in cursos]

if "asignaciones" not in st.session_state:
    st.session_state.asignaciones = [dict(x) for x in asignaciones]

if "alumnos" not in st.session_state:
    st.session_state.alumnos = [dict(x) for x in alumnos]

if "asistencias" not in st.session_state:
    st.session_state.asistencias = [dict(x) for x in asistencias]

if "evaluaciones" not in st.session_state:
    st.session_state.evaluaciones = []

if "calificaciones_cuatrimestre" not in st.session_state:
    st.session_state.calificaciones_cuatrimestre = []

if "eventos_calendario" not in st.session_state:
    st.session_state.eventos_calendario = []

if "horarios" not in st.session_state:
    st.session_state.horarios = []

if "mes_calendario" not in st.session_state:
    st.session_state.mes_calendario = date.today().month

if "anio_calendario" not in st.session_state:
    st.session_state.anio_calendario = date.today().year

if "fecha_calendario_seleccionada" not in st.session_state:
    st.session_state.fecha_calendario_seleccionada = date.today()


# ============================================================
# FUNCIONES GENERALES
# ============================================================

def siguiente_id(lista):
    if not lista:
        return 1

    return max(item["id"] for item in lista) + 1


def obtener_nombre_curso(curso_id):
    for curso in st.session_state.cursos:
        if curso["id"] == curso_id:
            return curso["nombre"]

    return "Sin curso"


def obtener_nombre_materia(materia_id):
    for materia in st.session_state.materias:
        if materia["id"] == materia_id:
            return materia["nombre"]

    return "Sin materia"


def obtener_nombre_asignacion(asignacion_id):
    for asignacion in st.session_state.asignaciones:

        if asignacion["id"] == asignacion_id:

            curso = obtener_nombre_curso(
                asignacion["curso_id"]
            )

            materia = obtener_nombre_materia(
                asignacion["materia_id"]
            )

            return f"{curso} - {materia}"

    return "Sin asignación"


def obtener_alumnos_asignacion(asignacion_id):
    return [
        alumno
        for alumno in st.session_state.alumnos
        if alumno["asignacion_id"] == asignacion_id
    ]


def calcular_porcentaje_asistencia(
    alumno_id,
    asignacion_id
):
    registros = [
        registro
        for registro in st.session_state.asistencias
        if (
            registro["alumno_id"] == alumno_id
            and registro["asignacion_id"] == asignacion_id
        )
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
        1
    )


def obtener_asistencia(
    alumno_id,
    asignacion_id,
    fecha
):
    fecha_texto = fecha.isoformat()

    for registro in st.session_state.asistencias:

        if (
            registro["alumno_id"] == alumno_id
            and registro["asignacion_id"] == asignacion_id
            and registro["fecha"] == fecha_texto
        ):
            return registro["estado"]

    return None


def guardar_asistencia(
    alumno_id,
    asignacion_id,
    fecha,
    estado
):
    fecha_texto = fecha.isoformat()

    for registro in st.session_state.asistencias:

        if (
            registro["alumno_id"] == alumno_id
            and registro["asignacion_id"] == asignacion_id
            and registro["fecha"] == fecha_texto
        ):

            registro["estado"] = estado
            return

    st.session_state.asistencias.append(
        {
            "id": siguiente_id(
                st.session_state.asistencias
            ),
            "alumno_id": alumno_id,
            "asignacion_id": asignacion_id,
            "fecha": fecha_texto,
            "estado": estado
        }
    )


def eventos_para_fecha(
    fecha,
    asignacion_id=None
):
    fecha_texto = fecha.isoformat()
    resultado = []

    for evento in st.session_state.eventos_calendario:

        if evento["fecha"] != fecha_texto:
            continue

        if evento["alcance"] == "Todas mis clases":
            resultado.append(evento)

        elif (
            asignacion_id is not None
            and evento["asignacion_id"] == asignacion_id
        ):
            resultado.append(evento)

    return resultado


def todos_los_eventos_para_fecha(fecha):
    fecha_texto = fecha.isoformat()

    return [
        evento
        for evento in st.session_state.eventos_calendario
        if evento["fecha"] == fecha_texto
    ]


def horarios_para_asignacion_dia(
    asignacion_id,
    dia
):
    return [
        horario
        for horario in st.session_state.horarios
        if (
            horario["asignacion_id"] == asignacion_id
            and horario["dia"] == dia
        )
    ]


def hay_horario_en_dia(
    asignacion_id,
    fecha
):
    dias = [
        "Lunes",
        "Martes",
        "Miércoles",
        "Jueves",
        "Viernes"
    ]

    dia = dias[fecha.weekday()]

    return len(
        horarios_para_asignacion_dia(
            asignacion_id,
            dia
        )
    ) > 0


def nota_cuatrimestre(
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


def obtener_nota_final(
    alumno_id,
    asignacion_id
):
    primero = nota_cuatrimestre(
        alumno_id,
        asignacion_id,
        "1° cuatrimestre"
    )

    segundo = nota_cuatrimestre(
        alumno_id,
        asignacion_id,
        "2° cuatrimestre"
    )

    if primero is None or segundo is None:
        return "Pendiente"

    nota1 = primero.get("nota_numerica")
    nota2 = segundo.get("nota_numerica")

    if nota1 in [None, "Sin registrar"]:
        return "Pendiente"

    if nota2 in [None, "Sin registrar"]:
        return "Pendiente"

    return round(
        (
            float(nota1)
            + float(nota2)
        ) / 2,
        2
    )


# ============================================================
# FUNCIONES PARA CALENDARIO
# ============================================================

def nombre_mes(mes):
    meses = [
        "",
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre"
    ]

    return meses[mes]


def obtener_dia_semana(fecha):
    nombres = [
        "Lunes",
        "Martes",
        "Miércoles",
        "Jueves",
        "Viernes",
        "Sábado",
        "Domingo"
    ]

    return nombres[fecha.weekday()]


def cambiar_mes(direccion):
    mes = st.session_state.mes_calendario
    anio = st.session_state.anio_calendario

    mes += direccion

    if mes > 12:
        mes = 1
        anio += 1

    if mes < 1:
        mes = 12
        anio -= 1

    st.session_state.mes_calendario = mes
    st.session_state.anio_calendario = anio


def volver_mes_actual():
    hoy = date.today()

    st.session_state.mes_calendario = hoy.month
    st.session_state.anio_calendario = hoy.year
    st.session_state.fecha_calendario_seleccionada = hoy


def seleccionar_fecha_calendario(fecha):
    st.session_state.fecha_calendario_seleccionada = fecha


def obtener_eventos_del_mes(
    mes,
    anio
):
    eventos = []

    for evento in st.session_state.eventos_calendario:

        try:
            fecha_evento = datetime.strptime(
                evento["fecha"],
                "%Y-%m-%d"
            ).date()

        except ValueError:
            continue

        if (
            fecha_evento.month == mes
            and fecha_evento.year == anio
        ):
            eventos.append(evento)

    return eventos


def eventos_del_dia_en_mes(
    dia,
    mes,
    anio
):
    fecha = date(
        anio,
        mes,
        dia
    )

    return todos_los_eventos_para_fecha(
        fecha
    )


def formato_fecha_es(fecha):
    nombres_dias = [
        "lunes",
        "martes",
        "miércoles",
        "jueves",
        "viernes",
        "sábado",
        "domingo"
    ]

    nombres_meses = [
        "",
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre"
    ]

    return (
        f"{nombres_dias[fecha.weekday()].capitalize()} "
        f"{fecha.day} de "
        f"{nombres_meses[fecha.month]} "
        f"de {fecha.year}"
    )


def mostrar_evento_resumido(evento):
    tipo = evento["tipo"]
    descripcion = evento["descripcion"]

    if len(descripcion) > 24:
        descripcion = descripcion[:21] + "..."

    return f"{tipo}: {descripcion}"


# ============================================================
# FUNCIONES PARA LIMPIAR FORMULARIOS
# ============================================================

def incrementar_formulario(nombre):
    clave = f"version_{nombre}"

    if clave not in st.session_state:
        st.session_state[clave] = 0

    st.session_state[clave] += 1

    return st.session_state[clave]


def obtener_version_formulario(nombre):
    clave = f"version_{nombre}"

    if clave not in st.session_state:
        st.session_state[clave] = 0

    return st.session_state[clave]


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🎓 Aula360")

opcion = st.sidebar.radio(
    "Menú principal",
    [
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
)


# ============================================================
# INICIO
# ============================================================

if opcion == "🏠 Inicio":

    hoy = date.today()

    st.title("🎓 Aula360")

    st.subheader(
        "Sistema de gestión y seguimiento docente"
    )

    st.markdown(
        f"### 📅 {formato_fecha_es(hoy)}"
    )

    st.divider()

    # --------------------------------------------------------
    # AGENDA DE HOY
    # --------------------------------------------------------

    st.subheader("📌 Agenda de hoy")

    eventos_hoy = todos_los_eventos_para_fecha(
        hoy
    )

    if not eventos_hoy:

        st.success(
            "No hay eventos ni conmemoraciones "
            "registrados para hoy."
        )

    else:

        for evento in eventos_hoy:

            if evento["tipo"] == "Conmemoración":

                st.info(
                    f"🎉 **{evento['tipo']}** — "
                    f"{evento['descripcion']}"
                )

            elif evento["afecta_clases"]:

                st.warning(
                    f"⚠️ **{evento['tipo']}** — "
                    f"{evento['descripcion']}"
                )

            else:

                st.info(
                    f"📌 **{evento['tipo']}** — "
                    f"{evento['descripcion']}"
                )

    st.divider()

    # --------------------------------------------------------
    # RESUMEN
    # --------------------------------------------------------

    st.subheader("📊 Resumen")

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
        "Asignaciones",
        len(st.session_state.asignaciones)
    )

    col4.metric(
        "Alumnos",
        len(st.session_state.alumnos)
    )

    st.divider()

    st.markdown(
        """
        ### Bienvenida/o a Aula360

        Desde este sistema podés centralizar:

        - cursos y materias
        - alumnos
        - horarios
        - calendario académico
        - asistencia
        - evaluaciones y calificaciones
        - observaciones
        - estadísticas
        """
    )


# ============================================================
# ADMINISTRACIÓN
# ============================================================

elif opcion == "⚙️ Administración":

    st.title("⚙️ Administración")

    tab_cursos, tab_materias, tab_asignaciones = st.tabs(
        [
            "Cursos",
            "Materias",
            "Asignaciones"
        ]
    )

    # ========================================================
    # CURSOS
    # ========================================================

    with tab_cursos:

        st.subheader("Cursos")

        sub1, sub2, sub3 = st.tabs(
            [
                "Agregar",
                "Modificar / Eliminar",
                "Listado"
            ]
        )

        with sub1:

            version = obtener_version_formulario(
                "agregar_curso"
            )

            with st.form(
                f"form_agregar_curso_{version}"
            ):

                nombre = st.text_input(
                    "Nombre del curso"
                )

                guardar = st.form_submit_button(
                    "Agregar curso"
                )

            if guardar:

                if not nombre.strip():

                    st.error(
                        "Ingresá el nombre del curso."
                    )

                else:

                    st.session_state.cursos.append(
                        {
                            "id": siguiente_id(
                                st.session_state.cursos
                            ),
                            "nombre": nombre.strip()
                        }
                    )

                    incrementar_formulario(
                        "agregar_curso"
                    )

                    st.success(
                        "Curso agregado."
                    )

                    st.rerun()

        with sub2:

            if st.session_state.cursos:

                cursos_opciones = {}

                for curso in st.session_state.cursos:
                    cursos_opciones[
                        curso["id"]
                    ] = curso["nombre"]

                curso_id = st.selectbox(
                    "Seleccioná un curso",
                    list(cursos_opciones.keys()),
                    format_func=(
                        lambda x: cursos_opciones[x]
                    ),
                    key="curso_modificar"
                )

                nuevo_nombre = st.text_input(
                    "Nuevo nombre",
                    value=cursos_opciones[curso_id]
                )

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(
                        "Guardar cambios",
                        key="guardar_curso"
                    ):

                        if nuevo_nombre.strip():

                            for curso in (
                                st.session_state.cursos
                            ):

                                if curso["id"] == curso_id:

                                    curso["nombre"] = (
                                        nuevo_nombre.strip()
                                    )

                            st.success(
                                "Curso modificado."
                            )

                            st.rerun()

                with col2:

                    if st.button(
                        "Eliminar curso",
                        key="eliminar_curso"
                    ):

                        tiene_asignaciones = any(
                            a["curso_id"] == curso_id
                            for a in (
                                st.session_state.asignaciones
                            )
                        )

                        if tiene_asignaciones:

                            st.error(
                                "No se puede eliminar porque "
                                "el curso tiene materias asignadas."
                            )

                        else:

                            st.session_state.cursos = [
                                c
                                for c in (
                                    st.session_state.cursos
                                )
                                if c["id"] != curso_id
                            ]

                            st.success(
                                "Curso eliminado."
                            )

                            st.rerun()

        with sub3:

            datos = []

            for curso in st.session_state.cursos:

                datos.append(
                    {
                        "ID": curso["id"],
                        "Curso": curso["nombre"]
                    }
                )

            st.dataframe(
                pd.DataFrame(datos),
                use_container_width=True,
                hide_index=True
            )

    # ========================================================
    # MATERIAS
    # ========================================================

    with tab_materias:

        st.subheader("Materias")

        sub1, sub2, sub3 = st.tabs(
            [
                "Agregar",
                "Modificar / Eliminar",
                "Listado"
            ]
        )

        with sub1:

            version = obtener_version_formulario(
                "agregar_materia"
            )

            with st.form(
                f"form_agregar_materia_{version}"
            ):

                nombre = st.text_input(
                    "Nombre de la materia"
                )

                guardar = st.form_submit_button(
                    "Agregar materia"
                )

            if guardar:

                if not nombre.strip():

                    st.error(
                        "Ingresá el nombre de la materia."
                    )

                else:

                    st.session_state.materias.append(
                        {
                            "id": siguiente_id(
                                st.session_state.materias
                            ),
                            "nombre": nombre.strip()
                        }
                    )

                    incrementar_formulario(
                        "agregar_materia"
                    )

                    st.success(
                        "Materia agregada."
                    )

                    st.rerun()

        with sub2:

            if st.session_state.materias:

                materias_opciones = {}

                for materia in st.session_state.materias:
                    materias_opciones[
                        materia["id"]
                    ] = materia["nombre"]

                materia_id = st.selectbox(
                    "Seleccioná una materia",
                    list(materias_opciones.keys()),
                    format_func=(
                        lambda x: materias_opciones[x]
                    ),
                    key="materia_modificar"
                )

                nuevo_nombre = st.text_input(
                    "Nuevo nombre",
                    value=materias_opciones[materia_id]
                )

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(
                        "Guardar cambios",
                        key="guardar_materia"
                    ):

                        if nuevo_nombre.strip():

                            for materia in (
                                st.session_state.materias
                            ):

                                if materia["id"] == materia_id:

                                    materia["nombre"] = (
                                        nuevo_nombre.strip()
                                    )

                            st.success(
                                "Materia modificada."
                            )

                            st.rerun()

                with col2:

                    if st.button(
                        "Eliminar materia",
                        key="eliminar_materia"
                    ):

                        tiene_asignaciones = any(
                            a["materia_id"] == materia_id
                            for a in (
                                st.session_state.asignaciones
                            )
                        )

                        if tiene_asignaciones:

                            st.error(
                                "No se puede eliminar porque "
                                "la materia está asignada a "
                                "uno o más cursos."
                            )

                        else:

                            st.session_state.materias = [
                                m
                                for m in (
                                    st.session_state.materias
                                )
                                if m["id"] != materia_id
                            ]

                            st.success(
                                "Materia eliminada."
                            )

                            st.rerun()

        with sub3:

            datos = []

            for materia in st.session_state.materias:

                datos.append(
                    {
                        "ID": materia["id"],
                        "Materia": materia["nombre"]
                    }
                )

            st.dataframe(
                pd.DataFrame(datos),
                use_container_width=True,
                hide_index=True
            )

    # ========================================================
    # ASIGNACIONES
    # ========================================================

    with tab_asignaciones:

        st.subheader(
            "Asignaciones curso + materia"
        )

        sub1, sub2 = st.tabs(
            [
                "Agregar",
                "Listado / Eliminar"
            ]
        )

        with sub1:

            cursos_opciones = {}

            for curso in st.session_state.cursos:
                cursos_opciones[
                    curso["id"]
                ] = curso["nombre"]

            materias_opciones = {}

            for materia in st.session_state.materias:
                materias_opciones[
                    materia["id"]
                ] = materia["nombre"]

            if (
                cursos_opciones
                and materias_opciones
            ):

                curso_id = st.selectbox(
                    "Curso",
                    list(cursos_opciones.keys()),
                    format_func=(
                        lambda x: cursos_opciones[x]
                    ),
                    key="asig_curso"
                )

                materia_id = st.selectbox(
                    "Materia",
                    list(materias_opciones.keys()),
                    format_func=(
                        lambda x: materias_opciones[x]
                    ),
                    key="asig_materia"
                )

                if st.button(
                    "Crear asignación"
                ):

                    existe = any(
                        a["curso_id"] == curso_id
                        and a["materia_id"] == materia_id
                        for a in (
                            st.session_state.asignaciones
                        )
                    )

                    if existe:

                        st.warning(
                            "Esta materia ya está asignada "
                            "a ese curso."
                        )

                    else:

                        st.session_state.asignaciones.append(
                            {
                                "id": siguiente_id(
                                    st.session_state.asignaciones
                                ),
                                "curso_id": curso_id,
                                "materia_id": materia_id
                            }
                        )

                        st.success(
                            "Asignación creada."
                        )

                        st.rerun()

        with sub2:

            if st.session_state.asignaciones:

                for asignacion in (
                    st.session_state.asignaciones
                ):

                    nombre = obtener_nombre_asignacion(
                        asignacion["id"]
                    )

                    col1, col2 = st.columns(
                        [5, 1]
                    )

                    with col1:

                        st.write(nombre)

                    with col2:

                        if st.button(
                            "Eliminar",
                            key=(
                                f"eliminar_asig_"
                                f"{asignacion['id']}"
                            )
                        ):

                            asignacion_id = (
                                asignacion["id"]
                            )

                            st.session_state.asignaciones = [
                                a
                                for a in (
                                    st.session_state.asignaciones
                                )
                                if a["id"] != asignacion_id
                            ]

                            st.session_state.alumnos = [
                                a
                                for a in (
                                    st.session_state.alumnos
                                )
                                if (
                                    a["asignacion_id"]
                                    != asignacion_id
                                )
                            ]

                            st.session_state.horarios = [
                                h
                                for h in (
                                    st.session_state.horarios
                                )
                                if (
                                    h["asignacion_id"]
                                    != asignacion_id
                                )
                            ]

                            st.success(
                                "Asignación eliminada."
                            )

                            st.rerun()


# ============================================================
# ALUMNOS
# ============================================================

elif opcion == "👥 Alumnos":

    st.title("👥 Alumnos")

    asignaciones_opciones = {}

    for asignacion in st.session_state.asignaciones:

        asignaciones_opciones[
            asignacion["id"]
        ] = obtener_nombre_asignacion(
            asignacion["id"]
        )

    if not asignaciones_opciones:

        st.warning(
            "Primero debés crear una asignación."
        )

    else:

        tab1, tab2 = st.tabs(
            [
                "Agregar alumno",
                "Listado"
            ]
        )

        with tab1:

            version = obtener_version_formulario(
                "agregar_alumno"
            )

            with st.form(
                f"form_agregar_alumno_{version}"
            ):

                asignacion_id = st.selectbox(
                    "Curso y materia",
                    list(asignaciones_opciones.keys()),
                    format_func=(
                        lambda x: asignaciones_opciones[x]
                    )
                )

                nombre = st.text_input(
                    "Nombre"
                )

                apellido = st.text_input(
                    "Apellido"
                )

                guardar = st.form_submit_button(
                    "Agregar alumno"
                )

            if guardar:

                if (
                    not nombre.strip()
                    or not apellido.strip()
                ):

                    st.error(
                        "Completá nombre y apellido."
                    )

                else:

                    st.session_state.alumnos.append(
                        {
                            "id": siguiente_id(
                                st.session_state.alumnos
                            ),
                            "nombre": nombre.strip(),
                            "apellido": apellido.strip(),
                            "asignacion_id": asignacion_id
                        }
                    )

                    incrementar_formulario(
                        "agregar_alumno"
                    )

                    st.success(
                        "Alumno agregado."
                    )

                    st.rerun()

        with tab2:

            asignacion_id = st.selectbox(
                "Seleccioná curso y materia",
                list(asignaciones_opciones.keys()),
                format_func=(
                    lambda x: asignaciones_opciones[x]
                ),
                key="alumnos_listado_asig"
            )

            alumnos_asignacion = (
                obtener_alumnos_asignacion(
                    asignacion_id
                )
            )

            if not alumnos_asignacion:

                st.info(
                    "No hay alumnos cargados."
                )

            else:

                datos = []

                for alumno in alumnos_asignacion:

                    porcentaje = (
                        calcular_porcentaje_asistencia(
                            alumno["id"],
                            asignacion_id
                        )
                    )

                    datos.append(
                        {
                            "ID": alumno["id"],
                            "Apellido": alumno["apellido"],
                            "Nombre": alumno["nombre"],
                            "Asistencia":
                                f"{porcentaje}%"
                        }
                    )

                st.dataframe(
                    pd.DataFrame(datos),
                    use_container_width=True,
                    hide_index=True
                )


# ============================================================
# CALENDARIO
# ============================================================

elif opcion == "🗓️ Calendario":

    st.title("🗓️ Calendario académico")

    st.markdown(
        """
        Desde este calendario podés registrar y consultar
        feriados, conmemoraciones, recesos, artículos,
        exámenes, mesas, actos, reuniones y notas personales.
        """
    )

    # ========================================================
    # ENCABEZADO DEL MES
    # ========================================================

    col1, col2, col3 = st.columns(
        [1, 5, 1]
    )

    with col1:

        if st.button(
            "◀",
            key="mes_anterior"
        ):

            cambiar_mes(-1)
            st.rerun()

    with col2:

        st.markdown(
            f"<h2 style='text-align:center;'>"
            f"{nombre_mes(st.session_state.mes_calendario)} "
            f"{st.session_state.anio_calendario}"
            f"</h2>",
            unsafe_allow_html=True
        )

    with col3:

        if st.button(
            "▶",
            key="mes_siguiente"
        ):

            cambiar_mes(1)
            st.rerun()

    if st.button(
        "📅 Volver al mes actual",
        key="volver_mes_actual"
    ):

        volver_mes_actual()
        st.rerun()

    st.divider()

    # ========================================================
    # GRILLA MENSUAL
    # ========================================================

    cal = calendar.Calendar(
        firstweekday=0
    )

    semanas = cal.monthdayscalendar(
        st.session_state.anio_calendario,
        st.session_state.mes_calendario
    )

    nombres_dias = [
        "Lunes",
        "Martes",
        "Miércoles",
        "Jueves",
        "Viernes",
        "Sábado",
        "Domingo"
    ]

    encabezados = st.columns(7)

    for indice in range(7):

        with encabezados[indice]:

            st.markdown(
                f"**{nombres_dias[indice]}**"
            )

    for semana in semanas:

        columnas = st.columns(7)

        for indice, dia in enumerate(semana):

            with columnas[indice]:

                if dia == 0:

                    st.empty()

                else:

                    fecha = date(
                        st.session_state.anio_calendario,
                        st.session_state.mes_calendario,
                        dia
                    )

                    es_hoy = (
                        fecha == date.today()
                    )

                    es_seleccionada = (
                        fecha
                        == st.session_state
                        .fecha_calendario_seleccionada
                    )

                    if es_hoy:

                        titulo_dia = (
                            f"📍 **{dia} · HOY**"
                        )

                    elif es_seleccionada:

                        titulo_dia = (
                            f"🔵 **{dia}**"
                        )

                    else:

                        titulo_dia = f"**{dia}**"

                    st.markdown(
                        titulo_dia
                    )

                    eventos_dia = (
                        eventos_del_dia_en_mes(
                            dia,
                            st.session_state
                            .mes_calendario,
                            st.session_state
                            .anio_calendario
                        )
                    )

                    if eventos_dia:

                        for evento in eventos_dia:

                            if (
                                evento["tipo"]
                                == "Conmemoración"
                            ):

                                st.caption(
                                    "🎉 "
                                    + mostrar_evento_resumido(
                                        evento
                                    )
                                )

                            elif evento[
                                "afecta_clases"
                            ]:

                                st.caption(
                                    "⚠️ "
                                    + mostrar_evento_resumido(
                                        evento
                                    )
                                )

                            else:

                                st.caption(
                                    "📌 "
                                    + mostrar_evento_resumido(
                                        evento
                                    )
                                )

                    else:

                        st.caption(
                            "Sin eventos"
                        )

                    if st.button(
                        "Seleccionar",
                        key=(
                            f"dia_{"
                            f"st.session_state"
                            f".anio_calendario}_"
                            f"{st.session_state"
                            f".mes_calendario}_"
                            f"{dia}"
                        )
                    ):

                        seleccionar_fecha_calendario(
                            fecha
                        )

                        st.rerun()

    st.divider()

    # ========================================================
    # DÍA SELECCIONADO
    # ========================================================

    fecha_seleccionada = (
        st.session_state
        .fecha_calendario_seleccionada
    )

    st.subheader(
        f"📌 {formato_fecha_es(fecha_seleccionada)}"
    )

    eventos_seleccionados = (
        todos_los_eventos_para_fecha(
            fecha_seleccionada
        )
    )

    # ========================================================
    # EVENTOS DEL DÍA
    # ========================================================

    if eventos_seleccionados:

        st.markdown(
            "### Eventos registrados"
        )

        for evento in eventos_seleccionados:

            col1, col2 = st.columns(
                [6, 1]
            )

            with col1:

                st.markdown(
                    f"**{evento['tipo']}**"
                )

                st.write(
                    evento["descripcion"]
                )

                if evento["alcance"] == (
                    "Todas mis clases"
                ):

                    st.caption(
                        "Alcance: todas mis clases"
                    )

                else:

                    nombre_asignacion = (
                        obtener_nombre_asignacion(
                            evento["asignacion_id"]
                        )
                    )

                    st.caption(
                        "Alcance: "
                        + nombre_asignacion
                    )

                if evento["afecta_clases"]:

                    st.warning(
                        "Afecta el dictado normal "
                        "de clases."
                    )

            with col2:

                if st.button(
                    "Eliminar",
                    key=(
                        f"eliminar_evento_cal_"
                        f"{evento['id']}"
                    )
                ):

                    st.session_state.eventos_calendario = [
                        e
                        for e in (
                            st.session_state
                            .eventos_calendario
                        )
                        if e["id"] != evento["id"]
                    ]

                    st.success(
                        "Evento eliminado."
                    )

                    st.rerun()

            st.divider()

    else:

        st.info(
            "No hay eventos registrados para este día."
        )

    # ========================================================
    # AGREGAR NUEVO EVENTO
    # ========================================================

    st.markdown(
        "### ➕ Agregar nota o evento"
    )

    version = obtener_version_formulario(
        "agregar_evento_calendario"
    )

    tipos_evento = [
        "Feriado",
        "Conmemoración",
        "Receso",
        "Sin actividad escolar",
        "Artículo docente",
        "Examen",
        "Mesa de examen",
        "Acto / actividad institucional",
        "Reunión",
        "Otro"
    ]

    alcance_opciones = [
        "Todas mis clases",
        "Un curso y materia específicos"
    ]

    with st.form(
        f"form_evento_calendario_{version}"
    ):

        tipo_evento = st.selectbox(
            "Tipo de evento",
            tipos_evento
        )

        alcance = st.selectbox(
            "Alcance",
            alcance_opciones
        )

        asignacion_id = None

        if alcance == (
            "Un curso y materia específicos"
        ):

            opciones_asignaciones = {}

            for asignacion in (
                st.session_state.asignaciones
            ):

                opciones_asignaciones[
                    asignacion["id"]
                ] = obtener_nombre_asignacion(
                    asignacion["id"]
                )

            if opciones_asignaciones:

                asignacion_id = st.selectbox(
                    "Curso y materia",
                    list(
                        opciones_asignaciones.keys()
                    ),
                    format_func=(
                        lambda x:
                        opciones_asignaciones[x]
                    )
                )

        afecta_clases = st.checkbox(
            "Afecta el dictado normal de clases"
        )

        descripcion = st.text_area(
            "Nota / descripción",
            placeholder=(
                "Ej.: No asistí este día. "
                "Evaluación de Software II. "
                "Acto institucional..."
            )
        )

        guardar_evento = st.form_submit_button(
            "💾 Guardar"
        )

    if guardar_evento:

        if (
            alcance
            == "Un curso y materia específicos"
            and asignacion_id is None
        ):

            st.error(
                "Seleccioná un curso y materia."
            )

        elif not descripcion.strip():

            st.error(
                "Ingresá una nota o descripción."
            )

        else:

            st.session_state.eventos_calendario.append(
                {
                    "id": siguiente_id(
                        st.session_state
                        .eventos_calendario
                    ),
                    "fecha":
                        fecha_seleccionada.isoformat(),
                    "tipo": tipo_evento,
                    "alcance": alcance,
                    "asignacion_id":
                        asignacion_id,
                    "descripcion":
                        descripcion.strip(),
                    "afecta_clases":
                        afecta_clases
                }
            )

            incrementar_formulario(
                "agregar_evento_calendario"
            )

            st.success(
                "Evento guardado correctamente."
            )

            st.rerun()

    # ========================================================
    # MODIFICAR EVENTO
    # ========================================================

    if eventos_seleccionados:

        st.markdown(
            "### ✏️ Modificar evento"
        )

        opciones_eventos = {}

        for evento in eventos_seleccionados:

            texto = (
                f"{evento['tipo']} — "
                f"{evento['descripcion']}"
            )

            opciones_eventos[
                evento["id"]
            ] = texto

        evento_id = st.selectbox(
            "Seleccioná el evento",
            list(opciones_eventos.keys()),
            format_func=(
                lambda x: opciones_eventos[x]
            ),
            key="evento_modificar"
        )

        evento_actual = None

        for evento in eventos_seleccionados:

            if evento["id"] == evento_id:

                evento_actual = evento
                break

        if evento_actual is not None:

            tipos_evento_mod = [
                "Feriado",
                "Conmemoración",
                "Receso",
                "Sin actividad escolar",
                "Artículo docente",
                "Examen",
                "Mesa de examen",
                "Acto / actividad institucional",
                "Reunión",
                "Otro"
            ]

            tipo_actual = evento_actual["tipo"]

            indice_tipo = 0

            if tipo_actual in tipos_evento_mod:

                indice_tipo = tipos_evento_mod.index(
                    tipo_actual
                )

            tipo_nuevo = st.selectbox(
                "Tipo",
                tipos_evento_mod,
                index=indice_tipo,
                key="tipo_evento_modificar"
            )

            descripcion_nueva = st.text_area(
                "Nota / descripción",
                value=evento_actual["descripcion"],
                key="descripcion_evento_modificar"
            )

            afecta_nuevo = st.checkbox(
                "Afecta el dictado normal de clases",
                value=evento_actual[
                    "afecta_clases"
                ],
                key="afecta_evento_modificar"
            )

            if st.button(
                "💾 Guardar modificación",
                key="guardar_modificacion_evento"
            ):

                evento_actual["tipo"] = tipo_nuevo

                evento_actual[
                    "descripcion"
                ] = descripcion_nueva.strip()

                evento_actual[
                    "afecta_clases"
                ] = afecta_nuevo

                st.success(
                    "Evento modificado."
                )

                st.rerun()


# ============================================================
# HORARIOS
# ============================================================

elif opcion == "🕐 Horarios":

    st.title("🕐 Horarios")

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Vista semanal",
            "Agregar",
            "Modificar",
            "Eliminar"
        ]
    )

    dias = [
        "Lunes",
        "Martes",
        "Miércoles",
        "Jueves",
        "Viernes"
    ]

    asignaciones_opciones = {}

    for asignacion in st.session_state.asignaciones:

        asignaciones_opciones[
            asignacion["id"]
        ] = obtener_nombre_asignacion(
            asignacion["id"]
        )

    # ========================================================
    # VISTA SEMANAL
    # ========================================================

    with tab1:

        columnas = st.columns(5)

        for indice, dia in enumerate(dias):

            with columnas[indice]:

                st.markdown(
                    f"### {dia}"
                )

                horarios_dia = [
                    h
                    for h in st.session_state.horarios
                    if h["dia"] == dia
                ]

                horarios_dia = sorted(
                    horarios_dia,
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

    with tab2:

        if not asignaciones_opciones:

            st.warning(
                "Primero creá una asignación."
            )

        else:

            version = obtener_version_formulario(
                "agregar_horario"
            )

            with st.form(
                f"form_agregar_horario_{version}"
            ):

                dia = st.selectbox(
                    "Día",
                    dias
                )

                asignacion_id = st.selectbox(
                    "Curso y materia",
                    list(
                        asignaciones_opciones.keys()
                    ),
                    format_func=(
                        lambda x:
                        asignaciones_opciones[x]
                    )
                )

                hora_inicio = st.time_input(
                    "Hora de inicio",
                    value=time(15, 30)
                )

                hora_fin = st.time_input(
                    "Hora de finalización",
                    value=time(17, 20)
                )

                guardar_horario = (
                    st.form_submit_button(
                        "Agregar horario"
                    )
                )

            if guardar_horario:

                if hora_fin <= hora_inicio:

                    st.error(
                        "La hora de finalización debe ser "
                        "posterior a la hora de inicio."
                    )

                else:

                    nuevo_inicio = (
                        hora_inicio.strftime("%H:%M")
                    )

                    nuevo_fin = (
                        hora_fin.strftime("%H:%M")
                    )

                    superpone = False

                    for horario in (
                        st.session_state.horarios
                    ):

                        if horario["dia"] != dia:
                            continue

                        if (
                            nuevo_inicio
                            < horario["hora_fin"]
                            and nuevo_fin
                            > horario["hora_inicio"]
                        ):

                            superpone = True
                            break

                    if superpone:

                        st.error(
                            "El horario se superpone con "
                            "otra clase registrada ese día."
                        )

                    else:

                        st.session_state.horarios.append(
                            {
                                "id": siguiente_id(
                                    st.session_state.horarios
                                ),
                                "asignacion_id":
                                    asignacion_id,
                                "dia": dia,
                                "hora_inicio":
                                    nuevo_inicio,
                                "hora_fin":
                                    nuevo_fin
                            }
                        )

                        incrementar_formulario(
                            "agregar_horario"
                        )

                        st.success(
                            "Horario agregado."
                        )

                        st.rerun()

    # ========================================================
    # MODIFICAR HORARIO
    # ========================================================

    with tab3:

        if not st.session_state.horarios:

            st.info(
                "No hay horarios registrados."
            )

        else:

            horarios_opciones = {}

            for horario in (
                st.session_state.horarios
            ):

                asignacion_nombre = (
                    obtener_nombre_asignacion(
                        horario["asignacion_id"]
                    )
                )

                texto = (
                    f"{horario['dia']} | "
                    f"{asignacion_nombre} | "
                    f"{horario['hora_inicio']} - "
                    f"{horario['hora_fin']}"
                )

                horarios_opciones[
                    horario["id"]
                ] = texto

            horario_id = st.selectbox(
                "Seleccioná el horario",
                list(
                    horarios_opciones.keys()
                ),
                format_func=(
                    lambda x:
                    horarios_opciones[x]
                ),
                key="horario_modificar"
            )

            horario_actual = next(
                h
                for h in (
                    st.session_state.horarios
                )
                if h["id"] == horario_id
            )

            dia_nuevo = st.selectbox(
                "Día",
                dias,
                index=dias.index(
                    horario_actual["dia"]
                ),
                key="horario_dia_mod"
            )

            ids_asignaciones = list(
                asignaciones_opciones.keys()
            )

            asignacion_nueva = st.selectbox(
                "Curso y materia",
                ids_asignaciones,
                index=ids_asignaciones.index(
                    horario_actual[
                        "asignacion_id"
                    ]
                ),
                format_func=(
                    lambda x:
                    asignaciones_opciones[x]
                ),
                key="horario_asig_mod"
            )

            hora_inicio_nueva = st.time_input(
                "Hora de inicio",
                value=datetime.strptime(
                    horario_actual[
                        "hora_inicio"
                    ],
                    "%H:%M"
                ).time(),
                key="horario_inicio_mod"
            )

            hora_fin_nueva = st.time_input(
                "Hora de finalización",
                value=datetime.strptime(
                    horario_actual[
                        "hora_fin"
                    ],
                    "%H:%M"
                ).time(),
                key="horario_fin_mod"
            )

            if st.button(
                "Guardar modificación"
            ):

                if hora_fin_nueva <= hora_inicio_nueva:

                    st.error(
                        "La hora de finalización debe ser "
                        "posterior a la hora de inicio."
                    )

                else:

                    nuevo_inicio = (
                        hora_inicio_nueva.strftime(
                            "%H:%M"
                        )
                    )

                    nuevo_fin = (
                        hora_fin_nueva.strftime(
                            "%H:%M"
                        )
                    )

                    superpone = False

                    for horario in (
                        st.session_state.horarios
                    ):

                        if horario["id"] == horario_id:
                            continue

                        if horario["dia"] != dia_nuevo:
                            continue

                        if (
                            nuevo_inicio
                            < horario["hora_fin"]
                            and nuevo_fin
                            > horario["hora_inicio"]
                        ):

                            superpone = True
                            break

                    if superpone:

                        st.error(
                            "El nuevo horario se superpone "
                            "con otra clase."
                        )

                    else:

                        horario_actual["dia"] = (
                            dia_nuevo
                        )

                        horario_actual[
                            "asignacion_id"
                        ] = asignacion_nueva

                        horario_actual[
                            "hora_inicio"
                        ] = nuevo_inicio

                        horario_actual[
                            "hora_fin"
                        ] = nuevo_fin

                        st.success(
                            "Horario modificado."
                        )

                        st.rerun()

    # ========================================================
    # ELIMINAR HORARIO
    # ========================================================

    with tab4:

        if not st.session_state.horarios:

            st.info(
                "No hay horarios registrados."
            )

        else:

            horarios_opciones = {}

            for horario in (
                st.session_state.horarios
            ):

                asignacion_nombre = (
                    obtener_nombre_asignacion(
                        horario["asignacion_id"]
                    )
                )

                texto = (
                    f"{horario['dia']} | "
                    f"{asignacion_nombre} | "
                    f"{horario['hora_inicio']} - "
                    f"{horario['hora_fin']}"
                )

                horarios_opciones[
                    horario["id"]
                ] = texto

            horario_id = st.selectbox(
                "Seleccioná el horario a eliminar",
                list(
                    horarios_opciones.keys()
                ),
                format_func=(
                    lambda x:
                    horarios_opciones[x]
                ),
                key="horario_eliminar"
            )

            if st.button(
                "Eliminar horario"
            ):

                st.session_state.horarios = [
                    h
                    for h in (
                        st.session_state.horarios
                    )
                    if h["id"] != horario_id
                ]

                st.success(
                    "Horario eliminado."
                )

                st.rerun()


# ============================================================
# ASISTENCIA
# ============================================================

elif opcion == "📅 Asistencia":

    st.title("📅 Asistencia")

    asignaciones_opciones = {}

    for asignacion in (
        st.session_state.asignaciones
    ):

        asignaciones_opciones[
            asignacion["id"]
        ] = obtener_nombre_asignacion(
            asignacion["id"]
        )

    if not asignaciones_opciones:

        st.warning(
            "No hay asignaciones disponibles."
        )

    else:

        asignacion_id = st.selectbox(
            "Curso y materia",
            list(
                asignaciones_opciones.keys()
            ),
            format_func=(
                lambda x:
                asignaciones_opciones[x]
            ),
            key="asistencia_asignacion"
        )

        fecha_asistencia = st.date_input(
            "Fecha",
            value=date.today(),
            key="asistencia_fecha"
        )

        st.divider()

        eventos = eventos_para_fecha(
            fecha_asistencia,
            asignacion_id
        )

        if eventos:

            st.subheader(
                "🗓️ Eventos de esta fecha"
            )

            for evento in eventos:

                st.info(
                    f"{evento['tipo']}: "
                    f"{evento['descripcion']}"
                )

                if evento["afecta_clases"]:

                    st.warning(
                        "El evento indica que el dictado "
                        "normal de clases está afectado."
                    )

        if not hay_horario_en_dia(
            asignacion_id,
            fecha_asistencia
        ):

            st.warning(
                "No hay un horario registrado para "
                "este curso y materia en el día seleccionado."
            )

        else:

            st.success(
                "Hay una clase prevista según el horario."
            )

        alumnos_asignacion = (
            obtener_alumnos_asignacion(
                asignacion_id
            )
        )

        if not alumnos_asignacion:

            st.info(
                "No hay alumnos registrados."
            )

        else:

            st.subheader(
                "Registro de asistencia"
            )

            estados = [
                "presente",
                "ausente",
                "justificado"
            ]

            for alumno in alumnos_asignacion:

                estado_actual = obtener_asistencia(
                    alumno["id"],
                    asignacion_id,
                    fecha_asistencia
                )

                if estado_actual is None:
                    estado_actual = "presente"

                estado = st.selectbox(
                    (
                        f"{alumno['apellido']}, "
                        f"{alumno['nombre']}"
                    ),
                    estados,
                    index=estados.index(
                        estado_actual
                    ),
                    key=(
                        f"estado_"
                        f"{alumno['id']}_"
                        f"{asignacion_id}_"
                        f"{fecha_asistencia.isoformat()}"
                    )
                )

                if st.button(
                    "Guardar",
                    key=(
                        f"guardar_asistencia_"
                        f"{alumno['id']}_"
                        f"{asignacion_id}_"
                        f"{fecha_asistencia.isoformat()}"
                    )
                ):

                    guardar_asistencia(
                        alumno["id"],
                        asignacion_id,
                        fecha_asistencia,
                        estado
                    )

                    st.success(
                        "Asistencia guardada."
                    )

                    st.rerun()

            st.divider()

            st.subheader(
                "Resumen"
            )

            datos = []

            for alumno in alumnos_asignacion:

                porcentaje = (
                    calcular_porcentaje_asistencia(
                        alumno["id"],
                        asignacion_id
                    )
                )

                datos.append(
                    {
                        "Apellido":
                            alumno["apellido"],
                        "Nombre":
                            alumno["nombre"],
                        "Asistencia":
                            f"{porcentaje}%"
                    }
                )

            st.dataframe(
                pd.DataFrame(datos),
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# CALIFICACIONES
# ============================================================

elif opcion == "📝 Calificaciones":

    st.title("📝 Calificaciones")

    tab1, tab2, tab3 = st.tabs(
        [
            "Evaluaciones",
            "Calificaciones por cuatrimestre",
            "Resumen final"
        ]
    )

    asignaciones_opciones = {}

    for asignacion in (
        st.session_state.asignaciones
    ):

        asignaciones_opciones[
            asignacion["id"]
        ] = obtener_nombre_asignacion(
            asignacion["id"]
        )

    # ========================================================
    # EVALUACIONES
    # ========================================================

    with tab1:

        st.subheader(
            "Registro de evaluaciones"
        )

        tipos_evaluacion = [
            "Evaluación escrita",
            "Evaluación oral",
            "Trabajo práctico individual",
            "Trabajo práctico grupal",
            "Revisión de carpeta"
        ]

        if asignaciones_opciones:

            version = obtener_version_formulario(
                "agregar_evaluacion"
            )

            with st.form(
                f"form_agregar_evaluacion_{version}"
            ):

                asignacion_id = st.selectbox(
                    "Curso y materia",
                    list(
                        asignaciones_opciones.keys()
                    ),
                    format_func=(
                        lambda x:
                        asignaciones_opciones[x]
                    )
                )

                alumnos_asignacion = (
                    obtener_alumnos_asignacion(
                        asignacion_id
                    )
                )

                if alumnos_asignacion:

                    alumno_id = st.selectbox(
                        "Alumno",
                        [
                            a["id"]
                            for a in alumnos_asignacion
                        ],
                        format_func=(
                            lambda x:
                            next(
                                (
                                    f"{a['apellido']}, "
                                    f"{a['nombre']}"
                                    for a
                                    in alumnos_asignacion
                                    if a["id"] == x
                                ),
                                "Alumno"
                            )
                        )
                    )

                    tipo = st.selectbox(
                        "Tipo de evaluación",
                        tipos_evaluacion
                    )

                    fecha = st.date_input(
                        "Fecha",
                        value=date.today()
                    )

                    nombre = st.text_input(
                        "Nombre / descripción"
                    )

                    if tipo == "Revisión de carpeta":

                        resultado = st.selectbox(
                            "Resultado",
                            [
                                "Completa",
                                "Incompleta"
                            ]
                        )

                    else:

                        resultado = st.selectbox(
                            "Resultado",
                            ["Sin registrar"]
                            + [
                                str(i)
                                for i in range(1, 11)
                            ]
                        )

                    guardar = (
                        st.form_submit_button(
                            "Registrar evaluación"
                        )
                    )

                else:

                    st.warning(
                        "No hay alumnos en esta asignación."
                    )

                    guardar = False

            if guardar:

                if not nombre.strip():

                    st.error(
                        "Ingresá el nombre o descripción."
                    )

                else:

                    st.session_state.evaluaciones.append(
                        {
                            "id": siguiente_id(
                                st.session_state
                                .evaluaciones
                            ),
                            "alumno_id":
                                alumno_id,
                            "asignacion_id":
                                asignacion_id,
                            "tipo":
                                tipo,
                            "fecha":
                                fecha.isoformat(),
                            "nombre":
                                nombre.strip(),
                            "resultado":
                                resultado
                        }
                    )

                    incrementar_formulario(
                        "agregar_evaluacion"
                    )

                    st.success(
                        "Evaluación registrada."
                    )

                    st.rerun()

        st.divider()

        if st.session_state.evaluaciones:

            datos = []

            for evaluacion in (
                st.session_state.evaluaciones
            ):

                alumno = next(
                    (
                        a
                        for a in (
                            st.session_state.alumnos
                        )
                        if a["id"]
                        == evaluacion["alumno_id"]
                    ),
                    None
                )

                if alumno:

                    alumno_nombre = (
                        f"{alumno['apellido']}, "
                        f"{alumno['nombre']}"
                    )

                    datos.append(
                        {
                            "Fecha":
                                evaluacion["fecha"],
                            "Curso - Materia":
                                obtener_nombre_asignacion(
                                    evaluacion[
                                        "asignacion_id"
                                    ]
                                ),
                            "Alumno":
                                alumno_nombre,
                            "Tipo":
                                evaluacion["tipo"],
                            "Evaluación":
                                evaluacion["nombre"],
                            "Resultado":
                                evaluacion["resultado"]
                        }
                    )

            st.dataframe(
                pd.DataFrame(datos),
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No hay evaluaciones registradas."
            )

    # ========================================================
    # CUATRIMESTRE
    # ========================================================

    with tab2:

        st.subheader(
            "Calificación por cuatrimestre"
        )

        if asignaciones_opciones:

            version = obtener_version_formulario(
                "agregar_calificacion_cuatrimestre"
            )

            with st.form(
                f"form_cuatrimestre_{version}"
            ):

                asignacion_id = st.selectbox(
                    "Curso y materia",
                    list(
                        asignaciones_opciones.keys()
                    ),
                    format_func=(
                        lambda x:
                        asignaciones_opciones[x]
                    )
                )

                alumnos_asignacion = (
                    obtener_alumnos_asignacion(
                        asignacion_id
                    )
                )

                if alumnos_asignacion:

                    alumno_id = st.selectbox(
                        "Alumno",
                        [
                            a["id"]
                            for a in alumnos_asignacion
                        ],
                        format_func=(
                            lambda x:
                            next(
                                (
                                    f"{a['apellido']}, "
                                    f"{a['nombre']}"
                                    for a
                                    in alumnos_asignacion
                                    if a["id"] == x
                                ),
                                "Alumno"
                            )
                        )
                    )

                    cuatrimestre = st.selectbox(
                        "Cuatrimestre",
                        [
                            "1° cuatrimestre",
                            "2° cuatrimestre"
                        ]
                    )

                    conceptual = st.selectbox(
                        "Calificación conceptual",
                        [
                            "Sin registrar",
                            "Excelente",
                            "Muy Bueno",
                            "Bueno",
                            "Regular",
                            "En proceso"
                        ]
                    )

                    numerica = st.selectbox(
                        "Calificación numérica",
                        ["Sin registrar"]
                        + [
                            str(i)
                            for i in range(1, 11)
                        ]
                    )

                    guardar = (
                        st.form_submit_button(
                            "Guardar calificación"
                        )
                    )

                else:

                    st.warning(
                        "No hay alumnos en esta asignación."
                    )

                    guardar = False

            if guardar:

                registro = nota_cuatrimestre(
                    alumno_id,
                    asignacion_id,
                    cuatrimestre
                )

                if registro is None:

                    st.session_state.calificaciones_cuatrimestre.append(
                        {
                            "id": siguiente_id(
                                st.session_state
                                .calificaciones_cuatrimestre
                            ),
                            "alumno_id":
                                alumno_id,
                            "asignacion_id":
                                asignacion_id,
                            "cuatrimestre":
                                cuatrimestre,
                            "nota_conceptual":
                                conceptual,
                            "nota_numerica":
                                numerica
                        }
                    )

                else:

                    registro[
                        "nota_conceptual"
                    ] = conceptual

                    registro[
                        "nota_numerica"
                    ] = numerica

                incrementar_formulario(
                    "agregar_calificacion_cuatrimestre"
                )

                st.success(
                    "Calificación guardada."
                )

                st.rerun()

        st.divider()

        if (
            st.session_state
            .calificaciones_cuatrimestre
        ):

            datos = []

            for registro in (
                st.session_state
                .calificaciones_cuatrimestre
            ):

                alumno = next(
                    (
                        a
                        for a in (
                            st.session_state.alumnos
                        )
                        if a["id"]
                        == registro["alumno_id"]
                    ),
                    None
                )

                if alumno:

                    alumno_nombre = (
                        f"{alumno['apellido']}, "
                        f"{alumno['nombre']}"
                    )

                    datos.append(
                        {
                            "Curso - Materia":
                                obtener_nombre_asignacion(
                                    registro[
                                        "asignacion_id"
                                    ]
                                ),
                            "Alumno":
                                alumno_nombre,
                            "Cuatrimestre":
                                registro["cuatrimestre"],
                            "Conceptual":
                                registro[
                                    "nota_conceptual"
                                ],
                            "Numérica":
                                registro[
                                    "nota_numerica"
                                ]
                        }
                    )

            st.dataframe(
                pd.DataFrame(datos),
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "Todavía no hay calificaciones "
                "por cuatrimestre."
            )

    # ========================================================
    # RESUMEN FINAL
    # ========================================================

    with tab3:

        st.subheader(
            "Resumen final"
        )

        if asignaciones_opciones:

            asignacion_id = st.selectbox(
                "Curso y materia",
                list(
                    asignaciones_opciones.keys()
                ),
                format_func=(
                    lambda x:
                    asignaciones_opciones[x]
                ),
                key="final_asignacion"
            )

            alumnos_asignacion = (
                obtener_alumnos_asignacion(
                    asignacion_id
                )
            )

            datos = []

            for alumno in alumnos_asignacion:

                primero = nota_cuatrimestre(
                    alumno["id"],
                    asignacion_id,
                    "1° cuatrimestre"
                )

                segundo = nota_cuatrimestre(
                    alumno["id"],
                    asignacion_id,
                    "2° cuatrimestre"
                )

                if primero is not None:

                    nota1 = primero[
                        "nota_numerica"
                    ]

                else:

                    nota1 = "Sin registrar"

                if segundo is not None:

                    nota2 = segundo[
                        "nota_numerica"
                    ]

                else:

                    nota2 = "Sin registrar"

                final = obtener_nota_final(
                    alumno["id"],
                    asignacion_id
                )

                datos.append(
                    {
                        "Apellido":
                            alumno["apellido"],
                        "Nombre":
                            alumno["nombre"],
                        "1° cuatrimestre":
                            nota1,
                        "2° cuatrimestre":
                            nota2,
                        "Nota final":
                            final
                    }
                )

            st.dataframe(
                pd.DataFrame(datos),
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# OBSERVACIONES
# ============================================================

elif opcion == "📋 Observaciones":

    st.title("📋 Observaciones")

    st.info(
        """
        Este módulo queda preparado para incorporar
        observaciones pedagógicas, de desempeño, conducta,
        trabajos, asistencia u otras situaciones relacionadas
        con cada alumno.
        """
    )


# ============================================================
# ESTADÍSTICAS
# ============================================================

elif opcion == "📊 Estadísticas":

    st.title("📊 Estadísticas")

    st.info(
        """
        Este módulo se desarrollará posteriormente,
        una vez terminada la integración entre calendario,
        horarios, asistencia y calificaciones.
        """
    )
