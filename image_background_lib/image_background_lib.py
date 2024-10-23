import boto3
import json
import base64
from io import BytesIO
from random import randint

# Get a BytesIO object from file bytes
def get_bytesio_from_bytes(image_bytes):
    image_io = BytesIO(image_bytes)
    return image_io


# Get a base64-encoded string from file bytes
def get_base64_from_bytes(image_bytes):
    resized_io = get_bytesio_from_bytes(image_bytes)
    img_str = base64.b64encode(resized_io.getvalue()).decode("utf-8")
    return img_str


# Load the bytes from a file on disk
def get_bytes_from_file(file_path):
    with open(file_path, "rb") as image_file:
        file_bytes = image_file.read()
    return file_bytes


# Get the stringified request body for the InvokeModel API call
def get_titan_image_background_replacement_request_body(prompt, image_bytes, mask_prompt, negative_prompt=None, outpainting_mode="DEFAULT", number_of_images=1):
    
    input_image_base64 = get_base64_from_bytes(image_bytes)

    body = {  # Create the JSON payload to pass to the InvokeModel API
        "taskType": "OUTPAINTING",
        "outPaintingParams": {
            "image": input_image_base64,
            "text": prompt,  # Description of the background to generate
            "maskPrompt": mask_prompt,  # The element(s) to keep
            "outPaintingMode": outpainting_mode,  # "DEFAULT" softens the mask. "PRECISE" keeps it sharp.
        },
        "imageGenerationConfig": {
            "numberOfImages": number_of_images,  # Number of variations to generate (passed from the frontend)
            "quality": "premium",  # Allowed values are "standard" and "premium"
            "height": 512,
            "width": 512,
            "cfgScale": 8.0,
            "seed": randint(0, 100000),  # Use a random seed
        },
    }
    
    if negative_prompt:
        body['outPaintingParams']['negativeText'] = negative_prompt
    
    return json.dumps(body)


# Get a list of BytesIO objects from the Titan Image Generator response
def get_titan_response_images(response):
    response = json.loads(response.get('body').read())
    
    images = response.get('images')
    
    # Return a list of BytesIO objects for all images
    image_list = []
    for image_data in images:
        decoded_image = base64.b64decode(image_data)
        image_list.append(BytesIO(decoded_image))
    
    return image_list


# Generate images using Amazon Titan Image Generator
def get_image_from_model(prompt_content, image_bytes, model_id, mask_prompt=None, negative_prompt=None, outpainting_mode="DEFAULT", number_of_images=1):
    session = boto3.Session()

    bedrock = session.client(service_name='bedrock-runtime')  # Creates a Bedrock client
    
    body = get_titan_image_background_replacement_request_body(
        prompt_content, 
        image_bytes, 
        mask_prompt=mask_prompt, 
        negative_prompt=negative_prompt, 
        outpainting_mode=outpainting_mode,
        number_of_images=number_of_images  # Pass the number of images
    )
    
    # Use the model ID that was passed from the frontend
    response = bedrock.invoke_model(body=body, modelId=model_id, contentType="application/json", accept="application/json")
    
    output_images = get_titan_response_images(response)
    
    return output_images
