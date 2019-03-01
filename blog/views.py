from django.shortcuts import render, get_object_or_404
from .models import Post
from django.utils import timezone
from .forms import PostForm
from django.shortcuts import redirect
import json
from watson_developer_cloud import ToneAnalyzerV3
from watson_developer_cloud.tone_analyzer_v3 import ToneInput
from watson_developer_cloud import LanguageTranslatorV3


language_translator = LanguageTranslatorV3(
    version='2018-05-01',
    iam_apikey='ZrxokU3Cg_vKweP0hSKml_TPxpwJNe4hpKoxgAv0jcoc')

service = ToneAnalyzerV3(
    ## url is optional, and defaults to the URL below. Use the correct URL for your region.
    # url='https://gateway.watsonplatform.net/tone-analyzer/api',
    username='b714bb0a-1d64-4dac-a2a5-d1f063c607c9',
    password='Ejk4l5viITJU',
    version='2017-09-26')


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')

    for post in posts:
        posting = post.text

        translation = language_translator.translate(
            text= post.text, model_id='en-es').get_result()
        obj = (json.dumps(translation, indent=2, ensure_ascii=False))
        print(obj)
        obj2 = json.loads(obj)
        post.obj2 = obj2['translations'][0]['translation']
        post.w_count = obj2['word_count']
        post.c_count = obj2['character_count']




        tone = service.tone({'text': posting}, 'application/json').get_result()
        objtone = (json.dumps(tone, indent=2, ensure_ascii=False))
        objtone2 = json.loads(objtone)

        post.name1 = objtone2['document_tone']['tones'][0]['tone_name']
        post.name2 = objtone2['document_tone']['tones'][1]['tone_name']

        post.score1 = objtone2['document_tone']['tones'][0]['score']
        post.score2 = objtone2['document_tone']['tones'][1]['score']


        #tone2 = str(tone)
        #post.tone3 = (tone2[1:500])
        #print(post.tone3)

    return render(request, 'blog/post_list.html', {'posts': posts})




def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})
