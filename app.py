from flask import Flask, render_template_string, render_template, request, redirect, url_for, send_from_directory
from flask_cors import CORS
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import os
import time
import threading 

app = Flask(__name__)
CORS(app)

MODEL_PATH = 'model.h5'
model = load_model(MODEL_PATH)

class_names = ['Apple Segar', 'Pisang Segar', 'Timun Segar', 'Okra Segar', 'Jeruk Segar', 'Kentang Segar',
               'Bukan Buah', 'Apple Busuk', 'Pisang Busuk', 'Timun Busuk', 'Okra Busuk', 'Jeruk Busuk', 'Kentang Busuk']

UPLOAD_FOLDER = 'temp'
EXPIRE_TIME = 300

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def prediksi(model, img_path):
    img = image.load_img(img_path, target_size=(259, 259))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, 0)

    predictions = model.predict(img_array)
    predicted_class = np.argmax(predictions[0])

    return class_names[predicted_class]

@app.route('/temp/<filename>')
def temp_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/hasil_prediksi/<predict>/<path:img_path>')
def hasil_prediksi(predict, img_path):
    hasil = predict
    kata = hasil.split()
    if hasil != 'Bukan Buah':
        if kata[1] == 'Busuk':
            pesan = f'{kata[0]} yang anda miliki sudah {kata[1]}'
        elif kata[1] == 'Segar':
            pesan = f'{kata[0]} yang anda miliki masih {kata[1]}'
    else:
        pesan = 'Gambar yang anda masukan bukan buah'
    return f"""
    <html>
        <body>
            <h1>{pesan}</h1>
            <img src="/{img_path}" alt="gambar">
        </body>
    </html>
    """
    

@app.route('/input', methods=['POST', 'GET'])
def input_route():
    if request.method == 'POST':
        file = request.files['gambar']
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        hasil = prediksi(model, file_path)

        return redirect(url_for('hasil_prediksi', predict=hasil, img_path=f'temp/{file.filename}'))
    return render_template('index.html')

def hapus_file_lama():
    while True:
        current_time = time.time()
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > EXPIRE_TIME:
                    try:
                        os.remove(file_path)
                        print(f"File {filename} dihapus karena sudah melebihi TTL.")
                    except Exception as e:
                        print(f"Error saat menghapus file {filename}: {e}")
        time.sleep(60)

thread = threading.Thread(target=hapus_file_lama, daemon=True)
thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5100)