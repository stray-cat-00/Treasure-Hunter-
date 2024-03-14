import streamlit as st
import pydeck as pdk
import pandas as pd
import requests
import random

# Fetch countries data with caching
@st.cache(suppress_st_warning=True, allow_output_mutation=True)

def fetch_countries_data():
    url = "https://restcountries.com/v3.1/all"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        countries = [{
            'CountryName': country['name']['common'],
            'Latitude': country['latlng'][0] if country['latlng'] else 0,
            'Longitude': country['latlng'][1] if country['latlng'] else 0,
        } for country in data if 'latlng' in country and country.get('name')]
        return pd.DataFrame(countries)
    except requests.RequestException as e:
        st.error(f"Error fetching countries data: {e}")
        return pd.DataFrame()

def welcome_page():
    st.markdown("""
        <style>
            .big_title { color: #f5f5dc; font-size: 50px; text-align: center; }
            .subtitle { color: #add8e6; font-size: 30px; text-align: center; }
            .stButton>button { font-size: 20px; border: 2px solid; border-radius: 20px; padding: 10px 24px; margin-top: 20px; }
        </style>
        """, unsafe_allow_html=True)
    st.markdown('<div class="big_title">Welcome to Treasure Hunter...</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Double Click to Embark on Your Next Adventure...</div>', unsafe_allow_html=True)

    if st.button('Allons-y!'):
        st.session_state.show_welcome = False

def manage_country_selection(df_countries, selected_country):
    if selected_country:
        st.subheader(f"Selected Country: {selected_country}")
        favorite_button, unfavorite_button = st.columns(2)
        with favorite_button:
            if st.button("💗", help="Add to favorites!"):
                if selected_country not in st.session_state.favorites:
                    st.session_state.favorites.append(selected_country)
                    st.success(f"Added {selected_country} to favorites!")
                else:
                    st.warning("Country already in favorites.")
        with unfavorite_button:
            if st.button("💔", help="Remove from favorites..."):
                if selected_country in st.session_state.favorites:
                    st.session_state.favorites.remove(selected_country)
                    st.success(f"Removed {selected_country} from favorites.")
                else:
                    st.info("Country not in favorites.")



def get_country_information(destination):
    rest_countries_api_url = f"https://restcountries.com/v3.1/name/{destination}?fullText=true"
    response = requests.get(rest_countries_api_url)
    data = response.json()

    details = {
        "Name": "Not available",
        "Capital": "Not available",
        "Population": "Not available",
        "Region": "Not available",
        "Subregion": "Not available",
        "Flag": "Not available",
        "Borders": "Not available",
        "Languages": "Not available",
        "Timezones": "Not available",
    }

    if data and isinstance(data, list):
        country_data = data[0]

        details["Name"] = country_data.get("name", {}).get("common", "Not available")
        details["Capital"] = country_data.get("capital", ["Not available"])[0]
        details["Population"] = country_data.get("population", "Not available")
        details["Region"] = country_data.get("region", "Not available")
        details["Subregion"] = country_data.get("subregion", "Not available")
        details["Flag"] = country_data.get("flags", {}).get("png", "Not available")
        details["Borders"] = ", ".join(country_data.get("borders", ["Not available"]))
        details["Languages"] = ", ".join([value for key, value in country_data.get("languages", {}).items()])
        details["Timezones"] = ", ".join(country_data.get("timezones", ["Not available"]))
    return details
def display_country_information(selected_country):
    if selected_country:
        country_info = get_country_information(selected_country)
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(country_info['Flag'], caption=f"Flag of {country_info['Name']}", use_column_width=True)
        with col2:
            st.subheader(f"Information about {selected_country}:")
            st.write(f"Capital: {country_info['Capital']}")
            st.write(f"Population: {country_info['Population']}")
            st.write(f"Region: {country_info['Region']}")
            st.write(f"Subregion: {country_info['Subregion']}")
            st.write(f"Borders: {country_info['Borders']}")
            st.write(f"Languages: {country_info['Languages']}")
            st.write(f"Timezones: {country_info['Timezones']}")
def display_country_map(df_countries, selected_country):
    country_data = df_countries[df_countries["CountryName"] == selected_country].iloc[0] if selected_country in \
                                                                                            df_countries[
                                                                                                "CountryName"].values else None
    view_state = pdk.ViewState(
        latitude=country_data["Latitude"] if country_data is not None else 0,
        longitude=country_data["Longitude"] if country_data is not None else 0,
        zoom=4 if country_data is not None else 1,
        pitch=0,
        bearing=0
    )

    country_layer = pdk.Layer(
        "ScatterplotLayer",
        df_countries,
        get_position="[Longitude, Latitude]",
        get_color="[255, 255, 255, 25]",
        get_radius=25000,
        pickable=True,
    )

    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v10",
        initial_view_state=view_state,
        layers=[country_layer],
        tooltip={"html": "<b>Country:</b> {CountryName}", "style": {"color": "white"}},
    ))
def main_app():
    df_countries = fetch_countries_data()

    st.session_state.setdefault('selected_country', "")
    st.session_state.setdefault('favorites', [])

    st.header("Treasure Hunter 🗺️")
    selected_country = st.text_input("Search for a Country 🌍🌎🌏", value=st.session_state.selected_country, key="country_input")

    country_action, clear_action = st.columns([3, 1])

    with country_action:
        if st.button("Randomize!🌀", help="Click to Randomly Land on a Country!"):
            st.session_state.selected_country = random.choice(df_countries["CountryName"].tolist())
            selected_country = st.session_state.selected_country

    with clear_action:
        if st.button("Clear!", help="Clear the Input!"):
            st.session_state.selected_country = ""
            st.experimental_rerun()

    manage_country_selection(df_countries, selected_country)
    display_country_map(df_countries, selected_country)
    display_country_information(selected_country)

# Function to fetch and display hidden gems
def show_treasures():
    API_KEY = 'bE0a_pzegp0eu7eBqF0N1hoXSjxtjBh7O9fTRFPMYM0l6ZPD76GYDDgeX4WG6S-qLgGDfwj67LpGNGW-uoEtZxiCuMJEjXKwcI9DZoGE3e84u4vrpQufaGg-5_3yZXYx'
    st.title("Treasure Hunter - Hidden Gems")
    country = st.text_input("Enter the country to find hidden gems:")

    if country:
        st.info("Fetching hidden gems...")
        hidden_gems = get_hidden_gems(country, API_KEY)

        if hidden_gems:
            st.success(f"Found them! Treasure spots for you to visit in {country}:")
            for gem in hidden_gems:
                with st.container():
                    st.markdown(f"**Name:** {gem['name']}")
                    st.markdown(f"**Rating:** {gem['rating']}")
                    st.markdown(f"**Address:** {', '.join(gem['location']['display_address'])}")
                    st.markdown("---")  # Adds a horizontal line for better separation
        else:
            st.warning("That's a great choice :). But unfortunately, we don't have enough information on this location yet. Soon to be updated ;)")

def get_hidden_gems(country, api_key):
    api_endpoint = "https://api.yelp.com/v3/businesses/search"
    params = {
        "term": "hidden gems",
        "location": country,
        "categories": "restaurants",
        "sort_by": "rating",
        "radius": 20000,  # Increased radius to 20 km (adjust as needed)
        "limit": 5
    }
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(api_endpoint, params=params, headers=headers)

    if response.status_code == 200:
        return response.json().get("businesses", [])
    else:
        st.error("Failed to fetch hidden gems :(")
        return []

def display_favorites_sidebar():
    # Initialize favorites list in session state if it doesn't exist
    if 'favorites' not in st.session_state:
        st.session_state.favorites = []

    st.sidebar.title("My Favorites")
    if st.session_state.favorites:
        for country in st.session_state.favorites:
            row = st.sidebar.container()
            row.text(country)
            # Provide an option to remove from favorites
            if row.button(f"Remove {country}", key=f"btn_remove_{country}"):
                st.session_state.favorites.remove(country)
                st.sidebar.success(f"Removed {country} from favorites")
    else:
        st.sidebar.write("No favorite countries yet. Add some!")


# Navigation and Page Management
def main():
    display_favorites_sidebar()
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Discover Hidden Gems"])

    if page == "Home":
        main_app()
    elif page == "Discover Hidden Gems":
        show_treasures()

if __name__ == "__main__":
    if 'show_welcome' not in st.session_state or st.session_state.show_welcome:
        welcome_page()
    else:
        main()
