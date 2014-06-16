from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class InterestForm(forms.Form):
    select_all = forms.BooleanField(
        label = "I like a bit of everything",
        required = False,
        help_text= ""
    )

    fiscal = forms.BooleanField(
        label = "Fiscal",
        required = False,
        help_text = '''
            Issues involving the Economy,
            matters of taxation, government spending,
            importing/exporting, the private sector,
            wall street etc
        '''
    )

    foreign_policy = forms.BooleanField(
        label = "Foreign Policy",
        required = False,
        help_text = '''
            Issues involving the interaction between the Federal Government
            and Governments of other states and nations.
        '''
    )

    social = forms.BooleanField(
        label = "Social",
        required = False,
        help_text = '''
            Issues that effect the advancement of society:
            Abortion, LGBT rights, social injustice, Gun Control, personal
            freedoms etc
        '''
    )

    education = forms.BooleanField(
        label = "Education",
        required = False,
        help_text = '''
            Issues involving the education of the nation's including
            educational reform, policy changes, curriculum changes, the arts
            etc.
        '''
    )

    science = forms.BooleanField(
        label = "Science",
        required = False,
        help_text = '''
            Issues rooted in science such as: climate change, stem cell
            research, product testing, genetic engineering etc.
        '''
    )

    environment = forms.BooleanField(
        label = "Environment",
        required = False,
        help_text = '''
            Issues that deal with the national and global climate such as:
            carbon pollution, other forms of chemical air pollution,
            water pollution, sewage dumping, plastics and recycling, trash
            and cleanup etc.
        '''
    )

    drugs = forms.BooleanField(
        label = "Drugs",
        required = False,
        help_text = '''
            Issues that deal with prescription drugs,
            recreational drugs, drug laws, drug penalties,
            drug psychology, etc.
        '''
    )

    agriculture = forms.BooleanField(
        label = "Agriculture",
        required = False,
        help_text = '''
            Issues that look at agricultural law, practice, patent law,
            mono-cropping, agricultural reform etc.
        '''
    )

    defense = forms.BooleanField(
        label = "Defense",
        required = False,
        help_text = '''
            Issues involving the United States Defense program, such as:
            defense spending, defense spending allocation, weapons research,
            military, military benefits and healthcare, veteran affairs,
            wartime strategy and treaty etc.
        '''
    )

    energy = forms.BooleanField(
        label = "Energy",
        required = False,
        help_text = '''
            Issues involving alternative energy research, energy emissions
            control, current energy goals and practice, etc.
        '''
    )

    health = forms.BooleanField(
        label = "Health",
        required = False,
        help_text = '''
            Issues involving general healthcare, the ACA, insurance,
            health research, the FDA, etc.
        '''
    )

    space = forms.BooleanField(
        label = "Space",
        required = False,
        help_text = '''
            Issues that deal with the science of space travel,
            space exploration, astrophysics, astronomy, asteroid mining, etc.
        '''
    )

    specific_interests = forms.MultipleChoiceField(
        label = "I only care about:",
        choices = [],
        required = False,
    )


    def __init__(self, *args, **kwargs):
        super(InterestForm, self).__init__(*args, **kwargs)

'''
If you want to adjust field attributes programatically without overwritting
everything use something like the following under super(...) in
the __init__ method

for field in self.fields:
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update({'class':'has-popover',
                'data-content':help_text, 'data-placement':'right',
                'data-container':'body'})
'''