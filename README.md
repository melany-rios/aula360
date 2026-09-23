# aula360
Sistema de gestión y seguimiento docente para administrar asistencia, calificaciones y observaciones de alumnos de múltiples cursos y materias.

# Aula360

### Sistema de gestión y seguimiento docente

Aula360 es una aplicación web desarrollada con **Python y Streamlit** para facilitar la gestión y el seguimiento de alumnos de diferentes cursos y materias.

El proyecto busca centralizar en un único sistema información que habitualmente se encuentra distribuida en planillas, cuadernos y diferentes registros, permitiendo llevar un seguimiento organizado de **asistencia, calificaciones, trabajos prácticos y observaciones de los estudiantes**.

La aplicación está pensada especialmente para docentes que trabajan con múltiples cursos y necesitan consultar rápidamente la situación académica de sus alumnos.

---

## 🎯 Objetivo

El objetivo de Aula360 es desarrollar una herramienta sencilla, intuitiva y adaptable que permita:

* Gestionar diferentes cursos y materias.
* Registrar y consultar la asistencia de los alumnos.
* Registrar calificaciones y diferentes instancias de evaluación.
* Realizar observaciones y seguimiento individual.
* Consultar el historial de cada estudiante.
* Obtener estadísticas generales de cada curso.
* Detectar situaciones que requieran seguimiento.
* Centralizar la información académica en un único lugar.
* Generar reportes para facilitar la tarea docente.

---

## 🚀 Funcionalidades

### 👥 Gestión de alumnos

* Registro de alumnos.
* Organización por curso y división.
* Consulta de información individual.
* Visualización del historial académico.

### 📅 Gestión de asistencia

* Registro de asistencia por fecha.
* Control de presentes y ausentes.
* Cálculo automático del porcentaje de asistencia.
* Seguimiento de alumnos con baja asistencia.

### 📝 Gestión de calificaciones

* Registro de notas.
* Diferentes tipos de evaluaciones:

  * Evaluaciones escritas.
  * Trabajos prácticos.
  * Recuperatorios.
  * Exposiciones.
  * Proyectos.
  * Otras instancias.
* Consulta del historial de calificaciones.
* Cálculo de promedios.

### 📋 Observaciones

Registro de observaciones relacionadas con el seguimiento del alumno, por ejemplo:

* Participación.
* Carpeta.
* Trabajos prácticos.
* Evaluaciones.
* Asistencia.
* Desempeño.
* Situaciones particulares.

### 📊 Dashboard

Panel de información general del curso con indicadores como:

* Cantidad de alumnos.
* Porcentaje de asistencia.
* Promedio general.
* Alumnos con situaciones a revisar.
* Trabajos pendientes.
* Información académica relevante.

### 📄 Reportes

Se prevé incorporar herramientas para generar y exportar información de:

* Asistencia.
* Calificaciones.
* Seguimiento individual.
* Información general de los cursos.

---

## 🛠️ Tecnologías

El proyecto se desarrolla utilizando:

* **Python**
* **Streamlit**
* **Pandas**
* **MySQL** para persistencia de datos
* **Git**
* **GitHub**

La arquitectura está pensada para permitir incorporar nuevas funcionalidades progresivamente.

---

## 🏗️ Arquitectura prevista

La aplicación seguirá una arquitectura sencilla:

```text
Aula360
│
├── Interfaz web
│   └── Streamlit
│
├── Lógica de aplicación
│   └── Python
│
├── Gestión de datos
│   └── Pandas
│
└── Base de datos
    └── MySQL
```

La estructura podrá evolucionar a medida que se incorporen nuevos módulos.

---

## 📚 Módulos previstos

El desarrollo se realizará progresivamente.

### Primera etapa

* [ ] Dashboard principal
* [ ] Gestión de cursos
* [ ] Gestión de alumnos
* [ ] Registro de asistencia
* [ ] Registro de calificaciones
* [ ] Registro de observaciones

### Segunda etapa

* [ ] Historial individual del alumno
* [ ] Estadísticas por curso
* [ ] Promedios
* [ ] Control de trabajos prácticos
* [ ] Seguimiento de evaluaciones
* [ ] Alertas de asistencia

### Tercera etapa

* [ ] Reportes
* [ ] Exportación a Excel/CSV
* [ ] Generación de informes
* [ ] Gestión de cuatrimestres
* [ ] Historial académico
* [ ] Mejoras de interfaz

---

## 💻 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/USUARIO/aula360.git
```

Ingresar al directorio:

```bash
cd aula360
```

### 2. Crear un entorno virtual

```bash
python -m venv venv
```

Activar el entorno virtual.

En Windows:

```bash
venv\Scripts\activate
```

En Linux/Mac:

```bash
source venv/bin/activate
```

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá en el navegador.

---

## 📁 Estructura del proyecto

La estructura inicial prevista es:

```text
aula360/
│
├── app.py
├── requirements.txt
├── README.md
│
├── data/
│   └── ...
│
├── database/
│   └── ...
│
├── modules/
│   └── ...
│
└── assets/
    └── ...
```

Esta estructura podrá modificarse durante el desarrollo para mantener el proyecto organizado y facilitar su mantenimiento.

---

## 🔐 Datos y privacidad

Aula360 está pensado para trabajar con información académica de estudiantes.

Durante el desarrollo se utilizarán **datos ficticios** para las pruebas y demostraciones.

Si el sistema se utiliza con información real, se deberán implementar medidas adecuadas de seguridad, control de acceso, protección de datos y copias de seguridad.

---

## 🗺️ Estado del proyecto

🚧 **En desarrollo**

Aula360 se encuentra actualmente en etapa de desarrollo inicial.

Las funcionalidades se irán incorporando progresivamente, comenzando por la gestión básica de alumnos, asistencia, calificaciones y observaciones.

---

## 👩‍💻 Autora

**Melany Ayelén Ríos Santillán**

Proyecto desarrollado como herramienta de apoyo para la gestión y el seguimiento de la actividad docente.

---

## 📄 Licencia

La licencia del proyecto será definida durante el desarrollo.
