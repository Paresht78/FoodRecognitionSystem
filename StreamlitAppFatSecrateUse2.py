import streamlit as st
import requests
from keras.applications import MobileNet
from keras.preprocessing import image
from keras.applications.mobilenet import preprocess_input, decode_predictions
from keras.models import load_model
import numpy as np
import pandas as pd

# Load the MobileNet model
model = load_model('FV.h5')
model = MobileNet(weights='imagenet')

def predict_food(image_path):
    # Function to predict the food item from an image
    img = image.load_img(image_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)
    decoded_preds = decode_predictions(preds, top=1)[0]
    return decoded_preds[0][1]

def get_nutrition(food_name, access_token):
    # Function to get nutrition information using the FatSecret API
    api_url = 'https://platform.fatsecret.com/rest/server.api'
    api_params = {
        'method': 'foods.search',
        'format': 'json',
        'search_expression': food_name,
    }
    api_headers = {
        'Authorization': f'Bearer {access_token}',
    }

    # Make the API request
    response = requests.get(api_url, params=api_params, headers=api_headers)
    data = response.json()
    return data

def get_access_token(client_id, client_secret):
    # Function to obtain OAuth 2.0 access token
    token_url = 'https://oauth.fatsecret.com/connect/token'
    token_payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    }

    # Request access token
    response = requests.post(token_url, data=token_payload)
    if response.status_code == 200:
        access_token = response.json().get('access_token')
        return access_token
    else:
        return None

# Main function
def main():
    # Title for the app
    st.title("Food Nutrition App	:green_apple:")

    # Client credentials provided by FatSecret
    client_id = '78c50bce3cc74a608af81c2612eba42a'
    client_secret = '361c4ee5cb3b4960bfab1ce0e4694e1a'

    # Upload image file
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png"])

    if uploaded_file is not None:
        # Display the uploaded image
        st.image(uploaded_file, caption='Uploaded Image.', use_column_width=True)

        # Predict the food item from the image
        with st.spinner('Predicting...'):
            food_name = predict_food(uploaded_file)

        st.write(f"Predicted Food: {food_name}")

        # Obtain OAuth 2.0 access token
        access_token = get_access_token(client_id, client_secret)
        if access_token:
            # Get nutrition information using the access token
            with st.spinner('Fetching Nutrition Information...'):
                nutrition_info = get_nutrition(food_name, access_token)
                if 'foods' in nutrition_info and 'food' in nutrition_info['foods']:  # Check if the expected keys are present
                    food_data = []
                    for item in nutrition_info['foods']['food']:
                        food_data.append({'Name': item['food_name'], 'Description': item['food_description']})
                    df = pd.DataFrame(food_data)
                    st.write(df)
                else:
                    st.error("No nutrition information found.")
        else:
            st.error("Failed to obtain access token.")

if __name__ == "__main__":
    main()
