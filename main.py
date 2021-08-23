from flask import Flask, render_template, request, redirect, url_for, Response
import os
from os.path import join, dirname, realpath
import pandas as pd
import json

app = Flask(__name__)

app.config["DEBUG"] = True

UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('index.html')

@app.route("/", methods=['POST'])
def uploadFiles():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        uploaded_file.save(file_path)
        return Response(parseCSV(file_path), 
                mimetype='application/json',
                headers={'Content-Disposition':'attachment;filename=Decathlon.json'})
    else:
        return redirect(url_for('index'))

def parseCSV(filePath):
    col_names = ['full_name','m_100','long_jump', 'shot_put', 'high_jump', 'm_400', 'm_110_hurdles', 'discus_throw', 'pole_vault', 'javelin_throw', 'm_1500']
    csvData = pd.read_csv(filePath,names=col_names, header=None, delimiter=';')

    return calcPoints(csvData)

def calcPoints(data):
    for i,row in data.iterrows():
        data.loc[i, "totalPoints"] = int(score(row['m_100'], 'm_100') +\
                                        score(row['long_jump'], 'long_jump') +\
                                        score(row['shot_put'], 'shot_put') +\
                                        score(row['high_jump'], 'high_jump') +\
                                        score(row['m_400'], 'm_400') +\
                                        score(row['m_110_hurdles'], 'm_110_hurdles') +\
                                        score(row['discus_throw'], 'discus_throw') +\
                                        score(row['pole_vault'], 'pole_vault') +\
                                        score(row['javelin_throw'], 'javelin_throw') +\
                                        score(row['m_1500'], 'm_1500'))
    data.sort_values(by=['totalPoints'], ascending=True, inplace=True)
    data.reset_index(drop=True,inplace=True)
    rankResults(data)
    
    result = data.to_json(orient="records")
    parsed = json.loads(result)

    result = json.dumps(parsed, indent=4)  
    print(result)
    return result

def score(points, field_name):
    if field_name == "m_100":
        return trackEvent(points, 25.4347, 18, 1.81)
    if field_name == "long_jump":
        return fieldEvent(points*100, 0.14354, 220, 1.4)
    if field_name == "shot_put":
        return fieldEvent(points, 51.39, 1.5, 1.05)
    if field_name == "high_jump":
        return fieldEvent(points*100, 0.8465, 75, 1.42)
    if field_name == "m_400":
        return trackEvent(points, 1.53775, 82, 1.81)
    if field_name == "m_110_hurdles":
        return trackEvent(points, 5.74352, 28.5, 1.92)
    if field_name == "discus_throw":
        return fieldEvent(points, 12.91, 4, 1.1)
    if field_name == "pole_vault":
        return fieldEvent(points*100, 0.2797, 100, 1.35)
    if field_name == "javelin_throw":
        return fieldEvent(points, 10.14, 7, 1.08)
    if field_name == "m_1500":
        return trackEvent(float(points.split('.', 1)[0])*60 + float(points.split('.', 1)[0]), 0.03768, 480, 1.85 )

# faster time produces a higher score
def trackEvent(p,a,b,c):
    return int(a*pow(b-p,c))

# greater distance or height produces a higher score
def fieldEvent(p,a,b,c):
    return int(a*pow(p-b,c))

def rankResults(data):
    rank = data.shape[0]
    for i,row in data.iterrows():
        try:
            if data.loc[i, "totalPoints"] == data.loc[i + 1, "totalPoints"]:
                data.loc[i, "rank"] = str(int(rank - 1)) + " - " + str(int(rank))
            elif data.loc[i, "totalPoints"] == data.loc[i - 1, "totalPoints"]:
                data.loc[i, "rank"] = str(int(rank)) + " - " + str(int(rank + 1))
            else:
                data.loc[i, "rank"] = rank
            rank -=1
        except:
            data.loc[i, "rank"] = rank
            rank -=1

if (__name__ == "__main__"):
    app.run(port = 5000)
