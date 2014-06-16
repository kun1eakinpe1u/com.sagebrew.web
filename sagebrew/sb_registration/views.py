from django.shortcuts import render, redirect
from django.http import HttpResponseServerError

from plebs.neo_models import Pleb, TopicCategory, SBTopic

from .forms import InterestForm
from .utils import generate_interests_tuple


def profile_information(request):
    profile_information_form = ProfileInfoForm(request.POST or None)
    address_information_form = AddressInfo(request.POST or None)
    '''if profile_information_form.is_valid():
        for item in profile_information_form.cleaned_data:
            if(profile_information_form.cleaned_data[item]):
                try:
                    citizen = Pleb.index.get(sb_email=request.user.email)
                except Pleb.DoesNotExist:
                    raise HttpResponseServerError
                #try:
                    #profile_object ='''

    return render(request, 'profile_info.html',
                    {'profile_information_form':None})


def interests(request):
    interest_form = InterestForm(request.POST or None)

    choices_tuple = generate_interests_tuple()
    interest_form.fields["specific_interests"].choices = choices_tuple

    if interest_form.is_valid():
        for item in interest_form.cleaned_data:
            if(interest_form.cleaned_data[item] and
                       item != "specific_interests"):
                try:
                    citizen = Pleb.index.get(email=request.user.email)
                except Pleb.DoesNotExist:
                    # return HttpResponseServerError('<h1>Server Error (500)</h1>')
                    print "Pleb does not exist"
                try:
                    print item
                    category_object = TopicCategory.index.get(
                        title=item.capitalize())
                    for topic in category_object.sb_topics.all():
                        #citizen.sb_topics.connect(topic)
                        pass
                    # citizen.topic_category.connect(category_object)
                except TopicCategory.DoesNotExist:
                    # return HttpResponseServerError('<h1>Server Error (500)</h1>')
                    print "Topic cat does not exist"

        for topic in interest_form.cleaned_data["specific_interests"]:
            try:
                interest_object = SBTopic.index.get(title=topic)
                print interest_object.title
            except SBTopic.DoesNotExist:
                # return HttpResponseServerError('<h1>Server Error (500)</h1>')
                print "Topic cat does not exist"
            # citizen.sb_topics.connect(interest_object)
        return redirect('invite_friends')
    else:
        print interest_form.errors

    return render(request, 'interests.html', {'interest_form': interest_form})


def invite_friends(request):
    return render(request, 'invite_friends.html', {"here": None})