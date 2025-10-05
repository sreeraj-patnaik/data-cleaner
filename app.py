from flask import Flask, render_template, request, send_file
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/clean', methods=['POST'])
def clean_csv():
    file = request.files['file']
    if not file:
        return "No file uploaded", 400

    # Save uploaded file
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Load CSV
    df = pd.read_csv(filepath)

    # --- Cleaning Steps ---
    # 1. Standardize column names
    df.columns = df.columns.str.strip().str.lower()

    # 2. Drop columns with >50% NaNs
    df = df.loc[:, df.isnull().mean() < 0.5]

    # 3. Fill numeric NaNs with column mean
    num_cols = df.select_dtypes(include=['float64', 'int64']).columns
    df[num_cols] = df[num_cols].fillna(df[num_cols].mean())

    # 4. Trim spaces in string columns
    str_cols = df.select_dtypes(include=['object']).columns
    df[str_cols] = df[str_cols].apply(lambda x: x.str.strip())

    # 5. Remove duplicate rows
    df.drop_duplicates(inplace=True)

    # 6. Reset index
    df.reset_index(drop=True, inplace=True)

    # Save cleaned CSV
    cleaned_filepath = os.path.join(UPLOAD_FOLDER, 'cleaned_' + file.filename)
    df.to_csv(cleaned_filepath, index=False)

    return send_file(cleaned_filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
