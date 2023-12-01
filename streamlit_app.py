import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import shutil
import os

def process(images):
    total_width = max(image.width for image in images)
    total_height = sum(image.height for image in images)
    # Create a new blank image with the determined size
    concatenated_image = Image.new('RGB', (total_width, total_height), (255, 255, 255))

    # Paste each image onto the blank image
    current_height = 0
    for image in images:
        concatenated_image.paste(image, (0, current_height))
        current_height += image.height
    return concatenated_image.save('images.jpg', format='PNG')

def convert_pdf_to_images(pdf_path, num_pages=None):
    pdf_document = fitz.open(pdf_path)
    images = []

    if not num_pages:
        num_pages = pdf_document.page_count

    for page_number in range(min(num_pages, pdf_document.page_count)):
        page = pdf_document.load_page(page_number)
        image = page.get_pixmap()
        pil_image = Image.frombytes("RGB", [image.width, image.height], image.samples)
        images.append(pil_image)

    pdf_document.close()
    return images


def compress_folder_to_zip(folder_path, zip_file_name):
    shutil.make_archive(zip_file_name, 'zip', folder_path)

st.title("PDF to Image :)")
st.write("This is a simple tool to convert PDF to image :sparkles: ")
uploaded_file = st.file_uploader("Choose your PDF file", type=["pdf"])

if uploaded_file is not None:

    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getvalue())
    num_pages = fitz.open(uploaded_file.name).page_count
    images = convert_pdf_to_images(uploaded_file.name, num_pages)

    opt_concat_or_not = st.checkbox("Do you want to concatenate images ?")
    st.write('Number all of pages:', num_pages)
    num_pages_to_process = st.number_input('Number of pages to concatenate', min_value=1, max_value=num_pages)

    images_to_process = images[:num_pages_to_process]

    if st.button('Process'):
        if opt_concat_or_not:
            process(images_to_process)
            with open('images.jpg', 'rb') as file:
                st.download_button("Download concatenated image", data=file, file_name="image.jpg", mime="image/jpg")
            st.image('images.jpg')
            os.remove('images.jpg')
        else:
            os.mkdir('images')
            for i, image in enumerate(images_to_process):
                image.save(f'images/image{i}.jpg') 
            compress_folder_to_zip('images', 'images_zip')
            with open("images_zip.zip", "rb") as fp:
                st.download_button(
                    label="Download ZIP :exclamation:",
                    data=fp,
                    file_name="images_files.zip",
                    mime="application/zip"
                )
            command, command2 = 'rm -r images', 'rm *.zip'
            os.system(command)
            os.system(command2)
        os.remove(uploaded_file.name)