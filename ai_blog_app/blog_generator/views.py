import os
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import json
from pytube import YouTube
import assemblyai as aai
import openai 
import requests
import replicate
from dotenv import load_dotenv
load_dotenv()
from .models import BlogPost

@login_required
def index(request):
    return render(request, "index.html")

@csrf_exempt
def generate_blog(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            yt_link = data['link']
            # return JsonResponse({'content' : yt_link})
        except(KeyError, json.JSONDecodeError):
            return JsonResponse({"Error": "Invalid data sent"}, status=400)
    else:
        return JsonResponse({"Error": "Invalid request method"}, status=405)

    # get yt title
    title = yt_title(yt_link)

    # get transcript
    transcription = get_transcription(yt_link)
    if not transcription:
        return JsonResponse({'error': " Failed to get transcript"}, status=500)

    # use openAI to generate the blog
    blog_content = generate_blog_transcription_replicate(transcription)
    if not blog_content:
        return JsonResponse({'error': " Failed to generate blog article"}, status=500)

    # save blog aticle to database
    new_blog_article = BlogPost.objects.create(
            user=request.user,
            youtube_title=title,
            youtube_link=yt_link,
            generated_content=blog_content,
        )
    new_blog_article.save()

    # return blog article as a response
    return JsonResponse({'content': blog_content})

# function to get youtube video title
def yt_title(link):
    yt = YouTube(link)
    title = yt.title
    return title

# download audio from video
def download_audio(link):
    yt = YouTube(link)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download(output_path=settings.MEDIA_ROOT)
    base, ext = os.path.splitext(out_file)
    new_file = base + ".mp3"
    os.rename(out_file, new_file)
    return new_file

# get video transcription
def get_transcription(link):
    audio_file = download_audio(link)
    aai.settings.api_key = "80787ecb388f45bca1c68c7c771c1317"


    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)
    print(transcript.text)

    return transcript.text

# generate blog from transcription
def generate_blog_from_transcription(transcription):
    openai.api_key = "sk-CtsnEOwT9ZFZtqtRFfEcA589DcC54b6e8404D5B1095f97Db"

    prompt = f"Based on the following transcript from a YouTube video, write a comprehensive blog article, write it based on the transcript, but dont make it look like a youtube video, make it look like a proper blog article:\n\n{transcription}\n\nArticle:"

    response = openai.completions.create(model="gpt-3.5-turbo-instruct",
    prompt=prompt,
    max_tokens=1000)

    generated_content = response.choices[0].text.strip()

    return generated_content

# generate blog from transcription using llama2
def generate_blog_from_transcription_llama(transcription):
    # Ollama API endpoint and model name
    url = "http://localhost:11434/api/generate"
    model_name = "llama2"

    # Prompt construction (similar to OpenAI)
    prompt = f"Based on the following transcript from a YouTube video, write a comprehensive blog article, write it based on the transcript, but don't make it look like a youtube video, make it look like a proper blog article:\n\n{transcription}\n\nArticle:"

    # Prepare data for Ollama API request
    data = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "format": "json",
    }

    # Send POST request to Ollama API
    response = requests.post(url, json=data)

    # Check for successful response
    if response.status_code == 200:
        try:
            # Assuming single nested JSON with "response" key
            response_data = response.json()
            generated_content = response_data["response"]
            print(generated_content)  # This will print the actual result (likely {"result": 2})
            # data = json.loads(generated_content)
            # message = data["message"]
            # print("Response:")
            # print(message)
            return generated_content
        except (KeyError, json.JSONDecodeError):
            print("Error: Unexpected response format.")
         
    else:
        # Handle error (e.g., print error message)
        print(f"Error generating content: {response.status_code}")
        return None

# generate blog transcription using replicae
def generate_blog_transcription_replicate(transcription):
    input = {
        "top_p": 1,
        "prompt": f"Based on the following transcript from a YouTube video, write a comprehensive blog article, write it based on the transcript, but don't make it look like a youtube video, make it look like a proper blog article and style it properly(with <h1>, <h2>, <br>) so it will look beautiful on a webpage:\n\n{transcription}\n\nArticle:",
        "temperature": 0.5,
        "system_prompt": "You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.\n\nIf a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.",
        "max_new_tokens": 500
    }

    output = replicate.run(
        "meta/llama-2-70b-chat",
        input=input
    )
    # print("".join(output))
    return "".join(output)

def blog_list(request):
    blog_articles = BlogPost.objects.filter(user=request.user)
    return render(request, "all-blogs.html", {'blog_articles': blog_articles})

def blog_details(request, pk):
    blog_article_detail = BlogPost.objects.get(id=pk)
    if request.user == blog_article_detail.user:
        return render(request, 'blog-details.html', {'blog_article_detail': blog_article_detail})
    else:
        return redirect('/')
    
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            error_message = "Invalid username or password"
            return render(request, 'login.html', {'error_message' : error_message})
    return render(request, "login.html")

def user_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirmPassword = request.POST['confirmPassword']

        if password == confirmPassword:
            try:
                user = User.objects.create_user(username, email, password)
                # user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                login(request, user)
                return redirect('/')
            except:
                error_message = "Error creating account."
                return render(request, 'register.html', {'error_message' : error_message})
        else:
            error_message = "Password doesn't match"
            return render(request, 'register.html', {'error_message' : error_message})

    return render(request, "register.html")

def user_logout(request):
    logout(request)
    return redirect('/')
