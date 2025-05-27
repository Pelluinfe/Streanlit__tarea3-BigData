# Importamos las bibliotecas necesarias
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import plotly.express as px
# CONFIGURACIÓN DEL DASHBOARD

# Configuración básica de la página con más opciones comentadas
st.set_page_config(
    page_title="Dashboard Ventas Supermercado", 
    page_icon="🏷️", 
    initial_sidebar_state='expanded', 
    menu_items={
        'About': """
        ## Dashboard Ventas Supermercado
        Este dashboard muestra un análisis de las ventas de supermercados.
        Desarrollado por Omar Garcia.
        """ 
    }
)

# Título principal dentro de la página
st.title("Sales Analysis DashBoard 💲🏷️") # Esto es diferente al page_title de la pestaña

st.markdown("""
Dash Board sales Birmania 📍 
* **Omar Nicolas Garcia Gomez**
            """)


# Cargamos el dataset a traves de una función en memoria caché
@st.cache_data
def cargar_datos():
    df = pd.read_csv("data.csv")
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
    df['Time'] = pd.to_datetime(df['Time'], format='%H:%M', errors='coerce')
    df['Hour'] = df['Time'].dt.hour
    df['Month'] = df['Date'].dt.month_name()
    df['Day'] = df['Date'].dt.day_name()
    df.dropna(inplace=True)
    return df

df = cargar_datos()
#------------------------------------------------------------------------------------
## Filtros Laterales
with st.sidebar:
    st.header("🔍 Filtros")
    fecha_min = df['Date'].min()
    fecha_max = df['Date'].max()
    fecha_rango = st.date_input(
    "📅 Rango de Fechas",
    (fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max
    )

    df_filtrado = df[(df['Date'] >= pd.to_datetime(fecha_rango[0])) & (df['Date'] <= pd.to_datetime(fecha_rango[1]))]

    st.write("Categorías 🗃️")
    categorias = {
        'Tipo de cliente': df["Customer type"].unique(),
        'Ciudad': df["City"].unique(),
        'Sucursal': df["Branch"].unique(),
        'Método de pago': df["Payment"].unique(),
        'Género': ['Male', 'Female'],
        'Línea de producto': df["Product line"].unique(),
    }

    # FILTRADO DE DATOS
    # Crear los multiselects dinámicamente
    selecciones = {}
    for nombre, opciones in categorias.items():
        selecciones[nombre] = st.sidebar.multiselect(nombre, opciones, opciones)

    # Acceso a los valores seleccionados:
    branch = selecciones['Sucursal']
    city = selecciones['Ciudad']
    customer = selecciones['Tipo de cliente']
    gender = selecciones['Género']
    product = selecciones['Línea de producto']
    payment = selecciones['Método de pago']

    df_selected_sales = df_filtrado[(df_filtrado["Branch"].isin(branch))
                            & (df_filtrado["City"].isin(city))
                            & (df_filtrado["Customer type"].isin(customer))
                            & (df_filtrado["Gender"].isin(gender))
                            & (df_filtrado["Product line"].isin(product))
                            & (df_filtrado["Payment"].isin(payment))]

# ----------------------------------------------------------------------
# Informacion del DataSet
st.divider()
st.header("Información del Dataset 📊")
st.markdown("*** Información de registros 👀***")

col1, col2, col3 = st.columns(3)
with col1: st.metric("Fecha inicio 📆", f"{df['Date'].min()}")
with col2: st.metric("Fecha fin 📆", f"{df['Date'].max()}")
with col3:
    total_transacciones = len(df_filtrado)
    st.metric("Total Transacciones 🧾", f"{total_transacciones:,}")

st.markdown("** Indicadores Clave 🔥**")
col1, col2, col3 = st.columns(3)
with col1: 
    st.metric("Ventas Totales 🚀", f"${df_selected_sales['Total'].sum():,.1f} ")
    st.caption("Suma total de ventas en el periodo filtrado, útil para evaluar ingresos generales.")
with col2: 
    st.metric("Rating promedio ⭐", f"{df_selected_sales['Rating'].mean():.1f}")
    st.caption("Promedio de ingresos por día: útil para campañas por fecha o eventos especiales.")
with col3: 
    st.metric("Ingreso Bruto Total 📈", f"{df_selected_sales['gross income'].sum():,.1f}")
    st.caption("Suma total de ingresos brutos, útil para evaluar la rentabilidad general.")

st.markdown("---")

# -------------------------------
# Tabs 
tabs = st.tabs(["📈 Ventas", "📦 Productos", "🔎 Data 3D"])

# -------------------------------
# Tab Ventas 
with tabs[0]:
    # -----------------------------------
    # Gráfico de Ventas Totales por Fecha
    st.header("Análisis de Ventas Totales 📈")
    st.subheader("Evolución de las Ventas Totales Diarias")
    # Agrupar por fecha
    ventas_diarias = df_selected_sales.groupby('Date')['Total'].sum().reset_index()

    # Calcular el promedio de las ventas totales diarias
    promedio_ventas_totales = ventas_diarias['Total'].mean()

    # Gráfico interactivo
    fig = px.line(
        ventas_diarias,
        x='Date',
        y='Total',
        title='Evolución de las Ventas Totales y Promedio', # Actualizamos el título
        markers=True,
        labels={'Date': 'Fecha', 'Total': 'Ventas Totales (USD)'}
    )

    # Personalización del color de la línea de ventas
    fig.update_traces(line_color='mediumseagreen') # Cambiado a un color diferente

    # Añadir una línea horizontal para el promedio
    fig.add_shape(type="line",
                x0=ventas_diarias['Date'].min(), x1=ventas_diarias['Date'].max(),
                y0=promedio_ventas_totales, y1=promedio_ventas_totales,
                line=dict(color="red", width=2, dash="dash"), # Línea roja punteada para el promedio
                xref='x', yref='y')

    # Añadir una anotación para el valor del promedio
    fig.add_annotation(
        x=ventas_diarias['Date'].median(), # Posición x al final del gráfico
        y=promedio_ventas_totales,     # Posición y en el valor del promedio
        text=f"Mean:{promedio_ventas_totales:.1f}", # Texto con el valor del promedio formateado
        showarrow=True,
        arrowhead=2,
        xanchor="left",
        yanchor="bottom"
    )


    fig.update_layout(
        xaxis_title='Fecha',
        yaxis_title='Ventas Totales (USD)',
        title_x=00.5,
        template='plotly_white',
        yaxis=dict(range=[0, None]), # El límite de Y parte desde 0
        showlegend=False # Ocultamos la leyenda si solo tenemos una línea de datos
    )

    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Ventas Totales por Ciudad y Tipo de Pago")

        # Agrupar por Ciudad y Método de Pago y sumar ventas
        df_cityPaymentTotal = df_selected_sales.groupby(["City", "Payment"])["Total"].sum().reset_index()

        # Crear gráfico
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(data=df_cityPaymentTotal, x='City', y='Total', hue='Payment', ax=ax)

        ax.set_title('Ventas Totales por Ciudad y Tipo de Pago', fontsize=14)
        ax.set_xlabel('Ciudad')
        ax.set_ylabel('Ventas Totales (USD)')

        # Mostrar valores sobre cada barra
        for container in ax.containers:
            ax.bar_label(container, fmt='%.2f', label_type='edge')

        st.pyplot(fig)
    with col2:
        st.subheader("Ingreso Bruto por Género y Línea de Producto")

        # Agrupar datos
        data_agrupada = df_selected_sales.groupby(['Gender', 'Product line'])['gross income'].sum().unstack().fillna(0)

        # Crear gráfico
        fig, ax = plt.subplots(figsize=(8, 5))
        bottom = None

        for column in data_agrupada.columns:
            bars = ax.bar(data_agrupada.index, data_agrupada[column], bottom=bottom, label=column)
            if bottom is None:
                bottom = data_agrupada[column]
            else:
                bottom += data_agrupada[column]

        ax.set_title('Composición del ingreso bruto por género y línea de producto', fontsize=14)
        ax.set_xlabel('Género')
        ax.set_ylabel('Ingreso Bruto')
        ax.legend(title='Línea de Producto')

        st.pyplot(fig)
        

with tabs[1]:
    # ------------------------------------
    # Tab Productos
    st.header("Análisis de Productos 📦")
    st.subheader("Estadísticas Generales:")
    # Mostrar estadísticas generales
    st.write(df_selected_sales['Product line'].value_counts())

    # Gráfico de Ingresos por Línea de Producto

    st.subheader("Gráfico de Ingresos por Línea de Producto")

    # Agrupar los ingresos por línea de producto
    ingresos_por_producto = df_selected_sales.groupby('Product line')['gross income'].sum().reset_index()

    # Crear gráfico de barras vertical
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(ingresos_por_producto['Product line'], ingresos_por_producto['gross income'], color='skyblue')
    ax.set_title('Ingresos por Línea de Producto', fontsize=14)
    ax.set_xlabel('Línea de Producto')
    ax.set_ylabel('Ingreso Bruto')
    plt.xticks(rotation=45)
    st.pyplot(fig)
    
    st.write("Correlacion entre datos:")

    # Generar la matriz de correlación
    st.subheader("Correlación entre Variables")
    correlation_matrix = df[['Unit price', 'Quantity', 'Tax 5%', 'Total', 'cogs', 'gross income', 'Rating']].corr()

    # Crear el heatmap
    fig, ax = plt.subplots()
    sns.heatmap(np.round(correlation_matrix, 2), annot=True, cmap='viridis', center=0, linewidths=0.6, linecolor='white', ax=ax)
    ax.set_title("Matriz de Correlación de Variables Numéricas")
    st.pyplot(fig)
    
    
with tabs[2]:
    # ------------------------------------
    # plot 3d
    st.header("Graficos 3D 🔎")
    st.subheader("Grafico 3D de los datos agrupados por simbolo")
    df_selected_sales_3d = df_selected_sales.copy()
    numeric_cols = df_selected_sales.select_dtypes(include=['number']).columns
    if len(numeric_cols) < 3:
        st.error("No hay suficientes columnas numéricas para crear un gráfico 3D.")
        st.stop()
    col_x = st.selectbox("Columna para eje X", numeric_cols)
    df_selected_sales_3d= df_selected_sales_3d.dropna(subset=[col_x]) # Eliminar filas con NaN en col_x
    numeric_cols=numeric_cols.drop(col_x)  # Excluir col_x de las opciones para Y y Z
    if len(numeric_cols) < 2:
        st.error("No hay suficientes columnas numéricas para crear un gráfico 3D.")
        st.stop()
    col_y = st.selectbox("Columna para eje Y", numeric_cols)
    df_selected_sales_3d = df_selected_sales_3d.dropna(subset=[col_y]) # Eliminar filas con NaN en col_y
    numeric_cols=numeric_cols.drop(col_y)  # Excluir col_x de las opciones para Y y Z
    if len(numeric_cols) < 2:
        st.error("No hay suficientes columnas numéricas para crear un gráfico 3D.")
        st.stop()
    col_z = st.selectbox("Columna para eje Z", numeric_cols)

    fig = px.scatter_3d(
        df_selected_sales,
        x=col_x,
        y=col_y,
        z=col_z,
        color=col_z,  # Puedes cambiar esto si quieres colorear por otra variable
        color_continuous_scale='viridis'
    )

    fig.update_layout(
        scene=dict(
            xaxis_title=col_x,
            yaxis_title=col_y,
            zaxis_title=col_z
        )
    )

    st.plotly_chart(fig, use_container_width=True)
