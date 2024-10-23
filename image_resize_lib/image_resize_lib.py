from io import BytesIO
from io import BytesIO
from PIL import Image, ImageEnhance, ImageFilter

# Function to resize the image using PIL while maintaining the aspect ratio
def resize_image_by_height(image_bytes, new_height):
    image = Image.open(BytesIO(image_bytes))
    original_width, original_height = image.size
    aspect_ratio = original_width / original_height
    new_width = int(new_height * aspect_ratio)
    
    resized_image = image.resize((new_width, new_height))
    resized_image_io = BytesIO()
    resized_image.save(resized_image_io, format="JPEG")
    resized_image_io.seek(0)
    
    return resized_image_io, new_width


# Function to apply high resolution using Pillow
def apply_high_resolution(resized_image_io):
    # Open the resized image from BytesIO
    resized_image_io.seek(0)
    image = Image.open(resized_image_io)
    
    # Slightly enhance the sharpness
    enhancer = ImageEnhance.Sharpness(image)
    enhanced_image = enhancer.enhance(2.0)  # Increase sharpness, value > 1 increases sharpness

    # Apply a slight resize to mimic higher resolution
    width, height = enhanced_image.size
    new_size = (int(width * 1.5), int(height * 1.5))  # Upscale by 1.5x
    upscaled_image = enhanced_image.resize(new_size, Image.LANCZOS)  # Use LANCZOS filter for high-quality resizing

    # Save the upscaled and enhanced image to a BytesIO object
    upscaled_image_io = BytesIO()
    upscaled_image.save(upscaled_image_io, format="JPEG")
    upscaled_image_io.seek(0)

    return upscaled_image_io


