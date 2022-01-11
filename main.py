import os
from PIL import Image
import requests
from flask import Flask, request, jsonify
from transformers import CLIPProcessor, CLIPModel, CLIPTokenizer
import redis

app = Flask(__name__)

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
cache = redis.Redis(host='redis', port=6379)

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)


#@torch.no_grad()
@app.route("/")
def hello_world():
    name = os.environ.get("NAME", "World")
    # count = get_hit_count()
    print("hello world")
    return 'Hello World! I have been seen {} times.\n' #.format(count)

#@torch.no_grad()
@app.route('/text')
def text():
    text = request.args.get('text')
    print(text)
    if text is None:
        return jsonify(code=403, message="bad request")
    inputs = processor(text=text, padding=True, return_tensors="pt")
    outputs = model.get_text_features(**inputs)
    #print(outputs)
    detached = outputs.detach().numpy().tolist()
    #print(detached)
    return jsonify(detached)

@app.route('/image')
def images():
    url = request.args.get('url')
    print(url)
    if url is None:
        return jsonify(code=403, message="bad request")
    image = Image.open(requests.get(url, stream=True).raw)
    inputs = processor(images=image, return_tensors="pt")
    outputs = model.get_image_features(**inputs)
    print(outputs)
    detached = outputs.detach().numpy().tolist()
    print(detached)
    return jsonify(detached)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
