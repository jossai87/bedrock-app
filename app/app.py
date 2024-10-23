import streamlit as st
import sys
import os
from PIL import Image  # Import the Image module from PIL (Pillow)

# Add the parent directory (project-folder/) to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import image_background_lib.image_background_lib as bg_glib
import image_understanding_lib.image_understanding_lib as ui_glib
import image_resize_lib.image_resize_lib as resize_glib  # Assuming you create a module for resizing
import subtitle_translation_lib.subtitle_translation_lib as sub_tran_glib  # Assuming you create a module for resizing

# Initialize the session state for resized images and super-resolution images
if "resized_image_io" not in st.session_state:
    st.session_state["resized_image_io"] = None
if "high_res_image_io" not in st.session_state:
    st.session_state["high_res_image_io"] = None

st.set_page_config(layout="wide", page_title="Image App")

# Create five tabs: Background Change, Image Understanding, Image Resize, Video Upload/Playback, and Image to Video Demo
tab2, tab1, tab3, tab4, tab5 = st.tabs(["Image Understanding", "Background Change", "Image Resize", "Subtitle/Translation", "Image to Video Demo"])

# Tab 1: Background Change
with tab1:
    st.title("Image Background Change")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Assign a unique key to this file uploader
        uploaded_file = st.file_uploader("Select an image", type=['png', 'jpg'], key="bg_file_uploader")
        
        if uploaded_file:
            uploaded_image_preview = bg_glib.get_bytesio_from_bytes(uploaded_file.getvalue())
            st.image(uploaded_image_preview)
        else:
            st.image("images/example.jpg")

    with col2:
        st.subheader("Image parameters")
        
        mask_prompt = st.text_input("Object to keep:", value="cosmetic bottle with white pointy top", help="The mask text")

        # Add a dropdown for selecting the model
        model_options = ["Default Titan Model (v2)", "Custom Titan Model (v2)"]
        selected_model = st.selectbox("Select Model", model_options)

        # Map the model selection to the model ID
        model_id_mapping = {
            "Default Titan Model (v2)": "amazon.titan-image-generator-v2:0",
            "Custom Titan Model (v2)": "amazon.titan-image-generator-v1"
        }

        prompt_text = st.text_area("Description including the object to keep and background to add:", value="Cosmetic bottle on a shelf, with other cosmetic products in the background blurred out", height=100, help="The prompt text")
        
        negative_prompt = st.text_input("What should not be in the background:", value="low resolution, fuzzy, distorted objects", help="The negative prompt")

        # Place the model selection dropdown right above the Outpainting mode
        outpainting_mode = st.radio("Outpainting mode:", ["DEFAULT", "PRECISE"], horizontal=True)
        
        number_of_images = st.selectbox("Number of Images to Generate:", [1, 2, 3], help="Select the number of variations to generate")
        
        generate_button = st.button("Generate", type="primary")

    with col3:
        st.subheader("Result")

        if generate_button:
            if uploaded_file:
                image_bytes = uploaded_file.getvalue()
            else:
                image_bytes = bg_glib.get_bytes_from_file("images/example.jpg")
            
            with st.spinner("Drawing..."):
                # Pass the selected model ID based on the dropdown selection
                selected_model_id = model_id_mapping[selected_model]
                
                generated_images = bg_glib.get_image_from_model(
                    prompt_content=prompt_text, 
                    image_bytes=image_bytes,
                    mask_prompt=mask_prompt,
                    negative_prompt=negative_prompt,
                    outpainting_mode=outpainting_mode,
                    number_of_images=number_of_images,
                    model_id=selected_model_id  # Pass the selected model ID
                )
            
            # Display the generated images
            for img in generated_images:
                st.image(img)

# Tab 2: Image Understanding
with tab2:
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

    prompt_options = list(prompt_options_dict)

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

    image_options = list(image_options_dict)

    with col1:
        st.subheader("Select an Image")
        
        image_selection = st.radio("Image example:", image_options)
        
        if image_selection == 'Other':
            uploaded_file = st.file_uploader("Select an image", type=['png', 'jpg'], key="ui_file_uploader", label_visibility="collapsed")
        else:
            uploaded_file = None
        
        if uploaded_file and image_selection == 'Other':
            uploaded_image_preview = ui_glib.get_bytesio_from_bytes(uploaded_file.getvalue())
            st.image(uploaded_image_preview)
        else:
            st.image(image_options_dict[image_selection])
        
    with col2:
        st.subheader("Prompt")
        
        prompt_selection = st.radio("Prompt example:", prompt_options)
        
        prompt_example = prompt_options_dict[prompt_selection]
        
        prompt_text = st.text_area("Prompt",
            value=prompt_example,
            height=100,
            help="What you want to know about the image.",
            label_visibility="collapsed")
        
        go_button = st.button("Go", type="primary")
        
        
    with col3:
        st.subheader("Result")

        if go_button:
            with st.spinner("Processing..."):
                
                if uploaded_file:
                    image_bytes = uploaded_file.getvalue()
                else:
                    image_bytes = ui_glib.get_bytes_from_file(image_options_dict[image_selection])
                
                response = ui_glib.get_response_from_model(
                    prompt_content=prompt_text, 
                    image_bytes=image_bytes,
                )
            
            st.write(response)

# Tab 3: Image Resize
with tab3:
    st.title("Image Resize")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Select an Image")

        # File uploader for the image
        uploaded_file_resize = st.file_uploader("Select an image", type=['png', 'jpg'], key="resize_file_uploader")
        
        if uploaded_file_resize:
            # Display the original image and specs
            image = Image.open(uploaded_file_resize)
            width, height = image.size
            size_kb = len(uploaded_file_resize.getvalue()) / 1024
            st.image(image, caption="Original Image")
            st.text(f"Original image dimensions: {width}x{height}px")
            st.text(f"Original file size: {size_kb:.2f} KB")
        else:
            st.image("images/example.jpg")

    with col2:
        st.subheader("Resize Parameters")

        # Dropdown options for height
        default_heights = {
            "400px": 400,
            "500px": 500,
            "720px": 720,
            "768px": 768,
            "1080px": 1080,
            "Other (Custom)": None  # Custom option to allow user input
        }

        # Add a dropdown for selecting a default height
        selected_height_option = st.selectbox("Select Height (Width auto-calculated)", list(default_heights.keys()), help="Choose a height from the list or select 'Other' to input a custom height.")

        # If "Other (Custom)" is selected, allow the user to input custom height
        if selected_height_option == "Other (Custom)":
            new_height = st.number_input("Enter custom height:", min_value=1, max_value=5000, value=800)
        else:
            # Use the selected default height from the dropdown
            new_height = default_heights[selected_height_option]

        # Button for resizing the image
        resize_button = st.button("Resize Image")

    with col3:
        st.subheader("Result")

        # Show alert if trying to resize without uploading an image
        if resize_button and not uploaded_file_resize:
            st.error("Please upload an image before resizing!")

        # Resize the image when the resize button is clicked
        if resize_button and uploaded_file_resize:
            image_bytes_resize = uploaded_file_resize.getvalue()

            # Call the backend function to resize the image and calculate the new width automatically
            resized_image_io, calculated_width = resize_glib.resize_image_by_height(image_bytes_resize, new_height)

            # Store resized image in session state
            st.session_state["resized_image_io"] = resized_image_io

            # Display the resized image and specs
            resized_image = Image.open(resized_image_io)
            resized_width, resized_height = resized_image.size
            resized_size_kb = resized_image_io.getbuffer().nbytes / 1024
            st.image(resized_image, caption="Resized Image")
            st.text(f"Resized image dimensions: {resized_width}x{resized_height}px (calculated width: {calculated_width}px)")
            st.text(f"Resized file size: {resized_size_kb:.2f} KB")

            # Provide a download link for the resized image
            st.download_button(
                label="Download Resized Image",
                data=resized_image_io,
                file_name="resized_image.jpg",
                mime="image/jpeg"
            )

        # If the resized image is in the session state, display it
        if st.session_state.get("resized_image_io") is not None:
            try:
                resized_image = Image.open(st.session_state["resized_image_io"])
                st.image(resized_image, caption="Resized Image")
            except Exception as e:
                st.error(f"Error opening resized image: {str(e)}")

        # Button for applying super-resolution (enabled after resizing)
        apply_resolution_button = st.button("Apply Super-Resolution")

        # Show alert if trying to apply super-resolution without uploading an image or resizing it first
        if apply_resolution_button and not uploaded_file_resize:
            st.error("Please upload an image before applying resolution!")
        elif apply_resolution_button and st.session_state.get("resized_image_io") is None:
            st.error("Please resize the image first before applying resolution!")

        # If Apply Super-Resolution button is pressed
        if apply_resolution_button and st.session_state.get("resized_image_io") is not None:
            with st.spinner("Applying higher resolution..."):
                high_res_image_io = resize_glib.apply_high_resolution(st.session_state["resized_image_io"])

                # Store the high-resolution image in session state
                st.session_state["high_res_image_io"] = high_res_image_io

                # Display the high-resolution image
                try:
                    high_res_image = Image.open(high_res_image_io)
                    st.image(high_res_image, caption="High-Resolution Image")
                except Exception as e:
                    st.error(f"Error opening high-resolution image: {str(e)}")

                # Provide a download link for the high-resolution image
                st.download_button(
                    label="Download High-Resolution Image",
                    data=high_res_image_io,
                    file_name="high_res_image.jpg",
                    mime="image/jpeg"
                )

        # If the high-res image is in the session state, display it
        if st.session_state.get("high_res_image_io") is not None:
            try:
                high_res_image = Image.open(st.session_state["high_res_image_io"])
                st.image(high_res_image, caption="High-Resolution Image")
            except Exception as e:
                st.error(f"Error opening high-resolution image: {str(e)}")

# Tab 4: Video Upload and Playback (subtitle & translation)
with tab4:
    st.title("Video Upload and Playback")

    # S3 Client initialization
    bucket_name = "demo-portal-videos-jossai"

    col1, col2 = st.columns(2)

    # Video upload to S3
    with col1:
        st.subheader("Upload and Preview Video")
        uploaded_video = st.file_uploader("Select a video", type=['mp4', 'mov', 'avi'], key="video_uploader")

        if uploaded_video:
            # Display the uploaded video preview
            st.video(uploaded_video)

            # Use the backend method to upload the video to S3
            video_filename = uploaded_video.name
            content_type = "video/mp4"  # Assuming mp4, update if necessary based on the video type

            upload_status = sub_tran_glib.upload_file_to_s3(uploaded_video.getvalue(), bucket_name, video_filename, content_type)
            st.success(upload_status)

            # Automatically populate the video filename input field after upload
            st.session_state['video_filename'] = video_filename

    # Video rendering from S3
    with col2:
        st.subheader("Play and Process Video from S3")
        video_filename_input = st.text_input("Enter S3 video filename to play:", value=st.session_state.get('video_filename', ""))

        # Dropdown for selecting the translation language
        st.subheader("Select Translation Language")
        language_mapping = {"Spanish": "es", "French": "fr"}
        selected_language = st.selectbox("Select Language", list(language_mapping.keys()))

        # State to track if the video processing is completed
        video_processed = st.session_state.get("video_processed", False)

        # Buttons to process and play the video
        process_video_button = st.button("Process Video with Subtitles")
        play_button = st.button("Play Video with Subtitles", key="play_button")

        # Processing video with subtitles
        if process_video_button and video_filename_input:
            with st.spinner("Processing video..."):
                # Call the backend function to process video
                target_language_code = language_mapping[selected_language]
                result = sub_tran_glib.process_video_with_subtitles(
                    region="us-west-2",
                    inbucket=bucket_name,
                    infile=video_filename_input,
                    outbucket=bucket_name,
                    outfilename=video_filename_input.split('.')[0],  # Output filename without extension
                    outfiletype="mp4",  # Output file type
                    target_language=target_language_code  # Pass the selected language code to the backend
                )
                st.success(result)
                st.session_state["video_processed"] = True  # Mark video as processed

        # Playing the processed video with subtitles from S3
        if play_button and video_filename_input:
            subtitle_video_filename = f"{video_filename_input.split('.')[0]}_subtitle.mp4"
            
            # Use the backend method to get the S3 video URL
            video_url = sub_tran_glib.get_video_url_from_s3(bucket_name, subtitle_video_filename)

            # Display the video with subtitles from S3
            st.video(video_url)
            st.success(f"Playing video with subtitles from S3: {subtitle_video_filename}")

# Tab 5: Image to Video Demo
with tab5:
    st.title("Image to Video Demo")

    # First row with image on the left and video on the right
    col1, col2 = st.columns(2)

    # First Image (Lotion)
    with col1:
        st.image("loreal_images/aspect_resized_revitalift.jpg", caption="Revitalift Image", use_column_width=True)

    # First Video (Lotion) without the caption argument
    with col2:
        st.video("videos/revitalift.mp4")
        st.markdown("**Revitalift Video**")  # Add caption manually

    # Add spacing between the first row and the second row
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Second row with image on the left and video on the right
    col3, col4 = st.columns(2)

    # Second Image (Shampoo)
    with col3:
        st.image("loreal_images/cream_resized.jpg", caption="Cream Image", use_column_width=True)

    # Second Video (Shampoo) without the caption argument
    with col4:
        st.video("videos/cream.mp4")
        st.markdown("**Cream Video**")  # Add caption manually

    # Add spacing between the first row and the second row
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Second row with image on the left and video on the right
    col5, col6 = st.columns(2)

    # Second Image (Shampoo)
    with col5:
        st.image("loreal_images/shampoo_resized.jpg", caption="Shampoo Image", use_column_width=True)

    # Second Video (Shampoo) without the caption argument
    with col6:
        st.video("videos/shampoo.mp4")
        st.markdown("**Shampoo Video**")  # Add caption manually


