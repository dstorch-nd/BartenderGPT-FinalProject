import streamlit as st
from PIL import Image
from openai import OpenAI
import io
import os
import base64

OpenAI.api_key = st.secrets["API_KEY"]

client = OpenAI()

# define function for converting image data to base64 for gpt entry
def encode_image(image_data):
    return base64.b64encode(image_data).decode("utf-8")

# function to find matching cocktails based on an image using gpt
def find_cocktails_with_image(image_data):
    #client.api_key = st.secrets["openai"]["key"]

    base64_image = encode_image(image_data)

    prompt = (
        "You are a bartender. I am uploading a photo of my liquor bottles and mixers. "
        "Identify the ingredients in the photo and suggest cocktails that can be made along with their recipes."
    )

    # create message for gpt with prompt and encoded image data
    try:
        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "You are a helpful bartender."},
                {"role": "user","content": [{"type": "text", "text": prompt,},
                                            {"type": "text", "text": "What is in this image?",},
                                            {"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},},
                                            ],},
            ]
        )
        return response.choices[0].message.content # future: possibly remove .message.content?
    except Exception as e:
        return f"Error fetching recipes: {str(e)}"

# Streamlit app
st.title("Dane's Cocktail Recipe Generator")

st.sidebar.header("Choose a method to input your ingredients:")
method = st.sidebar.radio("Input Method", ("Upload Photo", "Manually Select Ingredients"))

if method == "Upload Photo":
    st.subheader("Upload a photo of your liquor and mixers")
    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)
        st.write("Processing your image...")

        # convert the image to binary data
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="JPEG")
        image_data = image_bytes.getvalue()

        # call function to create cocktails
        cocktails = find_cocktails_with_image(image_data)
        if cocktails:
            st.success("Here are some cocktail suggestions:")
            st.write(cocktails)
        else:
            st.error("No matching cocktails found with your ingredients.")

elif method == "Manually Select Ingredients":
    st.subheader("Select the ingredients you have")

    alcohols = ["Vodka", "Tequila", "Gin", "White Rum", "Dark Rum", "Whiskey", "Sparkling Wine", "Herbal Liquor", "Vermouth", "Triple Sec", "Bitters", "Cream Liqueur"]
    mixers = ["Coca Cola", "Sprite", "Soda Water", "Simple Syrup", "Grenadine Syrup", "Lemon", "Lime", "Orange" "Mint", "Heavy Cream", "Pineapple Juice", "Lemonade", "Orange Juice", "Tomato Juice", "Tabasco", "Worcestershire Sauce"]

    selected_alcohols = st.multiselect("Select alcohols", alcohols)
    selected_mixers = st.multiselect("Select mixers", mixers)

    selected_ingredients = selected_alcohols + selected_mixers

    if selected_ingredients:
        st.write("Selected Ingredients:", ", ".join(selected_ingredients))

        # call function to create cocktails
        prompt = (
            f"You are a bartender. Given the following ingredients: {', '.join(selected_ingredients)}, "
            "suggest cocktails that can be made along with their recipes."
        )

        # create message for gpt based on prompt and drink selections
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful bartender."},
                    {"role": "user", "content": prompt}
                ]
            )
            cocktails = response.choices[0].message.content
            st.success("Here are some cocktail suggestions:")
            st.write(cocktails)
        except Exception as e:
            st.error(f"Error fetching recipes: {str(e)}")
    else:
        st.info("Please select at least one ingredient to see matching cocktails.")
