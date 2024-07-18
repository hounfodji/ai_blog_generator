# YouTube Blog Generator

This project is an innovative web application that automatically generates blog articles from YouTube videos. It uses artificial intelligence to transcribe the audio content of videos and create structured, well-written blog posts.

## Demo
![Youtube Blog generator interface](https://github.com/hounfodji/Super-Voice-Assistant/blob/master/z_demo/demo.png)
*Caption: Youtube Blog generator interface.*

## Features

- Blog article generation from YouTube links
- User authentication (sign up, login, logout)
- List of generated blog articles per user
- Detailed view of blog articles

## Technologies Used

- **Frontend**: HTML, CSS, JS
- **Backend**: Django
- **Transcription API**: AssemblyAI
- **Content Generation**: Replicate / LLaMA 2 model
- **YouTube Audio Extraction**: pytube

## Project Setup

### Prerequisites

- Python 3.x
- AssemblyAI account for transcription
- Replicate account for content generation

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/hounfodji/ai_blog_generator/
   cd ai_blog_generator
   ```

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   Create a `.env` file in the project root and add:
   ```
   ASSEMBLYAI_API_KEY=your_assemblyai_api_key
   REPLICATE_API_TOKEN=your_replicate_api_token
   ```

4. Run Django migrations:
   ```
   python manage.py migrate
   ```

### Launching the Project

1. Start the Django server:
   ```
   python manage.py runserver
   ```

## Usage

1. Sign up or log in to the application.
2. Paste a YouTube link in the provided field.
3. Click "Generate Blog" and wait for the article to be created.
4. View your new article in the list of generated blogs.

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.
