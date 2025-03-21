import uuid
import streamlit as st
import os
from dotenv import load_dotenv
from blog_generator import generate_outline, write_section
from fpdf import FPDF  # Import FPDF for PDF generation

def save_as_pdf(content, filename):
    """
    Saves the given content as a PDF file.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=content)
    pdf.output(filename)

def create_blog_post(topic, blog_subject):
    try:
        # Outline generation
        with st.spinner("Generating Outline..."):
            json_outline = generate_outline(topic, blog_subject)

        if "error" in json_outline:
            st.error(f"Error: {json_outline['error']}")
            return ""

        # Title and sections
        blog_title = json_outline.get('title', 'Untitled')
        st.markdown(f"# {blog_title}")

        # Write sections
        blog_sections = json_outline.get('sections', [])
        history_text = ''
        for section in blog_sections:
            st.divider()
            with st.spinner(f"Writing Section '{section['header']}'..."):
                content = write_section(topic, section['header'], section['sub-sections'], history_text)
            history_text += content
            st.markdown(content)  # Display the section content on the Streamlit page

        # Return history text
        return history_text

    except Exception as e:
        st.error(f"Error in create_blog_post: {e}")
        return ""


# Page configuration
st.set_page_config(
    page_title="Blog Post Generator",
    page_icon=":pencil2:",
    layout="centered",
)

# Page Title
st.title("Blog Post Generator", anchor=False)

# Page Description
st.markdown(f"""
Welcome to Blog Post Generator!\n\n
This site is minimalistic but powerful. It uses the latest AI technology and proprietary models to generate a blog post 
for you with just a category and subject.\n\n
You can download the generated blog post as a text file or a PDF.\n\n
Contact me on 'X' at [@DevAsService](https://twitter.com/DevAsService) if you have any questions.\n\n
© 2023 [Developer Service](https://developer-service.io/)
""")

# Category, Subject, and Generate Button
st.divider()
st.subheader("Generate Your Blog Post", anchor=False)
category = st.selectbox(
    "Category",
    ("", "Travel", "Technology", "Business", "Health", "Science", "Sports", "Entertainment", "Politics", "Education")
)
subject = st.text_input("Subject")
generate = st.button("Generate Blog Post")

if generate:
    # Validate inputs
    error = ""
    if category == "":
        error += "Please select a category.\n\n"
    if subject == "":
        error += "Please enter a subject.\n\n"
    if error != "":
        st.error(error)
        st.stop()

    # Create blog post
    st.divider()
    history = create_blog_post(category, subject)
    st.divider()
    st.success("Blog post generated successfully!")

    # Generate a unique filename
    random = uuid.uuid4().hex
    txt_filename = f"{category}_{subject}_{random}.txt"
    pdf_filename = f"{category}_{subject}_{random}.pdf"

    # Save as text file
    with open(txt_filename, "w") as f:
        f.write(history)

    # Save as PDF file
    save_as_pdf(history, pdf_filename)

    # Download buttons
    st.download_button(
        label="Download Blog Post as Text",
        data=history,
        file_name=txt_filename,
        mime="text/plain",
        help="Download the blog post as a text file."
    )

    with open(pdf_filename, "rb") as f:
        st.download_button(
            label="Download Blog Post as PDF",
            data=f,
            file_name=pdf_filename,
            mime="application/pdf",
            help="Download the blog post as a PDF file."
        )
