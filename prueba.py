#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import itertools
import pgmpy
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

import dash
from dash import dcc  # dash core components
from dash import html # dash html components
from dash.dependencies import Input, Output

import plotly.express as px
import pandas as pd

from pgmpy.sampling import BayesianModelSampling

na_values = ["?"]

df=pd.read_csv("/Users/paulaescobar/Documents/ACTD/Proyecto1/processed.cleveland.data.csv", sep = ",", na_values = na_values, header = None)

# Renombrar columnas
df.columns
df.columns = (["age", "sex", "cp", "trestbps", "chol", "fbs",
              "restecg", "thalach", "exang", "oldpeak", "slope",
              "ca", "thal", "num"])

df = df.dropna()

model = BayesianNetwork ([( "age" , "fbs" ),
                          ( "age" , "chol" ),
                          ( "age", "trestbps" ),
                          ( "age" , "thalach" ),
                          ( "sex", "chol" ),
                          ( "cp" , "thal" ),
                          ( "cp" , "slope" ),
                          ( "cp" , "num" ),
                          ( "cp", "restecg" ),
                          ( "trestbps" , "cp" ),
                          ( "chol" , "trestbps" ),
                          ( "fbs" , "trestbps" ),
                          ( "restecg", "slope" ),
                          ( "restecg" , "num" ),
                          ( "thalach" , "slope" ),
                          ( "exang" , "cp" ),
                          ( "exang" , "num" ),
                          ( "oldpeak" , "num" ),
                          ( "slope" , "oldpeak" ),
                          ( "num" , "thal" ),
                          ( "num" , "ca" )])



from pgmpy.estimators import MaximumLikelihoodEstimator
from sklearn.preprocessing import LabelEncoder as le

# EDAD
df["age"] = pd.cut(df['age'], bins=4, labels=['29-39', '40-49', '50-59', '60-79'])

# PRESIÓN SANGUÍNEA EN REPOSO
intervalos2 = [0, 80, 120, 129, 139, 179, 600]
categorias2 = ['hipotensión', 'normal', 'elevada', 'hiptertensión nivel 1', 'hiptertensión nivel 2', 'crisis hipertensión']
df['trestbps'] = pd.cut(df['trestbps'], bins=intervalos2, labels=categorias2)

# OLDPEAK
intervalos3 = [-1, 1.5, 2.5, 6.2]
categorias3 = ['baja', 'normal', 'terrible']
df['oldpeak'] = pd.cut(df['oldpeak'], bins=intervalos3, labels=categorias3)

# COLESTEROL
intervalos = [0, 200, 239, 600]
categorias = ['saludable', 'riesgoso', 'peligroso']
df['chol'] = pd.cut(df['chol'], bins=intervalos, labels=categorias)

# THALACH

categoria_edad = ['29-39', '40-49', '50-59', '60-79']
categoria_frec = ['inadecuado', 'normal', 'buena', 'excelente']

rangos = {('29-39'):{'inadecuado': (84,300),
                   'normal': (72,84),
                   'buena': (64,71),
                   'excelente': (60,62)},
          
          ('40-49'):{'inadecuado': (90,300),
                   'normal': (74,89),
                   'buena': (66,73),
                   'excelente': (64,66)},
          
                    
          ('50-59'):{'inadecuado': (90,300),
                   'normal': (76,89),
                   'buena': (68,75),
                   'excelente': (66,67)},
          
          ('60-79'):{'inadecuado': (90,300),
                   'normal': (76,89),
                   'buena': (68,75),
                   'excelente': (66,67)}
          }

df['thalach'] = df.apply( lambda row: 'inadecuado' if row['thalach'] < rangos[row['age']]['inadecuado'][0] 
                                                      or row['thalach'] > rangos[row['age']]['inadecuado'][1] 
                                                      else ('normal' if row['thalach'] < rangos[row['age']]['normal'][1] 
                                                                      else ('buena' if row['thalach'] < rangos[row['age']]['buena'][1] 
                                                                                      else 'excelente')), axis=1)


df.to_csv('datosDiscretizados.csv', index=False)
emv = MaximumLikelihoodEstimator( model = model , data = df )
# Estimar para nodos sin padres
# Estimar para nodo age
cpdem_age = emv.estimate_cpd(node ="age")
#print( cpdem_age )
# Estimar para nodo sex
cpdem_sex = emv.estimate_cpd(node ="sex")
#print( cpdem_sex )
# Estimar para nodo exang
cpdem_exang = emv.estimate_cpd(node ="exang")
#print( cpdem_exang )
model.fit(data=df , estimator = MaximumLikelihoodEstimator)
#for i in model.nodes():
    #print(model.get_cpds(i))
    

infer = VariableElimination(model)

posterior_num = infer.query(["num"], evidence={"age": '29-39', "sex": 1, 'exang': 1, 'chol': 'riesgoso', 'trestbps': 'elevada', 'fbs': 0})
print(posterior_num )

    #intento fallido de estimación por metodo de Bayer
#from pgmpy.estimators import BayesianEstimator

"""ps= [3000,3000,3000]
ps *= 72

pseudoC =[ps] 
pseudoC *= 5

eby = BayesianEstimator ( model = model , data = df ) 
cpdby_num = eby.estimate_cpd(node="num", prior_type="dirichlet", pseudo_counts= pseudoC)
print(cpdby_num)"""


#TABLERO DASH

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div(children=[
    
    html.H1("Herramienta de apoyo de analítica de datos en el proceso de evaluación de pacientes y la toma de decisiones asociada",
            style={'text-align': 'center', 'color': 'white', 'backgroundColor': '#0b0347'}),

    html.H2("Sección 1: Estimación de probabilidades del resultado del paciente para un exámen médico determinado",
            style={'backgroundColor': '#6a94c4'}),

    html.Div(children=[
    
        html.H5("Seleccione el exámen de interés:"),
    
        html.Div(
            className="Seleccion", children=[
                dcc.Dropdown(
                    id="dropdownExamen",
                    options=['Estado del corazón según prueba Thallium', 
                             'Tipo de dolor en el pecho',
                             'Resultados de electrocardiograma en reposo',
                             'Máxima frecuencia cardiaca',
                             'Depresión del ST inducida por el ejercicio en relación con el descanso',
                             'Pendiente del segmento ST',
                             'Número de vasos principales coloreados por fluoroscopia'],
                    value="Estado del corazón según prueba Thallium",
                    clearable=False,
                    ),
            ],),
        
        html.Br(),
        
        html.Div(children=[
            html.Div(children=[
                    html.Label("Seleccione el rango de edad:", htmlFor = "dropdownEdad"),
                    dcc.Dropdown(
                        id="dropdownEdad",
                        options=['29-39', '40-49', '50-59', '60-79'],
                        value='29-39',
                        clearable=False,
                        ),
                    ],style=dict(width='33%')),
            
            html.Div(children=[
                    html.Label("Seleccione el sexo:", htmlFor = "dropdownSexo"),
                    dcc.Dropdown(
                        id="dropdownSexo",
                        options=["Femenino","Masculino"],
                        value="Femenino",
                        clearable=False,
                        ),
                ],style=dict(width='33%')),
            
             html.Div(children=[
                    html.Label("Seleccione angina inducida por ejercicio:", htmlFor = "dropdownAngina"),
                    dcc.Dropdown(
                        id="dropdownAngina",
                        options=['No tiene angina inducida por ejercicio','Tiene angina inducida por ejercicio'],
                        value='No tiene angina inducida por ejercicio',
                        clearable=False,
                        ),
                ],style=dict(width='33%')),
             ],style=dict(display='flex')),
        
        html.Br(),
        
        html.H4("Distribución de probabilidad para resultados del paciente según edad, sexo y angina para un exámen en particular:"),
        
        dcc.Graph(id='graph'),
        
        html.H2("Sección 2: Estimación de probabilidades del diagnóstico del paciente respecto a la enfermedad cardiaca",
                style={'backgroundColor': '#6a94c4'}),

        html.Div(children=[
            html.Div(children=[
                    html.Label("Seleccione el rango de colesterol en mg/dl:", htmlFor = "dropdownCol"),
                    dcc.Dropdown(
                        id="dropdownCol",
                        options=['< 200', '200-239', '240 >='],
                        value='< 200',
                        clearable=False,
                        ),
                    ],style=dict(width='33%')),
            
            html.Div(children=[
                    html.Label("Seleccione el rango de presión arterial en reposo en mm Hg:", htmlFor = "dropdownPre"),
                    dcc.Dropdown(
                        id="dropdownPre",
                        options=['80-120', '120-129', '130-139', '140-180', '180 >='],
                        value="80-120",
                        clearable=False,
                        ),
                ],style=dict(width='33%')),
            
             html.Div(children=[
                    html.Label("Seleccione el nivel de azúcar en la sangre en ayunas:",
                               htmlFor = "dropdownAzu"),
                    dcc.Dropdown(
                        id="dropdownAzu",
                        options=['Es menor a 120 mg/dl','Es mayor a 120 mg/dl'],
                        value='Es menor a 120 mg/dl',
                        clearable=False,
                        ),
                ],style=dict(width='33%')),
             ],style=dict(display='flex')),
        
        html.H4("Distribución de probabilidad para diagnóstico del paciente según edad, sexo y angina (seleccionados en la Sección 1), niveles de colesterol, presión arterial y azúcar en ayunas:"),
        
        dcc.Graph(id='graph2'),
        
    ])
])
                 
             
@app.callback(
    [Output('graph', 'figure'),
     Output('graph2', 'figure')],
    [Input('dropdownExamen', 'value'),
     Input('dropdownEdad', 'value'),
     Input('dropdownSexo', 'value'),
     Input('dropdownAngina', 'value'),
     Input('dropdownCol', 'value'),
     Input('dropdownPre', 'value'),
     Input('dropdownAzu', 'value')])

def update_output_div(selected_Examen, selected_Age, selected_Sex, selected_Angina, selected_Col, selected_Pre, selected_Azu):
  
    sexo = 0
    angina = 0
    col = 'saludable'
    pre = 'normal'
    azucar = 0
  
    #Sexo  
    if selected_Sex == "Fememino":
        sexo = 0
    elif selected_Sex == "Masculino":
        sexo = 1
        
    #Angina
    if selected_Angina == "No tiene angina inducida por ejercicio":
        angina = 0
    elif selected_Angina == "Tiene angina inducida por ejercicio":
        angina = 1
        
    #Examen
    
    if selected_Examen == "Estado del corazón según prueba Thallium":
        posterior_p = infer.query(["thal"], evidence={"age": selected_Age, "sex": sexo, 'exang': angina})
        estados = (["Normal", 'Defecto fijo', 'Defecto reversible'])
    elif selected_Examen == "Tipo de dolor en el pecho":
        posterior_p = infer.query(["cp"], evidence={"age": selected_Age, "sex": sexo, 'exang': angina})
        estados = (["Angina típica", 'Angina atípica', 'Dolor no-anginal', 'Asintomático'])
    elif selected_Examen == "Resultados de electrocardiograma en reposo":
        posterior_p = infer.query(["restecg"], evidence={"age": selected_Age, "sex": sexo, 'exang': angina})
        estados = (["Normal", 'Anormalidad de onda ST-T', 'Hipertropía ventricular izquierda probable o definitiva'])
    elif selected_Examen == "Máxima frecuencia cardiaca":
        posterior_p = infer.query(["thalach"], evidence={"age": selected_Age, "sex": sexo, 'exang': angina})
        estados = (["Excelente", 'Inadecuada'])
    elif selected_Examen == "Depresión del ST inducida por el ejercicio en relación con el descanso":
        posterior_p = infer.query(["oldpeak"], evidence={"age": selected_Age, "sex": sexo, 'exang': angina})
        estados = (["Baja", 'Normal', 'Terrible'])
    elif selected_Examen == "Pendiente del segmento ST":
        posterior_p = infer.query(["slope"], evidence={"age": selected_Age, "sex": sexo, 'exang': angina})
        estados = (["Ascenso", 'Plano', 'Descenso'])
    elif selected_Examen == "Número de vasos principales coloreados por fluoroscopia":
        posterior_p = infer.query(["ca"], evidence={"age": selected_Age, "sex": sexo, 'exang': angina})
        estados = ([0, 1, 2, 3])
    
    dff = pd.DataFrame(posterior_p.values)
    dff.columns = (["Probabilidad"])
    dff['Estados'] = estados
    
    fig = px.bar(dff, x = "Estados", y = "Probabilidad",
                     labels={
                     "Estados": "Resultado",
                     }
                    )
    
    #Colesterol
    if selected_Col == "< 200":
        col = 'saludable'
    elif selected_Col == "200-239":
        col = 'riesgoso'
    elif selected_Col == "240 >=":
        col = 'peligroso'
        
    #Presión
    if selected_Pre == '80-120':
        pre = 'normal'
    elif selected_Pre == '120-129':
        pre = 'elevada'
    elif selected_Pre == '130-139':
        pre = 'hiptertensión nivel 1'
    elif selected_Pre == '140-180':
        pre = 'hiptertensión nivel 2'
    elif selected_Pre == '180 >=':
        pre = 'crisis hipertensión'
    
    #Azucar
    if selected_Azu == "Es mayor a 120 mg/dl":
        azucar = 0
    elif selected_Azu == "Es menor a 120 mg/dl":
        azucar = 1
        
    posterior_num = infer.query(["num"], evidence={"age": selected_Age, "sex": sexo, 'exang': angina, 'chol': col, 'trestbps': pre, 'fbs': azucar})
    dfff = pd.DataFrame(posterior_num.values)
    dfff.columns = (["Probabilidad"])
    dfff['Diagnóstico'] = ['Saludable', 'Etapa 1', 'Etapa 2', 'Etapa 3', 'Etapa 4']
    
    fig2 = px.bar(dfff, x = "Diagnóstico", y = "Probabilidad")
    
    return fig, fig2

if __name__ == '__main__':
    app.run_server(debug=True)



