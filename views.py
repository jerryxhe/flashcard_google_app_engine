import string
import logging
from django.shortcuts import render_to_response
from django.http import HttpResponse
#from django.contrib import admin
from google.appengine.api import users
from google.appengine.ext import db
from django.http import HttpResponseRedirect
from models import FlashCard, TexRender, DisplayCard, Note, Reference
from appengine_django.models import BaseModel
from django import forms
from conversion import *
from google.appengine.api.urlfetch import fetch

s = {}; # global index for latex characters NEEDS to be stored in datastore!!!

class FlashCardForm(db.djangoforms.ModelForm):
    question = forms.CharField(widget=forms.Textarea(attrs={'rows':'10', 'cols':'32'}))
    answer = forms.CharField(widget=forms.Textarea(attrs={'rows':'10', 'cols':'32'}))   
    #ref = forms.ChoiceField(choices=choices, required=False)
    class Meta:
        model = FlashCard
        exclude = ['mtime', 'user', 'display'] 

class ReferenceForm(db.djangoforms.ModelForm):
    title = forms.CharField(widget=forms.Textarea(attrs={'cols':'30'}))
    subtitle = forms.CharField(required=False, widget=forms.Textarea(attrs={'cols':'20'}))
    authors = forms.CharField()
    picURL = forms.URLField(required=False)
    class Meta:
        model = Reference
        exclude = ['pic', 'tags', 'authors']

class NoteForm(db.djangoforms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={'rows':'20', 'cols':'28'}))   
    class Meta:
        model = Note
        exclude = ['mtime', 'user', 'display']
        
def note(request):
    return render_to_response('add.html', 
                {'form':NoteForm(),
                'login_url': users.create_login_url('/add'),
                'user': users.get_current_user(),
            'logout_url': users.create_logout_url('/add')})

def add(request):
    return render_to_response('add.html', 
                {'form':FlashCardForm(),
                'login_url': users.create_login_url('/add'),
                'user': users.get_current_user(),
            'logout_url': users.create_logout_url('/add')})

def addref(request):
    return render_to_response('add.html', 
                {'form':ReferenceForm(),
                'login_url': users.create_login_url('/add'),
                'user': users.get_current_user(),
            'logout_url': users.create_logout_url('/add')})


def replaceTex(text):
    texSnippits = re.compile(r'([$](\s)?(\\(fs)?(?P<size>\d))?(?P<tex>.*?)[$])')
    placeID = []
    text = plaintext2html(text) # handle newlines 
    text = tex2html(text)  # handle \emph type control sequences
    logging.info("parsing HTML\n\n" + text) 
    for elem in texSnippits.finditer(text):
        tex = elem.group('tex').strip()
        d = elem.group('size')
        if d: fs = int(d) > 7 and r'\fs7' or r'\fs' + str(d)
        else: fs = r'\fs5'
        etex = fs + r'%20' + tex  # tex command with font size in front
        etex = etex.replace(" ", r"%20")        
        if (not s.has_key(etex)) and (TexRender.get_by_key_name(etex) is None):
            logging.info("tex source is " +  etex)
            photo = fetch(r'http://math.harvard.edu/cgi-bin/mimetex.cgi?'+ etex)
            logging.info("status code is " + unicode(photo.status_code))
            logging.info("headers is " + unicode(photo.headers))
            texGIF = TexRender(pic = db.Blob(photo.content), key_name=etex)
            texGIF.put()
            s[etex] = texGIF.key()
        placeID.append((elem.start(),elem.end(), etex))    
    if len(placeID)==0:
        return text
    finalHTML = []
    last = 0 
    for i in range(len(placeID)):
        (start, end, etex) = placeID[i]
        finalHTML.append(text[last:start])
        imageID = s.has_key(etex) and unicode(s[etex]) or unicode(TexRender.get_by_key_name(etex).key())
        finalHTML.append(r"<img src='/image/"+imageID+
                         r"/' alt ='%s'> </img>" % etex)
        last = end
    finalHTML.append(text[last:])
    return "".join(finalHTML)


def post(request):
    logging.info(unicode(request.POST))
    if request.POST.has_key("text"):
        form = NoteForm(request.POST)
        if not form.is_valid():
            return render_to_response('add.html', {'form': form, 
                'login_url': users.create_login_url('/add'),
                    'user': users.get_current_user(),
                'logout_url': users.create_logout_url('/add')})
        note = form.save(commit=False)
        note.user = users.get_current_user()
        display = DisplayCard(question= replaceTex(note.text))
        display.put()
        note.display = display.key()
        note.put()
        return HttpResponseRedirect('/')
        
    if request.POST.has_key("authors"):
        form = ReferenceForm(request.POST)
        if not form.is_valid():
            return render_to_response('add.html', {'form': form, 
                'login_url': users.create_login_url('/add'),
                    'user': users.get_current_user(),
                'logout_url': users.create_logout_url('/add')})
        ref = form.save(commit=False)
        ref.authors = map(string.strip, request.POST["authors"].split("|"))
        if request.POST["picURL"]:
            photo = fetch(request.POST["picURL"])
            keyname = ref.subtitle and ref.title + u" - " + ref.subtitle or ref.title
            bCover = TexRender(pic = photo.content, key_name = keyname)
            bCover.put()
            ref.pic = bCover.key()
        ref.put()
        return HttpResponseRedirect('/')
    form = FlashCardForm(request.POST)
    if not form.is_valid():
        return render_to_response('add.html', {'form': form, 
            'login_url': users.create_login_url('/add'),
                'user': users.get_current_user(),
            'logout_url': users.create_logout_url('/add')})
    flash = form.save(commit=False)
    flash.user = users.get_current_user()
    display = DisplayCard(question= replaceTex(flash.question), 
                           answer = replaceTex(flash.answer) 
                           )
    display.put()
    flash.display = display.key()
    flash.put()
    return HttpResponseRedirect('/')

def ssearch(request, key_word):
    query1 = FlashCard.all().search(key_word).order("-mtime")
    query2 = Note.all().search(key_word).order("-mtime")
    return render_to_response('quiz.html', {'cards': query1.run(),
                                                'notes': query2.run()})

def all(request):
    query = FlashCard.all().order("-mtime")
    return render_to_response('quiz.html', {'cards': query.run()})

def search(request):
    class SearchForm(forms.Form):
        keyword = forms.CharField()
    if request.POST:
        form = SearchForm(request.POST)
        keywords = form.data['keyword']
        query1 = FlashCard.all().search(keywords).order("-mtime")
        query2 = Note.all().search(keywords).order("-mtime")
        return render_to_response('display.html', {'cards': query1.run(),
                                                     'notes': query2.run()})
    else:
        return render_to_response('search.html', {'page':SearchForm()})


def image(request, img_id):
    photo = TexRender.get(img_id)
    if photo:
        return HttpResponse(photo.pic)
    else:
        return HttpResponse("NO IMAGE")
        

def books(request):
    query = Reference.all()
    imgIDs = [ref.pic.key() for ref in query.run() if ref.pic is not None]
    return render_to_response('library.html', {'images':imgIDs})
    
    

def download(request):
    query1 = FlashCard.all()
    query2 = Note.all()
    query3 = Reference.all()
    xmlcards = [card.to_xml() for card in query1.run()]
    xmlnotes = [note.to_xml() for note in query2.run()]
    xmlrefs = [ref.to_xml() for ref in query3.run()]
    return render_to_response('download.xml', 
                {'xmlcards': xmlcards,
                 'xmlnotes': xmlnotes,
                 'xmlrefs': xmlrefs}
            )
            
