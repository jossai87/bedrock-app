import boto3
import json
import base64
from io import BytesIO
from random import randint

# Function to structure the request body based on the model type
def get_image_generation_request_body(model_id, prompt, negative_prompt=None):
    rand_seed = randint(0, 4294967295)

    if model_id == 'stability.stable-diffusion-xl-v1':
        # Handle Stable Diffusion XL v1 model
        body = {
            "text_prompts": [
                {"text": prompt}
            ],
            "cfg_scale": 10,
            "seed": rand_seed,
            "steps": 50
        }
    elif model_id in ['stability.sd3-large-v1:0', 'stability.stable-image-core-v1:0', 'stability.stable-image-ultra-v1:0']:
        # Handle other Stable Diffusion models
        body = {
            "prompt": prompt
        }
    else:
        # Handle Amazon Titan models
        body = {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": prompt,
            },
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "quality": "premium",
                "height": 768,
                "width": 1280,
                "cfgScale": 7.5,
                "seed": rand_seed,
            }
        }
        if negative_prompt:
            body['textToImageParams']['negativeText'] = negative_prompt

    return json.dumps(body)


# Function to handle the response and return the image as BytesIO
def get_response_image(response):
    response = json.loads(response.get('body').read())
    images = response.get('images')
    image_data = base64.b64decode(images[0])
    return BytesIO(image_data)


# Function to generate an image from the selected model
def get_image_from_model(prompt_content, negative_prompt=None, model_id="amazon.titan-image-generator-v1"):
    # Reinitialize the session and Bedrock client to ensure it's refreshed before every call
    session = boto3.Session()
    bedrock = session.client(service_name='bedrock-runtime')  # Create Bedrock client
    
    # Get the request body based on model and prompt
    body = get_image_generation_request_body(model_id, prompt_content, negative_prompt)
    
    # Ensure fresh state by clearing any potential previous response before making the next call
    response = bedrock.invoke_model(
        body=body,
        modelId=model_id,  # Model ID passed dynamically
        contentType="application/json",
        accept="application/json"
    )
    
    # Process the response to get the image
    output = get_response_image(response)
    return output
