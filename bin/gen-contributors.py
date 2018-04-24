from pygithub3 import Github
import os
import sys
import yaml

DATA_DIR = os.path.join(os.path.dirname( __file__ ), '../_data')
ATOMIX_STACK = ['atomix', 'atomix-test', 'atomix-py', 'atomix-cli', 'atomix.github.io']

gh = Github(token=sys.argv[1])

def delete_keys(dic, keys):
  for key in dic.keys():
    if key in keys:
      del dic[key]

def retain_keys(dic, valid_keys):
  return dict(zip(valid_keys, [dic[k] for k in valid_keys]))

def get_user(login):
  user = gh.users.get(login)
  valid_keys = ["name", "blog"]
  user = retain_keys(user.__dict__, valid_keys)
  user = dict((k, v) for k, v in user.iteritems() if v is not None)
  return user

# Returns all contributors sorted by number of contributions
def get_users(repos, valid_keys, fetcher):
  result = dict()
  for repo in repos:
    contributors = fetcher(repo)
    for page in contributors:
        for c in page:
          user = retain_keys(c.__dict__, valid_keys)
          if user['login'] in result and user.has_key('contributions'):
            result[user['login']]['contributions'] += user['contributions']
          else:
            result[user['login']] = user
  for user in result.values():
    user.update(get_user(user['login']))
  return result

committers = get_users(ATOMIX_STACK, ["login", "avatar_url", "html_url"],
  lambda repo: gh.repos.collaborators.list(user='atomix', repo = repo))
contributors = get_users(ATOMIX_STACK, ["login", "avatar_url", "html_url", "contributions"], 
  lambda repo: gh.repos.list_contributors(user='atomix', repo = repo))

# Add contribution counts to committers
for committer in committers.values():
  committer['contributions'] = contributors.get(committer['login'], {}).get('contributions', 0)

# Remove committers from contributors
delete_keys(contributors, committers.keys())

# Remove contributors without a name
for login, contributor in contributors.items():
  if 'name' not in contributor:
    del contributors[login]

committers = sorted(committers.values(), key=lambda k: k['contributions'], reverse = True)
contributors = sorted(contributors.values(), key=lambda k: k['contributions'], reverse = True)

print("Committers: " + str(committers))
print("Contributors: " + str(contributors))

# Output to data dir
with open(DATA_DIR + '/committers.yml', 'w') as outfile:
  outfile.write(yaml.dump(committers, default_flow_style=False))
with open(DATA_DIR + '/contributors.yml', 'w') as outfile:
  outfile.write(yaml.dump(contributors, default_flow_style=False))
