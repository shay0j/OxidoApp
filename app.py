import os
import openai
import configparser
import time
import re
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import traceback

# Read configurations from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Check if the required OpenAI API key is present in the configuration
if 'openai' not in config or 'api_key' not in config['openai']:
    raise ValueError("OpenAI API key not found in config.ini")

# Get the API key from the config file
api_key = config['openai']['api_key']
os.environ['OPENAI_API_KEY'] = api_key

# Initialize the OpenAI client
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Initialize FastAPI app
app = FastAPI()

# Path to the text file in the project folder
TEXT_FILE_PATH = "input.txt"
TEMPLATE_FILE_PATH = "szablon.html"  # Path to the template HTML file

# Endpoint for testing if the server is running
@app.get("/")
async def root():
    return {"message": "Cześć, Zespół Oxido! :)"}

# Endpoint to read the text file, send it to OpenAI, and save the result in an HTML file
@app.post("/process_text")
async def process_text():
    try:
        # Check if the input.txt file exists
        if not os.path.exists(TEXT_FILE_PATH):
            raise HTTPException(status_code=404, detail="Text file not found")

        # Read the content of the input.txt file
        with open(TEXT_FILE_PATH, 'r', encoding='utf-8') as file:
            text_str = file.read()

        # Function to split text into chunks based on max token size
        def split_text_into_chunks(text, max_tokens=4096):
            words = text.split()  # Split text into words
            chunk_size = max_tokens // 2  # Approximate chunk size (half for safety)
            chunks = []
            for i in range(0, len(words), chunk_size):
                chunks.append(' '.join(words[i:i + chunk_size]))
            return chunks

        text_chunks = split_text_into_chunks(text_str)

        # Prepare the initial prompt (structure and SEO guidelines)
        prompt_instructions = f"""
        You are a helpful assistant. Your task is to process the following text and generate a well-structured HTML article following these specific instructions for SEO.

        1. HTML Structure:
            - Only include the HTML content that would go inside the <body> section.
            - Use appropriate HTML tags to structure the content:
                - Use <h1> for the main title (one <h1> per page).
                - Use <h2> and <h3> for subheadings in a logical hierarchy.
                - Use <p> for paragraphs.
                - Do not include any links or anchor tags in the article.
        
        2. SEO Guidelines:
            - Use semantic HTML for better accessibility and search engine optimization.
            - Ensure that all headings (<h1>, <h2>, <h3>) include keywords related to the topic.
            - Avoid keyword stuffing—maintain a natural flow of language.
            - Include a <meta> description (150-160 characters) summarizing the article, including keywords.

        3. Images:
            - Identify places in the text where images should be inserted and mark them with <img> tags with a placeholder source: src="image_placeholder.jpg".
            - Provide detailed, descriptive alt attributes in Polish language for each image, explaining exactly what is shown in the image, including context within the article.
            - Add a <figcaption> in Polish language below each image. The caption should describe why the image is relevant to the text and how it relates to the content of the article.
            - Make sure the images are contextually appropriate in the article.

        4. Content:
            - Ensure the content is well-organized and readable.
            - Important keywords and phrases should be in bold using <strong> tags.
            - The last line should be in italics using the <em> tag.

        Important: Do not include any additional comments, explanations, or instructions. Only return the HTML structure with the content as described. No extra text or explanations.

        Here is the text to process:

        {text_str}
        """

        # First API call with the instructions
        retries = 3
        for attempt in range(retries):
            try:
                print("Sending instructions to OpenAI API:", prompt_instructions)

                # OpenAI API call for instructions (first part)
                response = openai.ChatCompletion.create(
                    model=config['LanguageModel']['model'],
                    messages=[{"role": "system", "content": "You are a helpful assistant."},
                              {"role": "user", "content": prompt_instructions}],
                    max_tokens=4096
                )

                print("Received response from OpenAI API:", response)

                # Access the response
                bot_response_instructions = response['choices'][0]['message']['content'].strip()
                break
            except openai.error.OpenAIError as e:
                print(f"OpenAI error on attempt {attempt + 1}/{retries}: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise HTTPException(status_code=500, detail="OpenAI API error: " + str(e))
            except Exception as e:
                print("Error:", str(e))
                raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))

        # Now prepare the final article by sending the content of the article as the second part
        final_article = ""
        for chunk in text_chunks:
            final_prompt = f"""
            {bot_response_instructions}

            Here is the text that needs to be structured into HTML:

            {chunk}
            """

            # Second API call with each chunk of the article
            retries = 3
            for attempt in range(retries):
                try:
                    print("Sending article chunk to OpenAI API:", final_prompt)

                    # OpenAI API call with the article (second part)
                    response = openai.ChatCompletion.create(
                        model=config['LanguageModel']['model'],
                        messages=[{"role": "system", "content": "You are a helpful assistant."},
                                  {"role": "user", "content": final_prompt}],
                        max_tokens=4096
                    )

                    print("Received response from OpenAI API:", response)

                    # Access the response correctly
                    chunk_article = response['choices'][0]['message']['content'].strip()
                    final_article += chunk_article
                    break
                except openai.error.OpenAIError as e:
                    print(f"OpenAI error on attempt {attempt + 1}/{retries}: {e}")
                    if attempt < retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        raise HTTPException(status_code=500, detail="OpenAI API error: " + str(e))
                except Exception as e:
                    print("Error:", str(e))
                    raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))

        # Clean up the article to remove any lines not within HTML tags and code blocks
        final_article = remove_non_html_lines(final_article)

        # Save the result in artykul.html
        with open("artykul.html", "w", encoding="utf-8") as file:
            file.write(final_article)

        # Now, generate the preview HTML by reading the template
        with open(TEMPLATE_FILE_PATH, "r", encoding="utf-8") as template_file:
            template_content = template_file.read()

        # Replace the placeholder in the template with the generated article
        preview_content = template_content.replace("<!-- Miejsce na wygenerowany artykuł -->", f"<article>{final_article}</article>")

        # Save the preview HTML
        with open("podglad.html", "w", encoding="utf-8") as preview_file:
            preview_file.write(preview_content)

        # Return the HTML response for preview
        return HTMLResponse(content=preview_content)

    except Exception as e:
        # Log the error to the console
        print("An error occurred:", str(e))
        print(traceback.format_exc())  # This will print the full traceback to help debug
        raise HTTPException(status_code=500, detail="Internal Server Error")

def remove_non_html_lines(text):
    """
    This function removes any lines from the text that are not enclosed in HTML tags.
    It also cleans the `html` and ``` blocks that are not inside HTML tags.
    """
    cleaned_text = []
    lines = text.split('\n')

    for line in lines:
        # Remove code block start and end markers
        if re.search(r'```html', line):  # Starting a code block
            continue  # Skip code block start
        elif re.search(r'```', line):  # Closing a code block
            continue  # Skip code block end
        
        # Keep only lines with HTML tags
        if re.search(r'<.*?>', line):  # Contains HTML tag
            cleaned_text.append(line)
        elif not line.strip():  # Ignore empty lines
            continue

    # Rejoin the remaining lines
    return '\n'.join(cleaned_text)
