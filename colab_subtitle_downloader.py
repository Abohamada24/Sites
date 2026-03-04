# colab_subtitle_downloader.py

import requests
import os
from google.colab import widgets

def download_subtitle(url, language='en'):
    response = requests.get(url)
    if response.status_code == 200:
        filename = f"subtitle_{language}.srt"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Subtitle downloaded as {filename}")
    else:
        print("Failed to download subtitle")

# Simple UI for Google Colab
def create_ui():
    language_selector = widgets.Dropdown(
        options=['en', 'fr', 'es', 'de'],
        description='Language:',
        disabled=False,
    )

    url_input = widgets.Text(
        description='Subtitle URL:',
        disabled=False
    )

    download_button = widgets.Button(
        description='Download Subtitle'
    )

    output = widgets.Output()

    def on_button_clicked(b):
        with output:
            output.clear_output()
            download_subtitle(url_input.value, language_selector.value)

    download_button.on_click(on_button_clicked)

    display(language_selector, url_input, download_button, output)

if __name__ == "__main__":
    create_ui()