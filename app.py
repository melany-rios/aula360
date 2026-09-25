import calendar
from datetime import date, datetime, time

import pandas as pd
import streamlit as st

from data.datos_prueba import alumnos as alumnos_iniciales
from data.datos_prueba import asistencias as asistencias_iniciales
from data.datos_prueba import asignaciones as asignaciones_iniciales
from data.datos_prueba import cursos as cursos_iniciales
from data.datos_prueba import materias as materias_iniciales

st.set_page_config(page_title="Aula360", page_icon="📚", layout="wide")

MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
TIPOS_EVENTO = ["Feriado", "Conmemoración", "Receso", "Sin actividad escolar", "Artículo docente", "Examen", "Mesa de examen", "Acto / actividad institucional", "Reunión", "Otro"]
TIPOS_EVALUACION = ["Evaluación escrita", "Evaluación oral", "Trabajo práctico individual", "Trabajo práctico grupal", "Revisión de carpeta"]
CONCEPTUALES = ["Sin registrar", "Excelente", "Muy Bueno", "Bueno", "Regular", "En proceso"]


def inicializar():
    datos = {
        "cursos": cursos_iniciales,
        "materias": materias_iniciales,
        "asignaciones": asignaciones_iniciales,
        "alumnos": alumnos_iniciales,
        "asistencias": asistencias_iniciales,
    }
    for clave, valor in datos.items():
        if clave not in st.session_state:
            st.session_state[clave] = [dict(x) for x in valor]
    defaults = {
        "evaluaciones": [], "calificaciones_cuatrimestre": [], "observaciones": [],
        "eventos_calendario": [], "horarios": [], "fecha_calendario_seleccionada": date.today().isoformat(),
        "mes_calendario": date.today().month, "anio_calendario": date.today().year,
        "proximo_id_evento": 1, "proximo_id_horario": 1, "proximo_id_observacion": 1,
        "evento_form_version": 0, "horario_form_version": 0,
    }
    for clave, valor in defaults.items():
        if clave not in st.session_state:
            st.session_state[clave] = valor


def siguiente_id(lista):
    return max([x["id"] for x in lista], default=0) + 1


def curso_nombre(cid):
    for x in st.session_state.cursos:
        if x["id"] == cid:
            return x["nombre"]
    return "Curso desconocido"


def materia_nombre(mid):
    for x in st.session_state.materias:
        if x["id"] == mid:
            return x["nombre"]
    return "Materia desconocida"


def asignacion(aid):
    for x in st.session_state.asignaciones:
        if x["id"] == aid:
            return x
    return None


def asignacion_nombre(aid):
    x = asignacion(aid)
    if x is None:
        return "Asignación desconocida"
    return curso_nombre(x["curso_id"]) + " - " + materia_nombre(x["materia_id"])


def alumno_nombre(aid):
    for x in st.session_state.alumnos:
        if x["id"] == aid:
            return x["apellido"] + ", " + x["nombre"]
    return "Alumno desconocido"


def evento_nombre(eid):
    for x in st.session_state.eventos_calendario:
        if x["id"] == eid:
            return x["tipo"] + " - " + x["descripcion"]
    return "Evento"


def horario_nombre(hid):
    for x in st.session_state.horarios:
        if x["id"] == hid:
            return asignacion_nombre(x["asignacion_id"]) + " - " + x["dia"] + " " + x["hora_inicio"]
    return "Horario"


def fecha_texto(valor):
    return datetime.strptime(valor, "%Y-%m-%d").strftime("%d/%m/%Y")


def eventos_fecha(fecha):
    return [x for x in st.session_state.eventos_calendario if x["fecha"] == fecha]


def alumnos_asignacion(aid):
    return [x for x in st.session_state.alumnos if x["asignacion_id"] == aid]


def asistencia_existente(alumno_id, asignacion_id, fecha):
    for x in st.session_state.asistencias:
        if x["alumno_id"] == alumno_id and x["asignacion_id"] == asignacion_id and x["fecha"] == fecha:
            return x
    return None


def porcentaje_asistencia(alumno_id, asignacion_id):
    registros = [x for x in st.session_state.asistencias if x["alumno_id"] == alumno_id and x["asignacion_id"] == asignacion_id]
    if not registros:
        return 0
    buenos = sum(1 for x in registros if x["estado"] in ["presente", "justificado"])
    return round(buenos * 100 / len(registros), 1)


def calificacion_cuatri(alumno_id, asignacion_id, cuatri):
    for x in st.session_state.calificaciones_cuatrimestre:
        if x["alumno_id"] == alumno_id and x["asignacion_id"] == asignacion_id and x["cuatrimestre"] == cuatri:
            return x
    return None


def nota_final(alumno_id, asignacion_id):
    notas = []
    for cuatri in [1, 2]:
        x = calificacion_cuatri(alumno_id, asignacion_id, cuatri)
        if x is not None and x["nota_numerica"] is not None:
            notas.append(x["nota_numerica"])
    if len(notas) != 2:
        return None
    return round(sum(notas) / 2, 2)


def horario_colisiona(dia, inicio, fin, excluir_id=None):
    ni = datetime.combine(date.today(), inicio)
    nf = datetime.combine(date.today(), fin)
    for x in st.session_state.horarios:
        if excluir_id is not None and x["id"] == excluir_id:
            continue
        if x["dia"] != dia:
            continue
        ei = datetime.strptime(x["hora_inicio"], "%H:%M").time()
        ef = datetime.strptime(x["hora_fin"], "%H:%M").time()
        if ni < datetime.combine(date.today(), ef) and nf > datetime.combine(date.today(), ei):
            return True
    return False


def afecta_asignacion(evento, aid):
    if not evento["afecta_clases"]:
        return False
    return evento["alcance"] == "Todas mis clases" or evento["asignacion_id"] == aid


def hay_suspension(fecha, aid):
    tipos = ["Feriado", "Receso", "Sin actividad escolar", "Artículo docente"]
    return any(x["tipo"] in tipos and afecta_asignacion(x, aid) for x in eventos_fecha(fecha))


inicializar()

st.title("📚 Aula360")
st.caption("Sistema de gestión y seguimiento docente")

modulo = st.sidebar.radio("Menú principal", ["🏠 Inicio", "⚙️ Administración", "👥 Alumnos", "🗓️ Calendario", "🕐 Horarios", "📅 Asistencia", "📝 Calificaciones", "📋 Observaciones", "📊 Estadísticas"])

# INICIO
if modulo == "🏠 Inicio":
    hoy = date.today()
    st.subheader("Inicio")
    c1, c2, c3 = st.columns(3)
    c1.metric("Fecha de hoy", hoy.strftime("%d/%m/%Y"))
    c2.metric("Cursos", len(st.session_state.cursos))
    c3.metric("Materias", len(st.session_state.materias))
    st.divider()
    st.subheader("📅 Agenda de hoy")
    eventos = eventos_fecha(hoy.isoformat())
    if eventos:
        for x in eventos:
            st.info(x["tipo"] + ": " + x["descripcion"])
    else:
        st.success("No hay eventos registrados para hoy.")
    st.subheader("🎓 Conmemoración de hoy")
    conmemoraciones = [x for x in eventos if x["tipo"] == "Conmemoración"]
    if conmemoraciones:
        for x in conmemoraciones:
            st.info(x["descripcion"])
    else:
        st.write("No hay una conmemoración registrada para hoy.")

# ADMINISTRACIÓN
elif modulo == "⚙️ Administración":
    st.subheader("⚙️ Administración")
    tc, tm, ta = st.tabs(["Cursos", "Materias", "Asignaciones"])

    with tc:
        with st.form("agregar_curso"):
            nombre = st.text_input("Nombre del curso")
            if st.form_submit_button("Agregar curso"):
                nombre = nombre.strip()
                if not nombre:
                    st.error("Ingresá el nombre del curso.")
                elif any(x["nombre"].lower() == nombre.lower() for x in st.session_state.cursos):
                    st.warning("Ese curso ya existe.")
                else:
                    st.session_state.cursos.append({"id": siguiente_id(st.session_state.cursos), "nombre": nombre})
                    st.success("Curso agregado.")
                    st.rerun()
        st.dataframe(pd.DataFrame(st.session_state.cursos), use_container_width=True, hide_index=True)
        if st.session_state.cursos:
            cid = st.selectbox("Curso a modificar", [x["id"] for x in st.session_state.cursos], format_func=curso_nombre, key="mod_curso")
            nuevo = st.text_input("Nuevo nombre", value=curso_nombre(cid), key="nuevo_curso")
            if st.button("Guardar modificación", key="save_curso"):
                if nuevo.strip():
                    for x in st.session_state.cursos:
                        if x["id"] == cid:
                            x["nombre"] = nuevo.strip()
                    st.rerun()
            borrar = st.selectbox("Curso a eliminar", [x["id"] for x in st.session_state.cursos], format_func=curso_nombre, key="del_curso")
            if st.button("Eliminar curso", key="delete_curso"):
                if any(x["curso_id"] == borrar for x in st.session_state.asignaciones):
                    st.error("No se puede eliminar porque tiene asignaciones.")
                else:
                    st.session_state.cursos = [x for x in st.session_state.cursos if x["id"] != borrar]
                    st.rerun()

    with tm:
        with st.form("agregar_materia"):
            nombre = st.text_input("Nombre de la materia")
            if st.form_submit_button("Agregar materia"):
                nombre = nombre.strip()
                if not nombre:
                    st.error("Ingresá el nombre de la materia.")
                elif any(x["nombre"].lower() == nombre.lower() for x in st.session_state.materias):
                    st.warning("Esa materia ya existe.")
                else:
                    st.session_state.materias.append({"id": siguiente_id(st.session_state.materias), "nombre": nombre})
                    st.success("Materia agregada.")
                    st.rerun()
        st.dataframe(pd.DataFrame(st.session_state.materias), use_container_width=True, hide_index=True)
        if st.session_state.materias:
            mid = st.selectbox("Materia a modificar", [x["id"] for x in st.session_state.materias], format_func=materia_nombre, key="mod_mat")
            nuevo = st.text_input("Nuevo nombre", value=materia_nombre(mid), key="nuevo_mat")
            if st.button("Guardar modificación", key="save_mat"):
                if nuevo.strip():
                    for x in st.session_state.materias:
                        if x["id"] == mid:
                            x["nombre"] = nuevo.strip()
                    st.rerun()
            borrar = st.selectbox("Materia a eliminar", [x["id"] for x in st.session_state.materias], format_func=materia_nombre, key="del_mat")
            if st.button("Eliminar materia", key="delete_mat"):
                if any(x["materia_id"] == borrar for x in st.session_state.asignaciones):
                    st.error("No se puede eliminar porque tiene asignaciones.")
                else:
                    st.session_state.materias = [x for x in st.session_state.materias if x["id"] != borrar]
                    st.rerun()

    with ta:
        if st.session_state.cursos and st.session_state.materias:
            with st.form("agregar_asignacion"):
                cid = st.selectbox("Curso", [x["id"] for x in st.session_state.cursos], format_func=curso_nombre)
                mid = st.selectbox("Materia", [x["id"] for x in st.session_state.materias], format_func=materia_nombre)
                if st.form_submit_button("Crear asignación"):
                    if any(x["curso_id"] == cid and x["materia_id"] == mid for x in st.session_state.asignaciones):
                        st.warning("Esa asignación ya existe.")
                    else:
                        st.session_state.asignaciones.append({"id": siguiente_id(st.session_state.asignaciones), "curso_id": cid, "materia_id": mid})
                        st.rerun()
        datos = [{"ID": x["id"], "Curso": curso_nombre(x["curso_id"]), "Materia": materia_nombre(x["materia_id"])} for x in st.session_state.asignaciones]
        st.dataframe(pd.DataFrame(datos), use_container_width=True, hide_index=True)
        if st.session_state.asignaciones:
            aid = st.selectbox("Asignación a eliminar", [x["id"] for x in st.session_state.asignaciones], format_func=asignacion_nombre, key="del_asig")
            if st.button("Eliminar asignación", key="delete_asig"):
                if any(x["asignacion_id"] == aid for x in st.session_state.alumnos):
                    st.error("No se puede eliminar porque tiene alumnos.")
                else:
                    st.session_state.asignaciones = [x for x in st.session_state.asignaciones if x["id"] != aid]
                    st.rerun()

# ALUMNOS
elif modulo == "👥 Alumnos":
    st.subheader("👥 Alumnos")
    if not st.session_state.asignaciones:
        st.warning("No hay asignaciones registradas.")
    else:
        aid = st.selectbox("Curso y materia", [x["id"] for x in st.session_state.asignaciones], format_func=asignacion_nombre)
        a1, a2, a3 = st.tabs(["Agregar alumno", "Listado", "Asistencia"])
        with a1:
            with st.form("agregar_alumno"):
                nombre = st.text_input("Nombre")
                apellido = st.text_input("Apellido")
                if st.form_submit_button("Agregar alumno"):
                    if nombre.strip() and apellido.strip():
                        st.session_state.alumnos.append({"id": siguiente_id(st.session_state.alumnos), "nombre": nombre.strip(), "apellido": apellido.strip(), "asignacion_id": aid})
                        st.rerun()
                    st.error("Completá nombre y apellido.")
        with a2:
            datos = [{"ID": x["id"], "Apellido": x["apellido"], "Nombre": x["nombre"]} for x in alumnos_asignacion(aid)]
            st.dataframe(pd.DataFrame(datos), use_container_width=True, hide_index=True)
        with a3:
            datos = [{"Alumno": alumno_nombre(x["id"]), "Asistencia": str(porcentaje_asistencia(x["id"], aid)) + "%"} for x in alumnos_asignacion(aid)]
            st.dataframe(pd.DataFrame(datos), use_container_width=True, hide_index=True)

# CALENDARIO
elif modulo == "🗓️ Calendario":
    st.subheader("🗓️ Calendario académico")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("⬅️ Mes anterior"):
            if st.session_state.mes_calendario == 1:
                st.session_state.mes_calendario = 12
                st.session_state.anio_calendario -= 1
            else:
                st.session_state.mes_calendario -= 1
            st.rerun()
    with c2:
        if st.button("Hoy"):
            h = date.today()
            st.session_state.mes_calendario = h.month
            st.session_state.anio_calendario = h.year
            st.session_state.fecha_calendario_seleccionada = h.isoformat()
            st.rerun()
    with c3:
        if st.button("Mes siguiente ➡️"):
            if st.session_state.mes_calendario == 12:
                st.session_state.mes_calendario = 1
                st.session_state.anio_calendario += 1
            else:
                st.session_state.mes_calendario += 1
            st.rerun()
    with c4:
        st.markdown("### " + MESES[st.session_state.mes_calendario - 1] + " " + str(st.session_state.anio_calendario))

    encabezados = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    cols = st.columns(7)
    for i, nombre in enumerate(encabezados):
        cols[i].markdown("**" + nombre + "**")

    cal = calendar.Calendar(firstweekday=0)
    for semana in cal.monthdayscalendar(st.session_state.anio_calendario, st.session_state.mes_calendario):
        cols = st.columns(7)
        for i, dia in enumerate(semana):
            with cols[i]:
                if dia == 0:
                    st.write("")
                    continue
                fecha = date(st.session_state.anio_calendario, st.session_state.mes_calendario, dia)
                iso = fecha.isoformat()
                texto = ("📍 " if fecha == date.today() else "") + str(dia)
                clave = "dia_" + str(st.session_state.anio_calendario) + "_" + str(st.session_state.mes_calendario) + "_" + str(dia)
                if st.button(texto, key=clave, use_container_width=True):
                    st.session_state.fecha_calendario_seleccionada = iso
                    st.rerun()
                evs = eventos_fecha(iso)
                for ev in evs:
                    st.caption("• " + ev["tipo"] + ": " + ev["descripcion"])

    fecha_sel = st.session_state.fecha_calendario_seleccionada
    st.divider()
    st.subheader("📌 Fecha seleccionada: " + fecha_texto(fecha_sel))
    evs = eventos_fecha(fecha_sel)
    if not evs:
        st.info("No hay eventos registrados para esta fecha.")
    else:
        for ev in evs:
            st.info(ev["tipo"] + ": " + ev["descripcion"])

    ta, tm, te = st.tabs(["➕ Agregar", "✏️ Modificar", "🗑️ Eliminar"])
    with ta:
        v = st.session_state.evento_form_version
        with st.form("evento_nuevo_" + str(v)):
            fecha = st.date_input("Fecha", value=datetime.strptime(fecha_sel, "%Y-%m-%d").date())
            tipo = st.selectbox("Tipo", TIPOS_EVENTO)
            alcance = st.selectbox("Alcance", ["Todas mis clases", "Un curso y materia específicos"])
            aid_evento = None
            if alcance == "Un curso y materia específicos" and st.session_state.asignaciones:
                aid_evento = st.selectbox("Curso y materia", [x["id"] for x in st.session_state.asignaciones], format_func=asignacion_nombre)
            descripcion = st.text_area("Descripción / nota")
            afecta = st.checkbox("Afecta el dictado de clases", value=True)
            if st.form_submit_button("Guardar evento"):
                if not descripcion.strip():
                    st.error("Ingresá una descripción o nota.")
                elif alcance == "Un curso y materia específicos" and aid_evento is None:
                    st.error("Seleccioná el curso y materia.")
                else:
                    st.session_state.eventos_calendario.append({"id": st.session_state.proximo_id_evento, "fecha": fecha.isoformat(), "tipo": tipo, "alcance": alcance, "asignacion_id": aid_evento, "descripcion": descripcion.strip(), "afecta_clases": afecta})
                    st.session_state.proximo_id_evento += 1
                    st.session_state.fecha_calendario_seleccionada = fecha.isoformat()
                    st.session_state.evento_form_version += 1
                    st.rerun()
    with tm:
        if not evs:
            st.info("No hay eventos para modificar.")
        else:
            eid = st.selectbox("Evento", [x["id"] for x in evs], format_func=evento_nombre, key="evento_mod")
            ev = next(x for x in st.session_state.eventos_calendario if x["id"] == eid)
            nueva_fecha = st.date_input("Fecha", value=datetime.strptime(ev["fecha"], "%Y-%m-%d").date(), key="mod_fecha")
            nuevo_tipo = st.selectbox("Tipo", TIPOS_EVENTO, index=TIPOS_EVENTO.index(ev["tipo"]), key="mod_tipo")
            alcances = ["Todas mis clases", "Un curso y materia específicos"]
            nuevo_alcance = st.selectbox("Alcance", alcances, index=alcances.index(ev["alcance"]), key="mod_alcance")
            nuevo_aid = None
            if nuevo_alcance == "Un curso y materia específicos" and st.session_state.asignaciones:
                ids = [x["id"] for x in st.session_state.asignaciones]
                actual = ev["asignacion_id"] if ev["asignacion_id"] in ids else ids[0]
                nuevo_aid = st.selectbox("Curso y materia", ids, index=ids.index(actual), format_func=asignacion_nombre, key="mod_aid")
            nueva_desc = st.text_area("Descripción / nota", value=ev["descripcion"], key="mod_desc")
            nueva_afecta = st.checkbox("Afecta el dictado de clases", value=ev["afecta_clases"], key="mod_afecta")
            if st.button("Guardar cambios", key="save_evento"):
                if nueva_desc.strip():
                    ev["fecha"] = nueva_fecha.isoformat()
                    ev["tipo"] = nuevo_tipo
                    ev["alcance"] = nuevo_alcance
                    ev["asignacion_id"] = nuevo_aid
                    ev["descripcion"] = nueva_desc.strip()
                    ev["afecta_clases"] = nueva_afecta
                    st.session_state.fecha_calendario_seleccionada = nueva_fecha.isoformat()
                    st.rerun()
                st.error("La descripción no puede quedar vacía.")
    with te:
        if not evs:
            st.info("No hay eventos para eliminar.")
        else:
            eid = st.selectbox("Evento", [x["id"] for x in evs], format_func=evento_nombre, key="evento_del")
            if st.button("Eliminar evento", key="delete_evento"):
                st.session_state.eventos_calendario = [x for x in st.session_state.eventos_calendario if x["id"] != eid]
                st.rerun()

# HORARIOS
elif modulo == "🕐 Horarios":
    st.subheader("🕐 Horarios")
    tv, ta, tm, te = st.tabs(["Vista semanal", "Agregar", "Modificar", "Eliminar"])
    with tv:
        cols = st.columns(5)
        for i, dia in enumerate(DIAS):
            with cols[i]:
                st.markdown("### " + dia)
                hs = sorted([x for x in st.session_state.horarios if x["dia"] == dia], key=lambda x: x["hora_inicio"])
                if not hs:
                    st.info("Sin clases registradas")
                for h in hs:
                    st.markdown("**" + asignacion_nombre(h["asignacion_id"]) + "**")
                    st.caption("🕐 " + h["hora_inicio"] + " - " + h["hora_fin"])
    with ta:
        if st.session_state.asignaciones:
            v = st.session_state.horario_form_version
            with st.form("horario_nuevo_" + str(v)):
                dia = st.selectbox("Día", DIAS)
                aid = st.selectbox("Curso y materia", [x["id"] for x in st.session_state.asignaciones], format_func=asignacion_nombre)
                inicio = st.time_input("Hora de inicio", value=time(15, 30))
                fin = st.time_input("Hora de finalización", value=time(17, 20))
                if st.form_submit_button("Guardar horario"):
                    if fin <= inicio:
                        st.error("La hora de finalización debe ser posterior a la de inicio.")
                    elif horario_colisiona(dia, inicio, fin):
                        st.error("Existe otro horario que se superpone en ese día.")
                    else:
                        st.session_state.horarios.append({"id": st.session_state.proximo_id_horario, "asignacion_id": aid, "dia": dia, "hora_inicio": inicio.strftime("%H:%M"), "hora_fin": fin.strftime("%H:%M")})
                        st.session_state.proximo_id_horario += 1
                        st.session_state.horario_form_version += 1
                        st.rerun()
        else:
            st.warning("Primero creá una asignación.")
    with tm:
        if st.session_state.horarios:
            hid = st.selectbox("Horario", [x["id"] for x in st.session_state.horarios], format_func=horario_nombre, key="mod_horario")
            h = next(x for x in st.session_state.horarios if x["id"] == hid)
            dia = st.selectbox("Día", DIAS, index=DIAS.index(h["dia"]), key="mod_h_dia")
            ids = [x["id"] for x in st.session_state.asignaciones]
            aid = st.selectbox("Curso y materia", ids, index=ids.index(h["asignacion_id"]), format_func=asignacion_nombre, key="mod_h_aid")
            inicio = st.time_input("Hora de inicio", value=datetime.strptime(h["hora_inicio"], "%H:%M").time(), key="mod_h_inicio")
            fin = st.time_input("Hora de finalización", value=datetime.strptime(h["hora_fin"], "%H:%M").time(), key="mod_h_fin")
            if st.button("Guardar cambios", key="save_horario"):
                if fin <= inicio:
                    st.error("La hora de finalización debe ser posterior a la de inicio.")
                elif horario_colisiona(dia, inicio, fin, excluir_id=hid):
                    st.error("Existe otro horario que se superpone.")
                else:
                    h["dia"] = dia
                    h["asignacion_id"] = aid
                    h["hora_inicio"] = inicio.strftime("%H:%M")
                    h["hora_fin"] = fin.strftime("%H:%M")
                    st.rerun()
    with te:
        if st.session_state.horarios:
            hid = st.selectbox("Horario", [x["id"] for x in st.session_state.horarios], format_func=horario_nombre, key="del_horario")
            if st.button("Eliminar horario", key="delete_horario"):
                st.session_state.horarios = [x for x in st.session_state.horarios if x["id"] != hid]
                st.rerun()

# ASISTENCIA
elif modulo == "📅 Asistencia":
    st.subheader("📅 Asistencia")
    if st.session_state.asignaciones:
        aid = st.selectbox("Curso y materia", [x["id"] for x in st.session_state.asignaciones], format_func=asignacion_nombre)
        fecha = st.date_input("Fecha", value=date.today())
        iso = fecha.isoformat()
        for ev in eventos_fecha(iso):
            st.info(ev["tipo"] + ": " + ev["descripcion"])
        dia = DIAS[fecha.weekday()] if fecha.weekday() < 5 else None
        if dia is not None and any(x["dia"] == dia and x["asignacion_id"] == aid for x in st.session_state.horarios):
            st.success("Hay una clase registrada en el horario.")
        else:
            st.warning("No hay una clase registrada en el horario para esta fecha.")
        if hay_suspension(iso, aid):
            st.error("El calendario indica que esta fecha afecta el dictado de clases.")
        for alumno in alumnos_asignacion(aid):
            reg = asistencia_existente(alumno["id"], aid, iso)
            actual = reg["estado"] if reg else "Sin registrar"
            opciones = ["Sin registrar", "presente", "ausente", "justificado"]
            estado = st.selectbox(alumno_nombre(alumno["id"]), opciones, index=opciones.index(actual), key="as_" + str(alumno["id"]) + "_" + iso + "_" + str(aid))
            if estado != "Sin registrar":
                if reg:
                    reg["estado"] = estado
                else:
                    st.session_state.asistencias.append({"id": siguiente_id(st.session_state.asistencias), "alumno_id": alumno["id"], "asignacion_id": aid, "fecha": iso, "estado": estado})

# CALIFICACIONES
elif modulo == "📝 Calificaciones":
    st.subheader("📝 Calificaciones")
    if st.session_state.asignaciones:
        aid = st.selectbox("Curso y materia", [x["id"] for x in st.session_state.asignaciones], format_func=asignacion_nombre)
        te, tc, tf = st.tabs(["Evaluaciones", "Cuatrimestres", "Nota final"])
        with te:
            als = alumnos_asignacion(aid)
            if als:
                with st.form("nueva_evaluacion"):
                    al = st.selectbox("Alumno", [x["id"] for x in als], format_func=alumno_nombre)
                    tipo = st.selectbox("Tipo", TIPOS_EVALUACION)
                    fecha = st.date_input("Fecha", value=date.today())
                    nombre = st.text_input("Nombre / tema")
                    if tipo == "Revisión de carpeta":
                        resultado = st.selectbox("Resultado", ["Completa", "Incompleta"])
                    else:
                        resultado = st.selectbox("Resultado", ["Sin registrar", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
                        if resultado == "Sin registrar":
                            resultado = None
                    if st.form_submit_button("Registrar evaluación"):
                        if nombre.strip():
                            st.session_state.evaluaciones.append({"id": siguiente_id(st.session_state.evaluaciones), "alumno_id": al, "asignacion_id": aid, "tipo": tipo, "fecha": fecha.isoformat(), "nombre": nombre.strip(), "resultado": resultado})
                            st.rerun()
                        st.error("Ingresá el nombre o tema.")
                datos = [{"Alumno": alumno_nombre(x["alumno_id"]), "Fecha": fecha_texto(x["fecha"]), "Tipo": x["tipo"], "Evaluación": x["nombre"], "Resultado": "Sin registrar" if x["resultado"] is None else x["resultado"]} for x in st.session_state.evaluaciones if x["asignacion_id"] == aid]
                st.dataframe(pd.DataFrame(datos), use_container_width=True, hide_index=True)
        with tc:
            cuatri = st.selectbox("Cuatrimestre", [1, 2], key="cuatri")
            for al in alumnos_asignacion(aid):
                reg = calificacion_cuatri(al["id"], aid, cuatri)
                conceptual_actual = reg["nota_conceptual"] if reg else "Sin registrar"
                numerica_actual = reg["nota_numerica"] if reg else "Sin registrar"
                st.markdown("#### " + alumno_nombre(al["id"]))
                conceptual = st.selectbox("Nota conceptual", CONCEPTUALES, index=CONCEPTUALES.index(conceptual_actual), key="c_" + str(al["id"]) + "_" + str(cuatri) + "_" + str(aid))
                opciones = ["Sin registrar", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                numerica = st.selectbox("Nota numérica", opciones, index=opciones.index(numerica_actual), key="n_" + str(al["id"]) + "_" + str(cuatri) + "_" + str(aid))
                if st.button("Guardar calificación", key="g_" + str(al["id"]) + "_" + str(cuatri) + "_" + str(aid)):
                    valor = None if numerica == "Sin registrar" else numerica
                    if reg:
                        reg["nota_conceptual"] = conceptual
                        reg["nota_numerica"] = valor
                    else:
                        st.session_state.calificaciones_cuatrimestre.append({"alumno_id": al["id"], "asignacion_id": aid, "cuatrimestre": cuatri, "nota_conceptual": conceptual, "nota_numerica": valor})
                    st.rerun()
        with tf:
            datos = []
            for al in alumnos_asignacion(aid):
                r1 = calificacion_cuatri(al["id"], aid, 1)
                r2 = calificacion_cuatri(al["id"], aid, 2)
                n1 = r1["nota_numerica"] if r1 else None
                n2 = r2["nota_numerica"] if r2 else None
                nf = nota_final(al["id"], aid)
                datos.append({"Alumno": alumno_nombre(al["id"]), "1° cuatrimestre": n1 if n1 is not None else "Pendiente", "2° cuatrimestre": n2 if n2 is not None else "Pendiente", "Nota final": nf if nf is not None else "Pendiente"})
            st.dataframe(pd.DataFrame(datos), use_container_width=True, hide_index=True)

# OBSERVACIONES
elif modulo == "📋 Observaciones":
    st.subheader("📋 Observaciones")
    if st.session_state.asignaciones:
        aid = st.selectbox("Curso y materia", [x["id"] for x in st.session_state.asignaciones], format_func=asignacion_nombre)
        als = alumnos_asignacion(aid)
        if als:
            with st.form("nueva_observacion"):
                al = st.selectbox("Alumno", [x["id"] for x in als], format_func=alumno_nombre)
                fecha = st.date_input("Fecha", value=date.today())
                texto = st.text_area("Observación")
                if st.form_submit_button("Guardar observación"):
                    if texto.strip():
                        st.session_state.observaciones.append({"id": st.session_state.proximo_id_observacion, "alumno_id": al, "asignacion_id": aid, "fecha": fecha.isoformat(), "observacion": texto.strip()})
                        st.session_state.proximo_id_observacion += 1
                        st.rerun()
                    st.error("Ingresá una observación.")
            datos = [{"Alumno": alumno_nombre(x["alumno_id"]), "Fecha": fecha_texto(x["fecha"]), "Observación": x["observacion"]} for x in st.session_state.observaciones if x["asignacion_id"] == aid]
            st.dataframe(pd.DataFrame(datos), use_container_width=True, hide_index=True)

# ESTADÍSTICAS
elif modulo == "📊 Estadísticas":
    st.subheader("📊 Estadísticas")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cursos", len(st.session_state.cursos))
    c2.metric("Asignaciones", len(st.session_state.asignaciones))
    c3.metric("Alumnos", len(st.session_state.alumnos))
    c4.metric("Evaluaciones", len(st.session_state.evaluaciones))
    if st.session_state.asignaciones:
        aid = st.selectbox("Curso y materia", [x["id"] for x in st.session_state.asignaciones], format_func=asignacion_nombre)
        datos = [{"Alumno": alumno_nombre(x["id"]), "Asistencia": str(porcentaje_asistencia(x["id"], aid)) + "%"} for x in alumnos_asignacion(aid)]
        st.dataframe(pd.DataFrame(datos), use_container_width=True, hide_index=True)
