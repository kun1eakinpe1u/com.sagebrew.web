import os


branch = os.environ.get("CIRCLE_BRANCH", None)
circle_ci = os.environ.get("CIRCLECI", "false").lower()
if circle_ci == "false":
    circle_ci = False
if circle_ci == "true":
    circle_ci = True

if circle_ci is True:
    from test import *
elif branch is None:
    from development import *
elif "dev" in branch:
    from development import *
elif branch == "staging":
    from staging import *
elif branch == "master":
    from production import *
else:
    from production import *
