from flask import Flask, render_template,request, jsonify, send_file
import json
import warnings


from utils import server



warnings.filterwarnings("ignore")

server_client = server()

app = Flask(__name__)
# run_with_ngrok(app)

@app.route('/')
def index():
    return render_template('Main.html')

@app.route('/chat', methods=['POST'])
def chat():
    chat_history = request.json['chat_history']
    patient_details = request.json['patient_details']
    __p = request.json['__p']

    print(chat_history)
    print(patient_details)
    print(__p)

    if __p == 'OngoingChat':
        data = server_client.start_questioning(data = (chat_history, patient_details))
        

    return {"status": "success", "data": data}


if __name__ == '__main__':
    app.run(debug = True, port = 5000)


