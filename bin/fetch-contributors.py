from pygithub3 import Github
from pprint import pprint
import sys
import json
import operator

atomix_stack = ['atomix', 'copycat', 'catalyst']

gh = Github(login=sys.argv[1], password=sys.argv[2])

def delete_keys(dic, keys):
  for key in dic.keys():
    if key in keys:
      del dic[key]

def retain_keys(dic, valid_keys):
  return dict(zip(valid_keys, [dic[k] for k in valid_keys]))

def get_user(login):
  user = gh.users.get(login)
  valid_keys = ["name"]
  return retain_keys(user.__dict__, valid_keys)

# Returns all contributors sorted by number of contributions
def get_users(repos, valid_keys, fetcher):
  result = dict()
  for repo in repos:
    contributors = fetcher(repo)
    for page in contributors:
        for c in page:
          user = retain_keys(c.__dict__, valid_keys)
          result[user['login']] = user
  for user in result.values():
    user.update(get_user(user['login']))
  return result

contributors = get_users(atomix_stack, ["login", "avatar_url", "html_url", "contributions"], 
  lambda repo: gh.repos.list_contributors(user='atomix', repo = repo))
committers = get_users(atomix_stack, ["login", "avatar_url", "html_url"],
  lambda repo: gh.repos.collaborators.list(user='atomix', repo = repo))

# Add contributions to contributors
for committer in committers.values():
  committer['contributions'] = contributors[committer['login']]['contributions']

# Remove committers from contributors
delete_keys(contributors, committers.keys())

contributors = sorted(contributors.values(), key=lambda k: k['contributions'], reverse = True)
committers = sorted(committers.values(), key=lambda k: k['contributions'], reverse = True)

with open('committers.json', 'w') as outfile:
    json.dump(committers, outfile)
with open('contributors.json', 'w') as outfile:
    json.dump(contributors, outfile)