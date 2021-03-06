from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy
from django.http import HttpResponse
from . import forms, models
from django.views.generic import (TemplateView, CreateView, ListView, UpdateView, 
                                    DetailView, DeleteView, FormView)
from django.http import JsonResponse
from django.core import serializers
import json
from BlockChain.contract_interface import web3 
from BlockChain import contract_interface as ci
# Create your views here.


contractLocation=r'BlockChain\compiled\contracts\contract.json'
ContractDetail=ci.readContractInfo(contractLocation)
#remove Ones Database Implemented
#Tempory Variables
Contract='temp'
Funder='funder'
fundSeeker='FundSeeker'
class PostListView(ListView):
    model = models.Post
    def get_queryset(self):
        return models.Post.objects.order_by('-published_date')

class PostDetailView(DetailView):
    model = models.Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['add_funds_form'] = forms.AddFunds()
        context['add_comment_form'] = forms.CommentForm()
        return context
    

class PostDeleteView(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('accounts:login')
    success_url = reverse_lazy('post_list')
    model = models.Post

class PostCreateView(LoginRequiredMixin, CreateView):
    form_class = forms.PostForm
    model = models.Post
    login_url = reverse_lazy('accounts:login')
    success_url = reverse_lazy('projects:post_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UpdateView):
    login_url = reverse_lazy('accounts:login')
    model = models.Post
    success_url = models
    form_class = forms.PostForm

class UserPostView(LoginRequiredMixin,  ListView):
    login_url = reverse_lazy('accounts:login')
    model = models.Post
    template_name = 'projects/user_post_list.html'

    def get_queryset(self):
        return models.Post.objects.filter(author = self.request.user).order_by('-published_date')




@login_required(login_url=reverse_lazy('accounts:login'))
def put_comment_on_post(request,pk):
    post = get_object_or_404(models.Post, pk=pk)
    if request.method == "POST":
        form = forms.CommentForm(request.POST)
        model = models.Comment(request.POST)    
        if form.is_valid():
            model = form.save(commit=False)
            model.post = post
            model.author = request.user
            model.save()
            return redirect('projects:post_detail', pk=post.pk)
            # Add redirect in above code
    else:
        form = forms.CommentForm()
    
    return render(request, 'projects/comment_form.html', context={'form': form})

@login_required(login_url=reverse_lazy('accounts:login'))
def add_funds_view(request, pk):
    add_funds_form = forms.AddFunds()
    add_comment_form = forms.CommentForm()
    if request.method == 'POST':
        form = forms.AddFunds(request.POST)
        form2 = forms.CommentForm(request.POST)
        model = models.Comment(request.POST)
        if form.is_valid():
            value = form.cleaned_data['amount']
            post = get_object_or_404(models.Post, pk=pk)
            post.add_funds(value)
            post.save()
            model = form2.save(commit=False)
            model.post = post
            model.author = request.user
            model.save()
            return redirect('projects:post_detail', pk=pk)


# TODO
@csrf_exempt
def checkconnectivity(request):
    return JsonResponse({"response":web3.isConnected()})
@csrf_exempt
def CreateCampaign(request):
    js = request.read()
    js = json.loads(js)
    name = js['name']
    account = js['account']
    global fundSeeker
    fundSeeker = ci.CreateFundSeeker(name, account)
    #TODO ADD Contract ID returned below to database and make code to recover it
    global Contract
    Contract=ci.createContract(ContractDetail,"Campaign",fundSeeker.getAcc())
    return JsonResponse({'response':True})
@csrf_exempt
def CreateFunderForBucket(request):
    js = request.read()
    js = json.loads(js)
    name = js['name']
    account = js['account']
    global Funder 
    Funder = ci.CreateFunder(name,acc=account)
    print(Funder.getAcc())
    print(Contract)
    user=ci.registerFunder(Contract,Funder)
    return JsonResponse({'response':True})

@csrf_exempt
def registerFundSeeker(request):
    tx=ci.registerFundSeeker(Contract,funder=Funder,fund_seeker=fundSeeker)
    return JsonResponse({'response':True,'description':str(tx)})

@csrf_exempt
def getFundSeeker(request):
    tx=ci.getFundSeeker(Contract,fundSeeker)
    return JsonResponse({'response':True,'description':str(tx)})

@csrf_exempt
def sendMoneyToFundSeeker(request):
    [tx,val]=ci.DonateMoney(Contract,Funder,'10000')
    return JsonResponse({'response':True,'tx':str(tx),'val':val})

@csrf_exempt
def startVotingFor(request):
    ci.startVotingFor(Contract,Funder.getAcc(),fundSeeker.getAcc())
    return JsonResponse({'response':True})

@csrf_exempt
def endVotingFor(request):
    ci.endVotingFor(Contract,Funder.getAcc(),fundSeeker.getAcc())
    return JsonResponse({'response':True})

@csrf_exempt
def vote(request):
    vote=request.read()
    js = json.loads(js)
    vote = js['vote']
    ci.voteFor(Contract,fundSeeker,Funder,vote)

@csrf_exempt
def isAllowedToWithDraw(request):
    p=ci.isAllowedToWithDraw(Contract,fundSeeker,fundSeeker)
    return JsonResponse({'response':True,'body':str(p)})

@csrf_exempt
def getCurrentFundingStageFor(request):
    p=ci.getCurrentFundingStageFor(Contract,Funder,fundSeeker)
    return p
