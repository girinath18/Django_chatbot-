from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from .models import CustomUser
from .models import UploadedFile
from django.contrib.auth.decorators import login_required
from .models import Conversation
import json
import random
import nltk
import os
import string
import warnings
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import ChatHistory
from django.db.models import Count
from django.db.models.functions import TruncDate

# Suppress warnings
warnings.filterwarnings('ignore')

# Set custom NLTK data path
nltk_data_path = "C:\\Users\\USER\\AppData\\Roaming\\nltk_data\\tokenizers\\punkt_tab\\"
os.makedirs(nltk_data_path, exist_ok=True)
nltk.data.path.append(nltk_data_path)

# Ensure NLTK resources are available
def ensure_nltk_resources():
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

lemmer = WordNetLemmatizer()

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
    
    # Check if we have more than one token
    if len(sent_tokens) > 1:
        TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
        tfidf = TfidfVec.fit_transform(sent_tokens)
        vals = cosine_similarity(tfidf[-1], tfidf)
        
        # Proceed only if vals has more than one entry
        if vals.shape[1] > 1:
            idx = vals.argsort()[0][-2]
            flat = vals.flatten()
            flat.sort()
            req_tfidf = flat[-2]
            
            if req_tfidf == 0:
                robo_response = "I am sorry! I don't understand you"
            else:
                robo_response = sent_tokens[idx]
        else:
            robo_response = "I need more information to respond effectively."
    else:
        robo_response = "I need more information to respond effectively."

    sent_tokens.pop()
    return robo_response

# Chatbot view
def chat_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "")
        
        # Initialize session tokens if not present
        if 'sent_tokens' not in request.session:
            request.session['sent_tokens'] = []

        sent_tokens = request.session['sent_tokens']

        # Generate bot response using your existing logic
        response_message = chatbot_response(user_message, sent_tokens)

        # Store both user and bot messages in the database
        Conversation.objects.create(user=request.user, message=user_message)  # Store user's message
        Conversation.objects.create(user=request.user, message=response_message)  # Store bot's response

        return JsonResponse({"response": response_message})

    return render(request, "chat_interface.html")  # Render the chat page for GET requests

def upload_file(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            try:
                content = uploaded_file.read().decode('utf-8')
                sent_tokens = nltk.sent_tokenize(content)
                request.session['sent_tokens'] = sent_tokens

                # Redirect to the chat view after successful upload
                return redirect('chat_view')
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
        else:
            return JsonResponse({"error": "No file uploaded"}, status=400)

    return render(request, "upload_file.html")

# Chatbot response logic
def chatbot_response(user_input, sent_tokens):
    if user_input.lower() == 'bye':
        return "Bye! take care.."
    elif greeting(user_input) is not None:
        return greeting(user_input)
    else:
        return response(user_input, sent_tokens)

# Signup view
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({"message": "Username already exists"}, status=400)

        # Hash the password before storing it for security
        user = User.objects.create(username=username, password=make_password(password))
        user.save()

        return JsonResponse({"message": "User created successfully"}, status=201)

    # If it's a GET request, render the signup form
    return render(request, 'signup.html')

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')  
        else:
            return JsonResponse({"message": "Invalid credentials"}, status=400)

    return render(request, 'login.html')

# Dashboard view
@login_required  # Ensures only logged-in users can access the dashboard
def dashboard(request):
    return render(request, 'dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile_view(request):
    user = request.user  
    signup_date = user.date_joined  
    return render(request, 'profile.html', {'user': user, 'signup_date': signup_date})

@login_required
def chat_history_view(request):
    chat_history = ChatHistory.objects.annotate(
        date=TruncDate('timestamp')
    ).values('date').annotate(count=Count('id'))

    # Fetch messages associated with each date
    chat_messages = {}
    for entry in chat_history:
        messages = ChatHistory.objects.filter(timestamp__date=entry['date'])
        chat_messages[entry['date']] = messages

    return render(request, 'chat_history.html', {'chat_messages': chat_messages})