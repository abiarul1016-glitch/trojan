import random

from django.shortcuts import render


# Create your views here.
def index(request):
    """
    Returns the main page of the application.
    """

    phrases = [
        "cuz shit*y teachers exist.",
        "cuz some teachers are sh*t.",
        "cuz (some) teachers are sh*t.",
        "for all the shit*y teachers.",
    ]
    hero_phrase = random.choice(phrases)

    return render(request, "trojan/index.html", {"hero_phrase": hero_phrase})


def directory(request):
    return render(request, "trojan/directory.html")


def course(request):
    """
    Displays the course details for a requested course based on its ___.
    """

    pass


def search_course(request):
    """
    Presents a search view for courses, and redirects the user to their desired course.
    Also has suggested completions.
    """

    pass
