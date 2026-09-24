# ==========================================
# DATOS DE PRUEBA - AULA360
# ==========================================


# ==========================================
# MATERIAS
# ==========================================

materias = [
    {
        "id": 1,
        "nombre": "Sistemas Informáticos"
    },
    {
        "id": 2,
        "nombre": "Software III"
    },
    {
        "id": 3,
        "nombre": "Software II"
    },
    {
        "id": 4,
        "nombre": "Hardware"
    }
]


# ==========================================
# CURSOS
# ==========================================

cursos = [
    {
        "id": 1,
        "nombre": "5° 1°"
    },
    {
        "id": 2,
        "nombre": "4° 1°"
    },
    {
        "id": 3,
        "nombre": "4° 2°"
    }
]


# ==========================================
# ASIGNACIONES DE MATERIAS
# ==========================================

# Relaciona un curso con una materia.
# Una misma materia podría existir en diferentes cursos.

asignaciones = [
    {
        "id": 1,
        "curso_id": 1,
        "materia_id": 1
    },
    {
        "id": 2,
        "curso_id": 1,
        "materia_id": 2
    },
    {
        "id": 3,
        "curso_id": 2,
        "materia_id": 3
    },
    {
        "id": 4,
        "curso_id": 3,
        "materia_id": 4
    }
]


# ==========================================
# ALUMNOS
# ==========================================

alumnos = [
    {
        "id": 1,
        "nombre": "Sofía",
        "apellido": "Gómez",
        "asignacion_id": 1
    },
    {
        "id": 2,
        "nombre": "Mateo",
        "apellido": "López",
        "asignacion_id": 1
    },
    {
        "id": 3,
        "nombre": "Valentina",
        "apellido": "Pérez",
        "asignacion_id": 1
    },
    {
        "id": 4,
        "nombre": "Tomás",
        "apellido": "Rodríguez",
        "asignacion_id": 1
    },
    {
        "id": 5,
        "nombre": "Camila",
        "apellido": "Fernández",
        "asignacion_id": 2
    },
    {
        "id": 6,
        "nombre": "Lucas",
        "apellido": "Martínez",
        "asignacion_id": 2
    },
    {
        "id": 7,
        "nombre": "Martina",
        "apellido": "Díaz",
        "asignacion_id": 2
    },
    {
        "id": 8,
        "nombre": "Joaquín",
        "apellido": "Sánchez",
        "asignacion_id": 3
    },
    {
        "id": 9,
        "nombre": "Agustina",
        "apellido": "Romero",
        "asignacion_id": 3
    },
    {
        "id": 10,
        "nombre": "Franco",
        "apellido": "Torres",
        "asignacion_id": 4
    },
    {
        "id": 11,
        "nombre": "Micaela",
        "apellido": "Ruiz",
        "asignacion_id": 4
    }
]


# ==========================================
# ASISTENCIA DE PRUEBA
# ==========================================

# Estados posibles:
#
# presente
# ausente
# justificado

asistencias = [
    {
        "id": 1,
        "alumno_id": 1,
        "asignacion_id": 1,
        "fecha": "2026-09-02",
        "estado": "presente"
    },
    {
        "id": 2,
        "alumno_id": 2,
        "asignacion_id": 1,
        "fecha": "2026-09-02",
        "estado": "presente"
    },
    {
        "id": 3,
        "alumno_id": 3,
        "asignacion_id": 1,
        "fecha": "2026-09-02",
        "estado": "ausente"
    },
    {
        "id": 4,
        "alumno_id": 4,
        "asignacion_id": 1,
        "fecha": "2026-09-02",
        "estado": "justificado"
    },
    {
        "id": 5,
        "alumno_id": 1,
        "asignacion_id": 1,
        "fecha": "2026-09-09",
        "estado": "presente"
    },
    {
        "id": 6,
        "alumno_id": 2,
        "asignacion_id": 1,
        "fecha": "2026-09-09",
        "estado": "ausente"
    },
    {
        "id": 7,
        "alumno_id": 3,
        "asignacion_id": 1,
        "fecha": "2026-09-09",
        "estado": "presente"
    },
    {
        "id": 8,
        "alumno_id": 4,
        "asignacion_id": 1,
        "fecha": "2026-09-09",
        "estado": "presente"
    }
]
