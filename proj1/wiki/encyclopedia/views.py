from django.urls import reverse
from django.shortcuts import redirect, render

import random
from markdown2 import markdown

from . import util
from .forms import NewPageForm, EditForm


def index(request):
    """ Homepage for wiki app. Displays list of entries in wiki. """
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def contents(request, title):
    """ Display the contents of an encyclopedia entry. """
    contents = util.get_entry(title)
    # Error if entry does not exist
    if contents is None:
        context = {
            "message": f"<b><i>{title}</i></b> is not found in encylopedia."
        }
        return render(request, "encyclopedia/error.html", context)

    # Load entry
    else:
        contents = util.get_entry(title)
        # Convert markdown to html
        contents_html = markdown(contents)

        return render(request, "encyclopedia/contents.html", {
            "title": title,
            "contents": contents_html
        })


def search(request):
    """
    Process search query in searchbar.
    This view is only called from searchbar.
    If query matches name of entry, redirect to entry.
    Otherwise display a list of results which contains the query as a substring.
    Click on any entry name on results page to navigate to that entry's page.
    """
    # User submitted search query
    if request.method == "GET":
        # Access search query
        q = request.GET["q"]

        # If query matches name of entry, redirect to entry
        if util.get_entry(q) is not None:
            return contents(request, q)

        # If no match, display a list of results which contains the query as a substring
        results = [entry for entry in util.list_entries() if q.lower() in entry.lower()]
        return render(request, "encyclopedia/search.html", {
            "query": q,
            "results": results
        })


def create(request):
    """ Create a new page in wiki. """
    # User submitted form data
    if request.method == "POST":
        # Populate form
        form = NewPageForm(request.POST)

        # Only process valid form
        if form.is_valid():
            title = form.cleaned_data["title"]
            contents = form.cleaned_data["contents"]
            entries = util.list_entries()
            
            # Error if title already exists
            if title.lower() in [entry.lower() for entry in entries]:
                context = {
                    "message": f"Entry already exists with title: <a href={title.lower()}>{title}</a>"
                }
                return render(request, "encyclopedia/error.html", context)
            
            # Save entry to disk and redirect user to new page
            else:
                util.save_entry(title, contents)
                return redirect("contents", title=title)

        # Return the invalid populated form to user
        else:
            return render(request, "encyclopedia/create.html", {"form": form})

    # User accessed page via GET (as by clicking on link)
    # Load empty form
    else:
        return render(request, "encyclopedia/create.html", {"form": NewPageForm()})


def edit(request, title):
    """
    Edit a current page in wiki.
    Link to this view from each contents page.
    Form to edit page contains a single textarea that is populated 
    with existing markdown content.
    """
    # User submitted form
    if request.method == "POST":
        # Populate form
        form = EditForm(request.POST)

        if form.is_valid():
            contents = form.cleaned_data["contents"]
            util.save_entry(title, contents)
            return redirect("contents", title=title)

        else:
            return render(request, "encyclopedia/edit.html", {
                "title": title,
                "form": form
            })

    # User accessed page via GET
    # Load form pre-populated with current page's markdown content
    else:
        contents = util.get_entry(title)
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "form": EditForm(initial={"contents": contents})
        })


def random_page(request):
    """ Redirects to a random page in encyclopedia. """
    entries = util.list_entries()
    page = random.choice(entries)
    return redirect("contents", title=page)
