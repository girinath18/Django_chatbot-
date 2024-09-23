from django.shortcuts import render
from django.http import JsonResponse
import json
import io
import random
import string
import warnings
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.stem import WordNetLemmatizer
import os

# Suppress warnings
warnings.filterwarnings('ignore')

# Ensure NLTK resources are available
def ensure_nltk_resources():
    nltk_data_path = "V:\\jango_bot\\chatbot_project\\nltk_data"
    os.makedirs(nltk_data_path, exist_ok=True)
    nltk.data.path.append(nltk_data_path)

    # Check and download necessary resources
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', download_dir=nltk_data_path)

    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet', download_dir=nltk_data_path)

# Ensure resources are available at the start
ensure_nltk_resources()

# Initialize lemmatizer
lemmer = WordNetLemmatizer()

# Define greeting inputs and responses
GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up", "hey",)
GREETING_RESPONSES = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]

def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]

def LemNormalize(text):
    remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))

def greeting(sentence):
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)
    return None

def response(user_response, sent_tokens):
    robo_response = ''
    sent_tokens.append(user_response)
    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
    tfidf = TfidfVec.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1], tfidf)
    idx = vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]
    
    if req_tfidf == 0:
        robo_response = "I am sorry! I don't understand you"
    else:
        robo_response = sent_tokens[idx]
        
    sent_tokens.pop()
    return robo_response

def chat_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "")
        if 'sent_tokens' not in request.session:
            # Initialize an empty list if not yet set in the session
            request.session['sent_tokens'] = []
        sent_tokens = request.session['sent_tokens']

        # Process the user message
        response = chatbot_response(user_message, sent_tokens)
        return JsonResponse({"response": response})
    
    return render(request, "chat_interface.html")

def upload_file(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            try:
                # Read the contents of the uploaded text file
                content = uploaded_file.read().decode('utf-8')
                sent_tokens = nltk.sent_tokenize(content)  # Tokenize the uploaded content
                request.session['sent_tokens'] = sent_tokens  # Store in session for further use

                response = "File uploaded successfully. You can start asking questions."
                return JsonResponse({"response": response})
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
        else:
            return JsonResponse({"error": "No file uploaded"}, status=400)
    
    return render(request, "upload_file.html")

def chatbot_response(user_input, sent_tokens):
    if user_input.lower() == 'bye':
        return "Bye! take care.."
    elif greeting(user_input) is not None:
        return greeting(user_input)
    else:
        return response(user_input, sent_tokens)
