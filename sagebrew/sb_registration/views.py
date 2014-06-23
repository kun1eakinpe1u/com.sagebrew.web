import os

from django.conf import settings
from uuid import uuid1
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from plebs.neo_models import Pleb, TopicCategory, SBTopic, Address

from .forms import (ProfileInfoForm, AddressInfoForm, InterestForm, ProfilePictureForm,
                    ProfilePageForm, AddressChoiceForm)
from .utils import (validate_address, generate_interests_tuple, upload_image,
                    compare_address, generate_address_tuple, determine_senators,
                    determine_reps)

@login_required
def profile_information(request):
    '''
    Creates both a ProfileInfoForm and AddressInfoForm which populates the
    fields with what the user enters. If this function gets a valid POST request it
    will update the pleb. It then validates the address, through smartystreets api,
    if the address is valid a Address neo_model is created and populated.
    '''
    profile_information_form = ProfileInfoForm(request.POST or None)
    address_information_form = AddressInfoForm(request.POST or None)
    address_selection_form = AddressChoiceForm(request.POST or None)
    address_selection = "no_selection"

    try:
        citizen = Pleb.index.get(email=request.user.email)
    except Pleb.DoesNotExist:
        return redirect("404_Error")
    if profile_information_form.is_valid():
        citizen.date_of_birth = profile_information_form.cleaned_data[
            "date_of_birth"]
        citizen.home_town = profile_information_form.cleaned_data["home_town"]
        citizen.high_school = profile_information_form.cleaned_data[
            "high_school"]
        citizen.college = profile_information_form.cleaned_data["college"]
        citizen.employer = profile_information_form.cleaned_data["employer"]
        citizen.save()

    if address_information_form.is_valid():
        address_clean = address_information_form.cleaned_data
        address_info = validate_address(address_clean)
        addresses_returned = len(address_info)
        address_tuple = generate_address_tuple(address_info)

        # Not doing 0 cause already done with address_information_form
        if(addresses_returned == 1):
            if compare_address(address_info[0], address_clean):
                address = Address(**address_info[0])
                address.save()
                address.address.connect(citizen)
                citizen.completed_profile_info = True
                citizen.address.connect(address)
                citizen.save()
                return redirect('interests')
            else:
                address_selection_form.fields['address_options'].choices = address_tuple
                address_selection_form.fields['address_options'].required = True
                address_selection = "selection"
        elif(addresses_returned > 1):
            # Choices need to be populated prior to is_valid call to ensure
            # that the form validates against the correct values
            # We also are able ot keep this in the same location because
            # we hid the other address form but it keeps the same values as
            # previously entered. This enables us to get the same results
            # back from smarty streets and validate those choices again then
            # select the one that the user selected.
            address_selection_form.fields['address_options'].choices = address_tuple
            address_selection_form.fields['address_options'].required = True
            address_selection = "selection"

        if(address_selection == "selection"):
            if(address_selection_form.is_valid()):
                # address_selection_form.cleaned_data["address_options"] returns
                # as a string so have to convert it to an int

                # TODO
                # Need to use a hash to verify the same address string is being
                # used instead of an int. That way if smarty streets passes back
                # the addresses in a different order we can use the same address
                # we provided the user previously based on the previous
                # smarty streets ordering.
                address = Address(**address_info[int(
                        address_selection_form.cleaned_data["address_options"])])
                address.save()
                address.address.connect(citizen)
                citizen.completed_profile_info = True
                citizen.address.connect(address)
                citizen.save()
                return redirect('interests')



    return render(request, 'profile_info.html',
                    {'profile_information_form': profile_information_form,
                    'address_information_form': address_information_form,
                    'address_selection': address_selection,
                    'address_choice_form': address_selection_form})

@login_required()
def interests(request):
    '''
    The interests view creates an InterestForm populates the topics that
    a user can choose from and if a POST request is passed then the function
    checks the validity of the arguments POSTed. If the form is valid then
    the given topics and categories are associated with the logged in user.

    :param request:
    :return: HttpResponse
    '''
    interest_form = InterestForm(request.POST or None)
    choices_tuple = generate_interests_tuple()
    interest_form.fields["specific_interests"].choices = choices_tuple

    if interest_form.is_valid():
        for item in interest_form.cleaned_data:
            if(interest_form.cleaned_data[item] and
                    item != "specific_interests"):
                try:
                    citizen = Pleb.index.get(email=request.user.email)
                    # TODO profile page profile picture
                    if citizen.completed_profile_info:
                        return redirect('profile_picture')
                except Pleb.DoesNotExist:
                    redirect("404_Error")
                try:
                    category_object = TopicCategory.index.get(
                        title=item.capitalize())
                    for topic in category_object.sb_topics.all():
                        #citizen.sb_topics.connect(topic)
                        pass
                    # citizen.topic_category.connect(category_object)
                except TopicCategory.DoesNotExist:
                    redirect("404_Error")

        for topic in interest_form.cleaned_data["specific_interests"]:
            try:
                interest_object = SBTopic.index.get(title=topic)
            except SBTopic.DoesNotExist:
                redirect("404_Error")
            # citizen.sb_topics.connect(interest_object)
        return redirect('profile_picture')

    return render(request, 'interests.html', {'interest_form': interest_form})


@login_required()
def profile_picture(request):
    if request.method == 'POST':
        profile_picture_form = ProfilePictureForm(request.POST, request.FILES)
        if profile_picture_form.is_valid():
            try:
                citizen = Pleb.index.get(email=request.user.email)
                #if citizen.completed_profile_info:
                #    return redirect('profile_page')
                #print citizen.profile_pic
            except Pleb.DoesNotExist:
                print("How did you even get here!?")
                return render(request, 'profile_picture.html', {'profile_picture_form': profile_picture_form})
            image_uuid = uuid1()
            data = request.FILES['picture']
            temp_file = '%s%s.jpeg' % (settings.TEMP_FILES, image_uuid)
            with open(temp_file, 'wb+') as destination:
                for chunk in data.chunks():
                    destination.write(chunk)
            citizen.profile_pic = upload_image('profile_pictures', image_uuid)
            citizen.save()
            return redirect('profile_page')
    else:
        profile_picture_form = ProfilePictureForm()
    return render(request, 'profile_picture.html', {'profile_picture_form': profile_picture_form})

@login_required()
def profile_page(request):#who is your sen
    profile_page_form = ProfilePageForm(request.GET or None)
    citizen = Pleb.index.get(email=request.user.email)
    print citizen.address.congressional_district
    determine_senators(citizen.address)
    determine_reps(citizen.address)

    return render(request, 'profile_page.html', {'profile_page_form': profile_page_form,
                                                 'pleb_info': citizen})

