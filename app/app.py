import streamlit as st
import sys
import os
from PIL import Image
from io import BytesIO
# Add the parent directory (project-folder/) to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import image_background_lib.image_background_lib as bg_glib
import image_understanding_lib.image_understanding_lib as ui_glib
import image_extension_lib.image_extension_lib as img_extension_glib
import subtitle_translation_lib.subtitle_translation_lib as sub_tran_glib
import image_generation_lib.image_generation_lib as img_gen_glib
import object_replacement_removal_lib.object_replacement_removal_lib as rplce_rmv_glib


# Load custom CSS
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.set_page_config(layout="wide", page_title="Image App")

# Initialize the session state for resized images and super-resolution images
if "resized_image_io" not in st.session_state:
    st.session_state["resized_image_io"] = None
if "high_res_image_io" not in st.session_state:
    st.session_state["high_res_image_io"] = None

load_css()

# Create tabs: Multimodal & Images, Video Upload/Playback, Image to Video Demo, and Subtitle/Translation
tab1, tab2, tab3 = st.tabs(["Multimodal & Images", "Video Subtitle/Translation", "Image to Video Demo"])

# Tab 1: Multimodal & Images (containing subtabs)
with tab1:
    st.title("Multimodal & Images")
    subtab1, subtab2, subtab3, subtab4, subtab5 = st.tabs(["Image Understanding", "Background Change", "Image Extension", "Image Removal/Replacement", "Image Generation"])

    # Subtab: Image Understanding
    with subtab1:
        st.title("Image Understanding")

        col1, col2, col3 = st.columns(3)

        prompt_options_dict = {
            "Product Description": "Write a compelling and detailed product description for this L'Oreal cosmetic product. Highlight its key features, benefits, and ingredients. Focus on conveying a sense of luxury, innovation, and the brand's commitment to beauty and skincare. Use a tone that is informative yet engaging, and emphasize how this product enhances the user’s beauty routine. Keep the description concise and tailored for an audience seeking high-quality skincare or makeup solutions.",
            "Market Content": "Create a captivating marketing message for this L'Oreal cosmetic product that showcases the brand's innovation and commitment to beauty. The message should highlight the product's unique features, its benefits for the consumer, and how it reflects L'Oreal's values of luxury, science-backed beauty, and inclusivity. Use persuasive language that appeals to a broad audience, encouraging them to feel confident and empowered by using the product. Include a call-to-action that inspires engagement and aligns with L'Oreal's brand identity.",
            "Blog Creation": "Write an informative and engaging blog post about this L'Oreal cosmetic product. Begin with a brief introduction to the L'Oreal brand, emphasizing its leadership in beauty and innovation. Then, provide a detailed review of the product, highlighting its key features, benefits, and how it fits into a modern beauty routine. Include insights on the ingredients, results users can expect, and any tips on how to best use the product. Conclude with a call-to-action that encourages readers to try the product and experience the quality that L'Oreal is known for. The tone should be friendly and relatable while maintaining a sense of expertise in beauty care.",
            "Image caption": "Please provide a brief caption for this image.",
            "Detailed description": "Please provide a thoroughly detailed description of this image.",
            "Image classification": "Please categorize this image into one of the following categories: People, Food, Other. Only return the category name.",
            "Object recognition": "Please create a comma-separated list of the items found in this image. Only return the list of items.",
            "Writing a story": "Please write a fictional short story based on this image.",
            "Transcribing text": "Please transcribe any text found in this image.",
            "Translating text": "Please translate the text in this image to French.",
            "Other": "",
        }

        image_options_dict = {
            "Cosmetic": "loreal_images/aspect_resized_revitalift.jpg",
            "Food": "images/food.jpg",
            "People": "images/people.jpg",
            "Person and cat": "images/person_and_cat.jpg",
            "Room": "images/room.jpg",
            "Text in image": "images/text2.png",
            "Toy": "images/toy_car.jpg",
            "Other": "images/house.jpg",
        }

        with col1:
            st.subheader("Select an Image")
            image_selection = st.radio("Image example:", list(image_options_dict.keys()), key="image_selection_radio")
            uploaded_file = st.file_uploader("Select an image", type=['png', 'jpg'], key="ui_file_uploader_image_understanding") if image_selection == 'Other' else None

            if uploaded_file and image_selection == 'Other':
                uploaded_image_preview = ui_glib.get_bytesio_from_bytes(uploaded_file.getvalue())
                st.image(uploaded_image_preview)
            else:
                st.image(image_options_dict[image_selection])

        with col2:
            st.subheader("Prompt")
            prompt_selection = st.radio("Prompt example:", list(prompt_options_dict.keys()), key="prompt_selection_radio")
            prompt_text = st.text_area("Prompt", value=prompt_options_dict[prompt_selection], height=100)

            go_button = st.button("Go", type="primary", key="go_button_image_understanding")

        with col3:
            st.subheader("Result")
            if go_button:
                with st.spinner("Processing..."):
                    image_bytes = uploaded_file.getvalue() if uploaded_file else ui_glib.get_bytes_from_file(image_options_dict[image_selection])
                    response = ui_glib.get_response_from_model(prompt_content=prompt_text, image_bytes=image_bytes)
                st.write(response)

    # Subtab: Background Change
    with subtab2:
        st.title("Background Change")

        col1, col2, col3 = st.columns(3)

        with col1:
            uploaded_file = st.file_uploader("Select an image", type=['png', 'jpg'], key="bg_file_uploader_background_change")
            if uploaded_file:
                uploaded_image_preview = bg_glib.get_bytesio_from_bytes(uploaded_file.getvalue())
                st.image(uploaded_image_preview)
            else:
                st.image("images/example.jpg")

        with col2:
            st.subheader("Image parameters")
            mask_prompt = st.text_input("Object to keep:", value="Clear L'Oreal bottle with white circular top")
            model_options = ["Default Titan Model (v2)", "Default Titan Model (v1)"]
            selected_model = st.selectbox("Select Model", model_options, key="bg_model_selection")
            model_id_mapping = {
                "Default Titan Model (v2)": "amazon.titan-image-generator-v2:0",
                "Default Titan Model (v1)": "amazon.titan-image-generator-v1"
            }
            prompt_text = st.text_area("Description including the object to keep and background to add:", value="Cosmetic bottle on a marble shelf, with bathroom items in the back blurred out", height=100)
            negative_prompt = st.text_input("What should not be in the background:", value="low resolution, fuzzy objects")
            outpainting_mode = st.radio("Outpainting mode:", ["PRECISE", "DEFAULT"], horizontal=True, key="outpainting_mode_radio")
            number_of_images = st.selectbox("Number of Images to Generate:", [1, 2, 3], key="num_images_selection")
            generate_button = st.button("Generate", type="primary", key="generate_button_background_change")

        with col3:
            st.subheader("Result")
            if generate_button:
                with st.spinner("Drawing..."):
                    image_bytes = uploaded_file.getvalue() if uploaded_file else bg_glib.get_bytes_from_file("images/example.jpg")
                    selected_model_id = model_id_mapping[selected_model]
                    generated_images = bg_glib.get_image_from_model(
                        prompt_content=prompt_text, 
                        image_bytes=image_bytes,
                        mask_prompt=mask_prompt,
                        negative_prompt=negative_prompt,
                        outpainting_mode=outpainting_mode,
                        number_of_images=number_of_images,
                        model_id=selected_model_id
                    )
                for img in generated_images:
                    st.image(img)



    # Subtab: Image Extension
    with subtab3:
        st.title("Image Extension")

        col1, col2, col3 = st.columns(3)

        horizontal_alignment_dict = {
            "Left": 0.0,
            "Center": 0.5,
            "Right": 1.0,
        }

        vertical_alignment_dict = {
            "Top": 0.0,
            "Middle": 0.5,
            "Bottom": 1.0,
        }

        horizontal_alignment_options = list(horizontal_alignment_dict)
        vertical_alignment_options = list(vertical_alignment_dict)

        with col1:
            st.subheader("Initial image")

            uploaded_file = st.file_uploader("Select an image (smaller than 1024x1024)", type=['png', 'jpg'])

            if uploaded_file:
                uploaded_image_preview = img_extension_glib.get_bytesio_from_bytes(uploaded_file.getvalue())
                st.image(uploaded_image_preview)
            else:
                st.image("images/example.jpg")

        with col2:
            st.subheader("Extension parameters")
            prompt_text = st.text_area("What should be seen in the extended image:", height=100, value="Flower pot", help="The prompt text")
            negative_prompt = st.text_input("What should not be in the extended area:", help="The negative prompt")

            horizontal_alignment_selection = st.select_slider("Original image horizontal placement:", options=horizontal_alignment_options, value="Center")
            vertical_alignment_selection = st.select_slider("Original image vertical placement:", options=vertical_alignment_options, value="Middle")

            generate_button = st.button("Generate", type="primary", key="generate_button_image_extension")

        with col3:
            st.subheader("Result")

            if generate_button:
                with st.spinner("Drawing..."):
                    if uploaded_file:
                        image_bytes = uploaded_file.getvalue()
                    else:
                        image_bytes = img_extension_glib.get_bytes_from_file("images/example.jpg")

                    # Assuming this returns bytes or a BytesIO object
                    generated_image = img_extension_glib.get_image_from_model(
                        prompt_content=prompt_text,
                        image_bytes=image_bytes,
                        negative_prompt=negative_prompt,
                        vertical_alignment=vertical_alignment_dict[vertical_alignment_selection],
                        horizontal_alignment=horizontal_alignment_dict[horizontal_alignment_selection],
                    )

                # Convert the generated image to a PIL Image
                try:
                    if isinstance(generated_image, BytesIO):
                        img = Image.open(generated_image)  # Generated image is a BytesIO object
                    else:
                        img = Image.open(BytesIO(generated_image))  # If it’s bytes, wrap in BytesIO for PIL
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    img = None

                if img:
                    st.image(img)

                    # Prepare a buffer for the download button
                    buffered = BytesIO()
                    img.save(buffered, format="JPEG")
                    buffered.seek(0)

                    # Add a download button for the image
                    st.download_button(
                        label="Download Extended Image",
                        data=buffered,
                        file_name="extended_image.jpg",
                        mime="image/jpeg"
                    )

with subtab4:

    st.title("Image Replacement/Removal")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Image parameters")
        
        # Image uploader for user to upload a file
        uploaded_file = st.file_uploader("Select an image", type=['png', 'jpg'])

        # Placeholder for mask_prompt to automatically load identified items
        mask_prompt = ""

        # Display the uploaded image or the default example image
        if uploaded_file:
            uploaded_image_preview = rplce_rmv_glib.get_bytesio_from_bytes(uploaded_file.getvalue())
            st.image(uploaded_image_preview, caption="Uploaded Image")
            
            # Process the image and infer identified objects using ui_glib
            with st.spinner("Processing..."):
                # Get image bytes from the uploaded file
                image_bytes = uploaded_file.getvalue()

                # Run inference using ui_glib to get the objects identified in the image
                identified_items = ui_glib.get_response_from_model(
                    prompt_content="Describe 1 object on the image. Be as detailed as possible, but stay within 3 to 5 words for the description. For example, a Grey, wooden ball. - Only provide the description.", 
                    image_bytes=image_bytes
                )

                # Fix the format of the response if it has extra spaces between characters
                if isinstance(identified_items, str):
                    # In case the output is a single string with space between characters, we split and join correctly
                    mask_prompt = " ".join(identified_items.split())
                elif isinstance(identified_items, list):
                    # If it's a list, we assume it's already a list of words and join with a single space
                    mask_prompt = " ".join(identified_items)
                else:
                    mask_prompt = ""

        else:
            st.image("loreal_images/aspect_resized_revitalift.jpg", caption="Example Image")
            st.warning("Please upload an image to generate a result.")
        
    with col2:
        # Automatically populate the "Object to remove/replace" field with identified items
        mask_prompt = st.text_input("Object to remove/replace", value=mask_prompt.strip(), help="The mask text")
        
        prompt_text = st.text_area("Object to add (leave blank to remove)", value="", height=100, help="The prompt text")
        
        generate_button = st.button("Generate", type="primary", key="generate_button_image_removal")
        
    with col3:
        st.subheader("Result")
        
        # Ensure image is uploaded before allowing generation
        if generate_button:
            if not uploaded_file:
                st.error("Please upload an image to generate the result.")
            else:
                with st.spinner("Drawing..."):
                    image_bytes = uploaded_file.getvalue()
                    
                    # Call the backend to generate an image with the selected model and prompt
                    generated_image = rplce_rmv_glib.get_image_from_model(
                        prompt_content=prompt_text, 
                        image_bytes=image_bytes, 
                        mask_prompt=mask_prompt.strip(),  # Ensure no extra spaces are present
                    )
                
                st.image(generated_image, caption="Generated Image")


# Subtab: Image Generation
with subtab5:
    st.title("Image Generation")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Image parameters")
        prompt_text = st.text_area("What you want to see in the image:", height=100, value="L'Oreal store that appears busy with alot of people shopping.")
        negative_prompt = st.text_input("What should not be in the image:")

        # Update the model selection options
        model_options = [ 
            "Amazon Titan V1", 
            "Amazon Titan V2", 
            "Stable Diffusion 3 Large", 
            "Stable Image Ultra", 
            "Stable Image Core",
            "Custom Amazon Titan Model V2",
            "Stable Diffusion"
        ]
        
        # Mapping the user-friendly model names to actual Bedrock model IDs
        model_id_mapping = {
            "Amazon Titan V1": "amazon.titan-image-generator-v1",
            "Amazon Titan V2": "amazon.titan-image-generator-v2:0",
            "Stable Diffusion 3 Large": "stability.sd3-large-v1:0",
            "Stable Image Ultra": "stability.stable-image-ultra-v1:0",
            "Stable Image Core": "stability.stable-image-core-v1:0",
            "Custom Amazon Titan Model V2": "xxx", # Replace with provisioned thoughput ARN for the fine tuned bedrock model
            "Stable Diffusion": "stability.stable-diffusion-xl-v1",
        }

        # Select box for the model
        selected_model = st.selectbox("Select model", model_options, key="image_gen_model_selection")

        generate_button = st.button("Generate", type="primary", key="gen_generate_button_image_generation")

    with col2:
        st.subheader("Result")
        if generate_button:
            with st.spinner("Drawing..."):
                model_id = model_id_mapping[selected_model]  # Get the actual model ID from the mapping
                generated_image = img_gen_glib.get_image_from_model(
                    prompt_content=prompt_text, 
                    negative_prompt=negative_prompt, 
                    model_id=model_id
                )
            st.image(generated_image)



# Tab 2: Video Upload/Playback (Subtitle/Translation)
with tab2:
    st.title("Video Upload and Playback")

    # S3 Client initialization
    bucket_name = "demo-portal-videos-jossai"

    col1, col2 = st.columns(2)

    # Video upload to S3
    with col1:
        st.subheader("Upload and Preview Video")
        uploaded_video = st.file_uploader("Select a video", type=['mp4', 'mov', 'avi'], key="video_uploader")

        if uploaded_video:
            st.video(uploaded_video)
            video_filename = uploaded_video.name
            content_type = "video/mp4"
            upload_status = sub_tran_glib.upload_file_to_s3(uploaded_video.getvalue(), bucket_name, video_filename, content_type)
            st.success(upload_status)
            st.session_state['video_filename'] = video_filename

    # Video rendering from S3
    with col2:
        st.subheader("Play and Process Video from S3")
        video_filename_input = st.text_input("Enter S3 video filename to play:", value=st.session_state.get('video_filename', ""))
        language_mapping = {"Spanish": "es", "French": "fr"}
        selected_language = st.selectbox("Select Language", list(language_mapping.keys()))
        video_processed = st.session_state.get("video_processed", False)
        process_video_button = st.button("Process Video with Subtitles")
        play_button = st.button("Play Video with Subtitles", key="play_button")

        if process_video_button and video_filename_input:
            with st.spinner("Processing video..."):
                target_language_code = language_mapping[selected_language]
                result = sub_tran_glib.process_video_with_subtitles(
                    region="us-west-2",
                    inbucket=bucket_name,
                    infile=video_filename_input,
                    outbucket=bucket_name,
                    outfilename=video_filename_input.split('.')[0],
                    outfiletype="mp4",
                    target_language=target_language_code
                )
                st.success(result)
                st.session_state["video_processed"] = True

        if play_button and video_filename_input:
            subtitle_video_filename = f"{video_filename_input.split('.')[0]}_subtitle.mp4"
            video_url = sub_tran_glib.get_video_url_from_s3(bucket_name, subtitle_video_filename)
            st.video(video_url)
            st.success(f"Playing video with subtitles from S3: {subtitle_video_filename}")


# Tab 3: Image to Video Demo
with tab3:
    st.title("Image to Video Demo")

    slide_tabs = st.tabs(["Revitalift", "Cream", "Shampoo"])

    with slide_tabs[0]:
        st.subheader("Revitalift Slide")
        col1, col2 = st.columns(2)
        with col1:
            st.image("loreal_images/aspect_resized_revitalift.jpg", caption="Revitalift Image", use_column_width=True)
        with col2:
            st.video("videos/revitalift.mp4")
            st.markdown("**Revitalift Video**")

    with slide_tabs[1]:
        st.subheader("Cream Slide")
        col3, col4 = st.columns(2)
        with col3:
            st.image("loreal_images/cream_resized.jpg", caption="Cream Image", use_column_width=True)
        with col4:
            st.video("videos/cream.mp4")
            st.markdown("**Cream Video**")

    with slide_tabs[2]:
        st.subheader("Shampoo Slide")
        col5, col6 = st.columns(2)
        with col5:
            st.image("loreal_images/shampoo_resized.jpg", caption="Shampoo Image", use_column_width=True)
        with col6:
            st.video("videos/shampoo.mp4")
            st.markdown("**Shampoo Video**")

