from django.db.models import Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect, reverse
from .forms import CommentForm, PostForm
from Post.models import Post, Author, PostView
from marketing.models import Signup

def get_author(user):
    qs = Author.objects.filter(user=user)
    if qs.exists():
        return qs[0]
    return None

def search(request):
    queryset = Post.objects.all()
    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(overview__icontains=query)
        ).distinct()
    context = {
        'queryset' : queryset
    }
    return render(request, 'search.html', context)

def get_category_count():
    queryset = Post.objects.values('categories__title').annotate(Count('categories__title'))
    return queryset

def index(request):
    query = Post.objects.filter(featured=True)[0:3]
    latest = Post.objects.order_by('-timestamp')[0:3]

    if request.method == 'POST':
        email = request.POST['email']
        signup_email = Signup()
        signup_email.email = email
        signup_email.save()
    context = {
        'object_list' : query,
        'latest' : latest
    }
    return render(request, 'index.html', context)

def blog(request):
    category_count = get_category_count()
    print(category_count)
    most_recent = Post.objects.order_by('-timestamp')[:3]
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 4)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        paginated_query = paginator.page(page)
    except PageNotAnInteger:
        paginated_query = paginator.page(1)
    except EmptyPage:
        paginated_query = paginator.page(paginator.num_pages)
    context = {
        'most_recent' : most_recent,
        'query' : paginated_query,
        'page_request_var' : page_request_var,
        'category_count' : category_count
    }
    return render(request, 'blog.html', context)

def post(request, id):
    most_recent = Post.objects.order_by('-timestamp')[0:3]
    postdetail = get_object_or_404(Post, id = id)
    PostView.objects.get_or_create(post=postdetail)
    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            #form.instance.user = request.user
            form.instance.post = postdetail
            form.save()
            return redirect(reverse("post-detail", kwargs={'id' : postdetail.id}))
        form = CommentForm()
        
    context = {
        'form' : form,
        'postdetail' : postdetail,
        'most_recent' : most_recent
    }
    return render(request, 'post.html', context)

def postCreate(request): 
    title = 'Create'
    form = PostForm(request.POST or None, request.FILES or None)
    author = get_author(request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse("post-detail", kwargs={'id' : form.instance.id}))
    context = {
        'title' : title,
        'form' : form
    }    
    return render(request, 'postform.html', context)

def postUpdate(request, id):
    title = 'Update'
    post = get_object_or_404(Post, id = id)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    author = get_author(request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse("post-detail", kwargs={'id' : form.instance.id}))
    context = {
        'title' : title,
        'form' : form
    }    
    return render(request, 'postform.html', context)

def postDelete(request, id):
    deletepost = get_object_or_404(Post, id = id)
    deletepost.delete()
    return redirect(reverse("post-list"))

def postDraft(request):
    draft = Post.objects.filter(featured=False)
    context = {
        'draft' : draft
    }
    return render(request, 'draft.html', context)