from flask import Flask, request, jsonify
import faiss
import numpy as np
import json
from PIL import Image
from extract_features import mySigLipModel

app = Flask(__name__)

# Load the image index and URL mapping
index = faiss.read_index('index100k/siglip-image-index-0-100k.bin')
print("Total vectors in the index:", index.ntotal)

with open('index100k/siglip-image-index-0-100k.json') as f:
    image_urls = json.load(f)
print("Number of URLs loaded:", len(image_urls))

import torch
print(torch.__version__)
print(torch.cuda.is_available())

# Initialize the embedding extractor
extractor = mySigLipModel()

@app.route('/search_by_caption', methods=['POST'])
def search_by_caption():
    data = request.json
    caption = data['caption']
    k = data.get('k', 10)

    # Debug: Check embedding variation
    print("Caption received:", caption)

    caption_embedding = extractor.get_text_embedding(caption)
    print("Caption Embedding:", caption_embedding)

    query_vector = np.array([caption_embedding]).astype('float32').squeeze()
    if query_vector.ndim == 1:
        query_vector = query_vector.reshape(1, -1)

    # Check the shape of the query vector
    print("Query Vector Shape:", query_vector.shape)

    distances, indices = index.search(query_vector, k)
    print("Distances:", distances)
    print("Indices:", indices)

    result_images = [image_urls[idx] for idx in indices[0]]
    print("Resulting Images:", result_images)

    return jsonify({
        'distances': distances.tolist(),
        'images': result_images
    })


if __name__ == '__main__':
    app.run(debug=True)
