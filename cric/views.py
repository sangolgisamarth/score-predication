from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Cricket,Feedback
from .models import Cricket, Feedback, Team, Player, Format, PlayerStats, ReportCard
from django.http import JsonResponse
from django.core.paginator import Paginator
import pickle
import pandas as pd
import os
from django.conf import settings
import requests
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render


'''dash page'''
def dash(request):  
    return render(request,'dash.html')


def profile(request):
    return render(request,'profile.html')


'''login page'''
def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return redirect("home") 

        messages.error(request, "Invalid Username or Password")
        return redirect("login_page")

    return render(request, "login.html")



def logout_view(request):
    logout(request)
    return redirect("login_page")

'''register page'''
def register(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken. Choose a different one.")
            return redirect("register")

        user = User.objects.create_user(
            first_name=first_name, last_name=last_name, username=username, password=password
        )  
        user.save()

        messages.success(request, "Account created successfully! Please log in.")
        return redirect("login_page")  

    return render(request, "register.html")


def home(request):
    return render(request, "home.html")


'''model-1'''


# Load the model safely using BASE_DIR
MODEL_PATH = os.path.join(settings.BASE_DIR, 'cric', 'ml-models', 'pipe.pkl')

try:
    with open(MODEL_PATH, 'rb') as model_file:
        pipe = pickle.load(model_file)
except FileNotFoundError:
    pipe = None

teams = [
    'Australia', 'India', 'Bangladesh', 'New Zealand', 'South Africa', 
    'England', 'West Indies', 'Afghanistan', 'Pakistan', 'Sri Lanka'
]

cities = [
    'Colombo', 'Mirpur', 'Johannesburg', 'Dubai', 'Auckland', 'Cape Town', 
    'London', 'Pallekele', 'Barbados', 'Sydney', 'Melbourne', 'Durban', 
    'St Lucia', 'Wellington', 'Lauderhill', 'Hamilton', 'Centurion', 
    'Manchester', 'Abu Dhabi', 'Mumbai', 'Nottingham', 'Southampton', 
    'Mount Maunganui', 'Chittagong', 'Kolkata', 'Lahore', 'Delhi', 
    'Nagpur', 'Chandigarh', 'Adelaide', 'Bangalore', 'St Kitts', 'Cardiff', 
    'Christchurch', 'Trinidad'
]

def result(request):
    prediction = None
    error = None

    if request.method == 'POST':
        try:
            if not pipe:
                raise ValueError("Model file not found.")

            batting_team = request.POST.get('batting_team', '').strip()
            bowling_team = request.POST.get('bowling_team', '').strip()
            city = request.POST.get('city', '').strip()
            current_score = request.POST.get('current_score', '').strip()
            overs = request.POST.get('overs', '').strip()
            wickets = request.POST.get('wickets', '').strip()
            last_five = request.POST.get('last_five', '').strip()

            required_fields = [batting_team, bowling_team, city, current_score, overs, wickets, last_five]
            if any(not field for field in required_fields):
                error = 'All fields are required.'
            elif not (current_score.isdigit() and overs.replace('.', '', 1).isdigit() and 
                      wickets.isdigit() and last_five.isdigit()):
                error = 'Invalid input: Please enter valid numbers.'
            else:
                current_score = int(current_score)
                overs = float(overs)
                wickets = int(wickets)
                last_five = int(last_five)

                if overs == 0:
                    error = 'Invalid input: Overs cannot be zero.'
                else:
                    balls_left = 120 - int(overs * 6)
                    wickets_left = 10 - wickets
                    crr = current_score / overs

                    input_df = pd.DataFrame({
                        'batting_team': [batting_team],
                        'bowling_team': [bowling_team],
                        'city': [city],
                        'current_score': [current_score],
                        'balls_left': [balls_left],
                        'wicket_left': [wickets_left],  
                        'current_run_rate': [crr],
                        'last_five': [last_five]
                    })

                    result = pipe.predict(input_df)
                    prediction = int(result[0])

        except Exception as e:
            error = f'An error occurred: {e}'

    return render(request, 'index.html', {
        'teams': sorted(teams),
        'cities': sorted(cities),
        'prediction': prediction,
        'error': error
    })



'''model-2'''

model2_path = os.path.join(os.path.dirname(__file__), 'ml-models', 'model2.pkl')
try:
    with open(model2_path, 'rb') as file:
        pipe_model2 = pickle.load(file)
except FileNotFoundError:
    pipe_model2 = None

teams_model2 = [
    "Sunrisers Hyderabad", "Mumbai Indians", "Royal Challengers Bangalore",
    "Kolkata Knight Riders", "Kings XI Punjab", "Chennai Super Kings",
    "Rajasthan Royals", "Delhi Capitals"
]

cities_model2 = [
    "Hyderabad", "Bangalore", "Mumbai", "Indore", "Kolkata", "Delhi",
    "Chandigarh", "Jaipur", "Chennai", "Cape Town", "Port Elizabeth",
    "Durban", "Centurion", "East London", "Johannesburg", "Kimberley",
    "Bloemfontein", "Ahmedabad", "Cuttack", "Nagpur", "Dharamsala",
    "Visakhapatnam", "Pune", "Raipur", "Ranchi", "Abu Dhabi",
    "Sharjah", "Mohali", "Bengaluru"
]

def result_model2(request):
    context = {
        'teams_model2': teams_model2,
        'cities_model2': cities_model2,
        'prediction_model2': None,
        'error_model2': None,
    }

    if request.method == "POST":
        if not pipe_model2:
            context['error_model2'] = "Model 2 file not loaded."
            return render(request, "ipl.html", context)

        try:
            batting_team = request.POST.get("batting_team")
            bowling_team = request.POST.get("bowling_team")
            city = request.POST.get("city")
            target = int(request.POST.get("target", 0))
            score = int(request.POST.get("score", 0))
            overs = float(request.POST.get("overs", 0))
            wickets = int(request.POST.get("wickets", 0))

            if overs == 0 or target == 0:
                context['error_model2'] = "Overs and Target must be greater than 0."
                return render(request, "ipl.html", context)

            runs_left = target - score
            balls_left = 120 - int(overs * 6)
            wickets_left = 10 - wickets
            crr = score / overs
            rrr = (runs_left * 6) / balls_left if balls_left > 0 else 0

            input_df = pd.DataFrame({
                'batting_team': [batting_team],
                'bowling_team': [bowling_team],
                'city': [city],
                'runs_left': [runs_left],
                'balls_left': [balls_left],
                'wickets': [wickets_left],
                'total_runs_x': [target],
                'crr': [crr],
                'rrr': [rrr]
            })

            prediction_proba = pipe_model2.predict_proba(input_df)[0]
            loss_prob = round(prediction_proba[0] * 100, 2)
            win_prob = round(prediction_proba[1] * 100, 2)

            if win_prob > loss_prob:
                winner = f"{batting_team} has a {win_prob}% chance of winning."
                loser = f"{bowling_team} has a {loss_prob}% chance of winning."
            else:
                winner = f"{bowling_team} has a {loss_prob}% chance of winning."
                loser = f"{batting_team} has a {win_prob}% chance of winning."

            context.update({
                'prediction_model2': True,
                'batting_team_model2': batting_team,
                'bowling_team_model2': bowling_team,
                'win_prob_model2': win_prob,
                'loss_prob_model2': loss_prob,
                'winner_msg_model2': winner,
                'loser_msg_model2': loser
            })

        except Exception as e:
            context['error_model2'] = f"An error occurred: {str(e)}"

    return render(request, "ipl.html", context)



'''chatbot'''

NGROK_URL = "https://pet-snapper-happy.ngrok-free.app/call_llm/"

def proxy_llm(request):
    statement = request.GET.get("statement", "")
    if not statement:
        return JsonResponse({"error": "Missing 'statement' parameter"}, status=400)
    

    try:
        response = requests.get(f"{NGROK_URL}?statement={statement}", timeout=10)
        response.raise_for_status()  

        return JsonResponse(response.json())  

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": "Failed to fetch data", "details": str(e)}, status=500)


def ask_ai_page(request):
    """Render the IPL page with LLM response."""
    statement = request.GET.get("statement", "Predict IPL Score") 
    print("in view.py")

    return render(request, "ask_ai.html", {"llm_result": "result from view.py"}) 




'''feedback'''
def feedback(request):
    if request.method == 'POST':
        name = request.POST.get("name")
        email = request.POST.get("email")
        feed = request.POST.get("feed")

        feedbacks = Feedback.objects.create(name=name, email=email, feed=feed)
        feedbacks.save()
        
        return redirect('feedback')  
    return render(request, 'feedback.html')


def feedback_view(request):
    newfeed = Feedback.objects.all()
    print(newfeed)
    return render(request, 'home.html', {'feedbacks': newfeed})


''' for teams and player '''

def team_list(request):
    teams = Team.objects.all()
    return render(request, 'team_list.html', {'teams': teams})

def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    players = team.players.all() 
    return render(request, 'team_detail.html', {'team': team, 'players': players})

def player_list(request):
    players = Player.objects.all()
    return render(request, 'player_list.html', {'players': players})

def player_detail(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    stats = player.stats.all()  
    return render(request, 'player_detail.html', {'player': player, 'stats': stats})


''' upcoming matches '''
def upcoming(request):
    return render(request,"upcoming.html")


'''articles'''
def articles(request):
    return render(request,"articles.html")


'''products'''
def product(request):
    return render(request,"products.html")