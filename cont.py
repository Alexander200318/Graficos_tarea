import streamlit as st
import requests
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

DB_NAME = 'usuarios3.db'
API_URL = 'https://jsonplaceholder.typicode.com/users'

# Configuración de la página
st.set_page_config(page_title="Análisis de Usuarios", layout="wide")

# Función para cargar datos
@st.cache_data
def cargar_datos():
    response = requests.get(API_URL, timeout=20)
    if response.status_code != 200:
        st.error(f'❌ Error al consumir la API ({response.status_code})')
        return None, None
    
    users = response.json()
    
    # Guardar en SQLite
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS users;')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            username TEXT,
            email TEXT,
            phone TEXT,
            website TEXT
        )
    ''')
    
    for u in users:
        cur.execute('''
            INSERT OR REPLACE INTO users (id, name, username, email, phone, website)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (u.get('id'), u.get('name'), u.get('username'), 
              u.get('email'), u.get('phone'), u.get('website')))
    
    conn.commit()
    conn.close()
    
    # Leer datos
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query('SELECT * FROM users', conn)
    conn.close()
    
    # Transformaciones
    df['name_length'] = df['name'].astype(str).apply(len)
    df['email_domain'] = df['email'].astype(str).apply(
        lambda x: x.split('@')[-1].lower() if '@' in str(x) else None
    )
    
    return df, users

# Cargar datos
df, users = cargar_datos()

# Menú lateral
st.sidebar.title(" Menú")
opcion = st.sidebar.radio(
    "Selecciona una vista:",
    [
        " Portada",
        " Consumir API",
        " Guardar en SQLite",
        " Leer con Pandas",
        " Visualizaciones Plotly",
        " Exportar Gráficos"
    ]
)

if df is not None:
    # Vista según opción seleccionada
    if opcion == " Portada":
        st.title("Proyecto de Análisis de Datos")
        
        st.write("---")
        
        st.subheader("Información del Proyecto")
        st.write("")
        st.write("**Estudiante:** Alexander IsmaelLoja Llivichuzhca")
        st.write("**Carrera:** Desarrollo de software")
        st.write("**Ciclo:** M6A")
        st.write("**Tema:** Análisis de Usuarios mediante API REST")
        st.write("")
        st.write("Sistema de extracción, almacenamiento y visualización de datos utilizando Python, SQLite y Plotly")
        
        st.write("---")
        st.info("Usa el menú lateral para explorar cada paso del proyecto")
    
    elif opcion == " Consumir API":
        st.title("Consumir API con Requests")
        st.subheader("Paso 1: Consumir datos de la API REST")
        
        st.code(f"API_URL = '{API_URL}'", language="python")
        
        st.write(f" Conexión exitosa - Filas recibidas: {len(users)}")
        
        st.write("**Vista previa de los primeros 2 registros:**")
        st.json(users[:2])
        
        with st.expander(" Ver código utilizado"):
            st.code("""
response = requests.get(API_URL, timeout=20)
if response.status_code != 200:
    raise SystemExit(f' Error al consumir la API ({response.status_code})')
users = response.json()
print(f'Filas recibidas: {len(users)}')
            """, language="python")
    
    elif opcion == " Guardar en SQLite":
        st.title("Guardar en SQLite")
        st.subheader("Paso 2: Persistir datos en base de datos SQLite")
        
        st.write(f"Base de datos: **{DB_NAME}**")
        st.write(f" {len(df)} registros guardados exitosamente")
        
        st.write("**Estructura de la tabla users:**")
        estructura = pd.DataFrame({
            'Campo': ['id', 'name', 'username', 'email', 'phone', 'website'],
            'Tipo': ['INTEGER PRIMARY KEY', 'TEXT', 'TEXT', 'TEXT', 'TEXT', 'TEXT']
        })
        st.table(estructura)
        
        with st.expander(" Ver código utilizado"):
            st.code("""
conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS users;')

cur.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    username TEXT,
    email TEXT,
    phone TEXT,
    website TEXT
)
''')

for u in users:
    cur.execute('''
        INSERT OR REPLACE INTO users (id, name, username, email, phone, website)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (u.get('id'), u.get('name'), u.get('username'), 
          u.get('email'), u.get('phone'), u.get('website')))

conn.commit()
conn.close()
            """, language="python")
    
    elif opcion == " Leer con Pandas":
        st.title("Leer con Pandas")
        st.subheader("Paso 3: Cargar datos desde SQLite a DataFrame")
        
        st.write(f" {len(df)} registros cargados exitosamente")
        
        st.write("**DataFrame completo:**")
        st.dataframe(df, use_container_width=True)
        
        st.write("**Primeras 5 filas:**")
        st.dataframe(df.head(), use_container_width=True)
        
        with st.expander(" Ver código utilizado"):
            st.code("""
conn = sqlite3.connect(DB_NAME)
df = pd.read_sql_query('SELECT * FROM users', conn)
conn.close()
df.head()
            """, language="python")
    
    elif opcion == "🔧 Feature Engineering":
        st.title("Feature Engineering")
        st.subheader("Paso 4: Crear nuevas características")
        
        st.write("**Transformaciones aplicadas:**")
        st.write("1. name_length: Longitud del nombre de usuario")
        st.write("2. email_domain: Dominio extraído del correo electrónico")
        
        st.dataframe(df[['id','name','name_length','email','email_domain']].head(10), 
                    use_container_width=True)
        
        st.write(f"- Promedio caracteres nombre: {df['name_length'].mean():.1f}")
        st.write(f"- Dominios únicos: {df['email_domain'].nunique()}")
        st.write(f"- Nombre más largo: {df['name_length'].max()} caracteres")
        st.write(f"- Nombre más corto: {df['name_length'].min()} caracteres")
        
        with st.expander(" Ver código utilizado"):
            st.code("""
# Longitud del nombre
df['name_length'] = df['name'].astype(str).apply(len)

# Dominio del email
df['email_domain'] = df['email'].astype(str).apply(
    lambda x: x.split('@')[-1].lower() if '@' in str(x) else None
)
            """, language="python")
    
    elif opcion == " Visualizaciones Plotly":
        st.title("Visualizaciones con Plotly")
        st.subheader("Paso 5: Análisis gráfico de los datos")
        
        # Histograma
        st.write("**Distribución de caracteres en los nombres**")
        fig1 = px.histogram(df, x='name_length', nbins=10, 
                           title='Distribución de caracteres en los nombres')
        fig1.update_layout(xaxis_title='Cantidad de caracteres', 
                          yaxis_title='Frecuencia')
        st.plotly_chart(fig1, use_container_width=True)
        
        # Gráfico de barras
        st.write("**Usuarios por dominio de correo electrónico**")
        dom_counts = df['email_domain'].value_counts().reset_index()
        dom_counts.columns = ['email_domain', 'count']
        
        fig2 = px.bar(dom_counts, x='count', y='email_domain', 
                     orientation='h',
                     title='Usuarios por dominio de correo electrónico')
        fig2.update_layout(xaxis_title='Cantidad de usuarios', 
                          yaxis_title='Dominio')
        st.plotly_chart(fig2, use_container_width=True)
        
        # Gráfico de donut
        st.write("**Distribución de dominios de email (Donut)**")
        fig3 = px.pie(dom_counts, names='email_domain', values='count', 
                     hole=0.4,
                     title='Distribución de dominios de email')
        st.plotly_chart(fig3, use_container_width=True)
        
        # NUEVA GRÁFICA 1: Gráfico de dispersión
        st.write("**Relación entre ID y longitud del nombre**")
        fig5 = px.scatter(df, x='id', y='name_length', 
                         size='name_length',
                         color='email_domain',
                         hover_data=['name', 'username'],
                         title='Relación entre ID de usuario y longitud del nombre')
        fig5.update_layout(xaxis_title='ID Usuario', 
                          yaxis_title='Longitud del nombre')
        st.plotly_chart(fig5, use_container_width=True)
        
        # NUEVA GRÁFICA 2: Gráfico de líneas
        st.write("**Evolución de la longitud de nombres por usuario**")
        df_sorted = df.sort_values('id')
        fig6 = px.line(df_sorted, x='id', y='name_length', 
                      markers=True,
                      title='Evolución de la longitud de nombres por ID de usuario')
        fig6.update_layout(xaxis_title='ID Usuario', 
                          yaxis_title='Longitud del nombre')
        fig6.update_traces(line_color='#FF6B6B', marker=dict(size=8))
        st.plotly_chart(fig6, use_container_width=True)
        
        
    
    elif opcion == " Exportar Gráficos":
        st.title("Exportar Gráficos")
        st.subheader("Paso 6: Exportar visualizaciones a HTML")
        
        st.write("Puedes exportar cualquier gráfico de Plotly a un archivo HTML")
        
        # Generar gráfico de ejemplo
        fig = px.histogram(df, x='name_length', nbins=10, 
                          title='Ejemplo de exportación')
        st.plotly_chart(fig, use_container_width=True)
        
        # Botón para descargar
        html_str = fig.to_html(include_plotlyjs='cdn')
        st.download_button(
            label="Descargar gráfico como HTML",
            data=html_str,
            file_name="hist_name_length.html",
            mime="text/html"
        )
        
        st.write(" El archivo HTML incluye toda la interactividad de Plotly")

else:
    st.error("No se pudieron cargar los datos")

# Footer
st.sidebar.markdown("---")
st.sidebar.write("Navega por cada paso del proyecto")