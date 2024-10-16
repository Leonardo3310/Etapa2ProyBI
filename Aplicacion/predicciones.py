import sklearn as sk
import joblib
import pandas as pd
from io import BytesIO
import os
from sklearn.model_selection import train_test_split
from Dependencies import preprocessing_text, Transformer_Representacion_Seleccion 
from sklearn.metrics import classification_report

#Cargar el modelo
modelo = joblib.load('pipelon.joblib')


#Funcion para clasificar opiniones (End-point #1)
def clasificacion(opiniones):

    tamano = len(opiniones)
    predicciones = []

    for i in range(tamano):

        opinion = opiniones[i]
        opinion_df = pd.DataFrame({'Textos_espanol': [opinion]})
        clase_predicha  = int(modelo.predict(opinion_df)[0])
        probabilidades = modelo.predict_proba(opinion_df)

        prob_ods3 = str(round(float(probabilidades[0][0])*100,2))
        prob_ods4 = str(round(float(probabilidades[0][1])*100,2))
        prob_ods5 = str(round(float(probabilidades[0][2])*100,2))

        prediccion = {
            "opinion": i+1,
            "clase_predicha": clase_predicha,
            "probabilidades": {
                "ODS 3": prob_ods3+'%',
                "ODS 4": prob_ods4+'%',
                "ODS 5": prob_ods5+'%'
            }
        }
        predicciones.append(prediccion)
    return predicciones


#Funcion para unir los datos de ambos archivos para el reentrenamiento del modelo
def unir_datos(file: BytesIO):
    archivo1 = pd.read_excel('ODScat_345.xlsx')
    archivo2 = pd.read_excel(file)
    data = pd.concat([archivo1, archivo2], ignore_index=True)
    
    return data

df = pd.read_excel('ODScat_345.xlsx')

#Funcion para reentrenar el modelo (End-point #2)
def reentrenar_modelo(model, data):
    data_t, data_v = train_test_split(data, test_size=0.2, random_state=0)

    y_train = data_t['sdg']
    x_train = data_t.drop(columns='sdg')

    x_val = data_v.drop(columns='sdg')
    y_val = data_v['sdg']

    model.fit(x_train, y_train)
    y_pred = model.predict(x_val)

    metrics = classification_report(y_val, y_pred, output_dict=True)

    ods_3 = {
        'precision': round(metrics['3']['precision'],2),
        'recall': round(metrics['3']['recall'],2),
        'f1-score': round(metrics['3']['f1-score'],2)
    }
    ods_4 = {
        'precision': round(metrics['4']['precision'],2),
        'recall': round(metrics['4']['recall'],2),
        'f1-score': round(metrics['4']['f1-score'],2)
    }
    ods_5 = {
        'precision': round(metrics['5']['precision'],2),
        'recall': round(metrics['5']['recall'],2),
        'f1-score': round(metrics['5']['f1-score'],2)
    }

    joblib.dump(model, 'pipelon.joblib')

    metrics_dicc = {
        1: ods_3,
        2: ods_4,
        3: ods_5
    }

    return metrics_dicc
