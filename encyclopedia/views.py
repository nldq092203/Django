from django.shortcuts import render
from . import util
from markdown import markdown
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from random import randint

# from bs4 import BeautifulSoup


def index(request):
    if request.method != "POST":
        # print(util.list_entries())
        return render(
            request, "encyclopedia/index.html", {"entries": util.list_entries()}
        )
    return search(request)


def entry(request, title):
    if request.method != "POST":
        markdownContent = util.get_entry(title)
        if markdownContent:
            htmlContent = markdown(markdownContent)

            # # Parse HTML content
            # soup = BeautifulSoup(htmlContent, 'html.parser')

            # # Find all <a> tags
            # allLinks = soup.find_all('a')

            # # Process the links
            # for link in allLinks:

            return render(
                request,
                "encyclopedia/entry.html",
                {"htmlContent": htmlContent, "title": title},
            )
        else:
            return render(request, "encyclopedia/error.html")
    return search(request)


def search(request):
    if request.method == "POST":
        query = request.POST.get("q").rstrip()
        entries = util.list_entries()
        entriesLower = [entry.lower() for entry in entries]
        print(entriesLower)
        for i in range(len(entries)):
            if query.lower() == entriesLower[i]:
            # return render(
            #     request,
            #     "encyclopedia/entry.html",
            #     {"htmlContent": markdown(util.get_entry(query)), "title": query},
            # )
                return HttpResponseRedirect(reverse("entry", kwargs={"title": entries[i]}))

        
        listEntries = []
        for entry in entries:
            if query.lower() in entry.lower():
                listEntries.append(entry)
        if listEntries:
            return render(
                request, "encyclopedia/index.html", {"entries": listEntries}
            )
        else:
            return render(request, "encyclopedia/error.html")


class NewPage(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(label="Content", widget=forms.Textarea)


def checkExist(title):
    entries = [entry.lower() for entry in util.list_entries()]
    if title.lower() in entries:
        return True
    return False


def create(request):
    if request.method == "POST":
        form = NewPage(request.POST)
        if form.is_valid():
            form = form.cleaned_data
            if checkExist(form["title"]):
                return HttpResponse("The entry has existed")
            else:
                util.save_entry(form["title"], form["content"])
                return HttpResponseRedirect(
                    reverse("entry", kwargs={"title": form["title"]})
                )
    return render(request, "encyclopedia/create.html", {"form": NewPage()})


def edit(request, title):
    if request.method != "POST":
        markdownContent = util.get_entry(title)
        return render(
            request,
            "encyclopedia/edit.html",
            {"title": title, "htmlContent": markdownContent},
        )
    else:
        form = request.POST
        print(form["content"])
        util.save_entry(title, form["content"])
        return HttpResponseRedirect(reverse("entry", kwargs={"title" : title}))

def random(request):
    listEntries = util.list_entries()
    index = randint(0, len(listEntries) - 1)
    entry = listEntries[index]
    return HttpResponseRedirect(reverse("entry", kwargs={"title" : entry}))
