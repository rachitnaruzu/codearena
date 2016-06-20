from bs4 import BeautifulSoup
import requests as rq
import re
import json

pattern = "[A-Z0-9]+"
spoj_base = "http://www.spoj.com/users/"
hackerrank_prefix = "https://www.hackerrank.com/rest/hackers/"
hackerrank_problem_suffix = "/recent_challenges?offset=0&limit=1000/"
hackerrank_rating_suffix = "/rating_histories/"
codechef_base = "http://www.codechef.com/users/"

def fetch_spoj(handle):
    
    if handle == '':
        return False, []
    
    url = spoj_base + handle + "/"
    r = rq.get(url)
    if r.status_code == 404:
        return False, []

    strpg = r.text
    if(len(re.findall("World Rank",strpg)) == 0):
        return False, []
 
    soup = BeautifulSoup(strpg,"html.parser")
 
    table = soup.findAll("table",attrs = {"class":"table-condensed"})
    problems = table[0].findAll('a')
    problems = [re.findall(pattern,str(problem)) for problem in problems]
    problems2 = []
    for problem in problems:
        if problem:
            problems2.append(problem[0])
            
    profilerankstr = re.findall('([0-9\.]+ points)',strpg)[0]
    rating = profilerankstr.split(' ')[0]
    rating = [rating]
    
    return problems2, rating
    
def fetch_hackerrank_rating(handle):
    if handle == '':
        return [0]
    url = hackerrank_prefix + handle + hackerrank_rating_suffix
    resp = rq.get(url)
    if resp.status_code == 404:
        return [0]
    data = json.loads(resp.text)
    ratings = data['models'][0]['events']
    if not ratings:
       return [0] 
    return [ratings[len(ratings)-1]['rating']]
   
def fetch_hackerrank_problems(handle):
    if handle == '':
        return False
    url = hackerrank_prefix + handle + hackerrank_problem_suffix
    resp = rq.get(url)
    if resp.status_code == 404:
        return False
    data = json.loads(resp.text)
    data = data['models']
    problems = [problem['ch_slug'] for problem in data]
    return problems
    
def fetch_hackerrank(handle):
    problems = fetch_hackerrank_problems(handle)
    rating = fetch_hackerrank_rating(handle)
    return problems, rating
    
def fetch_codechef(handle):

    if handle == '':
        return False, []
    
    url = codechef_base + handle + '/'
    resp = rq.get(url)
    if resp.status_code == 404:
        return False, []
        
    strpg = resp.text
    if(len(re.findall('Rank &amp; Rating',strpg)) == 0):
        return False, []

    soup = BeautifulSoup(strpg,'html.parser')
    div = soup.findAll('div', attrs = {'class':'profile'})[0]
    profile_table = div.find_all('table')[1]
    problems = profile_table.find_all('tr')[7]
    anchor_tags = problems.find_all('a')
    expression = '/status/(.*),' + handle
    expression_search = '/status/.*,' + handle

    problem_solved = []
    for tag in anchor_tags:
        x = tag['href']
        temp = re.findall(expression, x)
        if len(temp) > 0:
            problem_solved.append(temp[0])
            
    ratingtable = soup.findAll('table', attrs = {'class':'rating-table'})[0]
    ratingtable = ratingtable.findAll('tr')[1:4]
    rating = [tr.findAll('td')[2].contents[0] for tr in ratingtable]
    
    return problem_solved, rating

def fetch_topcoder(handle):
    if handle == '':
        return False, []
    url = 'https://api.topcoder.com/v3/members/' + handle + '/stats/'
    resp = rq.get(url)
    if resp.status_code == 404:
        return False, []
    data = json.loads(resp.text)
    rating = 0
    maxrating = 0
    minrating = 0
    if 'SRM' in data['result']['content']['DATA_SCIENCE']:
        rating = data['result']['content']['DATA_SCIENCE']['SRM']['rank']['rating']
        maxrating = data['result']['content']['DATA_SCIENCE']['SRM']['rank']['maximumRating']
        minrating = data['result']['content']['DATA_SCIENCE']['SRM']['rank']['minimumRating']
    return [],[rating, maxrating]
    
def fetch_codeforces(handle):
    if handle == '':
        return False, []
    url = 'http://codeforces.com/api/user.info?handles=' + handle
    resp = rq.get(url)
    if resp.status_code == 404 or resp.status_code == 400:
        return False, []
    data = json.loads(resp.text)
    if data['status'] == 'FAILED':
        return False, []
    rating = data['result'][0]['rating']
    maxRating = data['result'][0]['maxRating']
    return [],[rating,maxRating]

def fetch_geeksforgeeks(handle):
    if handle == '':
        return False, []
    handle = handle.replace(' ','%20')
    url = 'http://www.practice.geeksforgeeks.org/user-profile.php?user=' + handle
    resp = rq.get(url)
    if resp.status_code == 404:
        return False, []
    strpg = resp.text
    if(len(re.findall('Username',strpg)) == 0):
        return False, []
    soup = BeautifulSoup(strpg,'html.parser')
    profile_table = soup.findAll('table', attrs = {'class':'table-user-information'})[0]
    profile_tr = profile_table.find_all('tr')
    rating = profile_tr[3]
    rating = rating.find_all('td')[1].contents[0]
    problems_solved = []
    problems = [problem.contents[0].replace(' ','') for problem in profile_tr[7].findAll('a')]
    problems_solved = problems_solved + problems
    problems = [problem.contents[0].replace(' ','') for problem in profile_tr[8].findAll('a')]
    problems_solved = problems_solved + problems
    problems = [problem.contents[0].replace(' ','') for problem in profile_tr[9].findAll('a')]
    problems_solved = problems_solved + problems
    problems = [problem.contents[0].replace(' ','') for problem in profile_tr[10].findAll('a')]
    problems_solved = problems_solved + problems
    return problems_solved, [rating.replace(' ','')]

def fetch_interviewbit(handle):
    if handle == '':
        return False, []
    url = 'https://www.interviewbit.com/profile/' + handle
    resp = rq.get(url)
    if resp.status_code == 404:
        print(1)
        return False, []
    strpg = resp.text
    #print(strpg)
    if len(re.findall('Score',strpg)) == 0:
        print(2)
        return False, []
    soup = BeautifulSoup(strpg,'html.parser')
    profile_div = soup.findAll('div', attrs = {'class':'user-stats'})[0]
    rating_div = profile_div.findAll('div',attrs={'class':'stat'})[1]
    rating = rating_div.findAll('div')[0].contents[0]
    return [], [rating]

def valid_codechef_problem(problemcode, url):
    if problemcode == '':
        return False
    
    resp = rq.get(url)
    if resp.status_code == 404:
        return False
    strpg = resp.text
    if(len(re.findall('SUCCESSFUL SUBMISSIONS',strpg)) == 0):
        return False
    if(len(re.findall(problemcode,strpg)) == 0):
        return False
    return True
    
def valid_spoj_problem(problemcode, url):
    if problemcode == '':
        return False
    
    resp = rq.get(url)
    if resp.status_code == 404:
        return False
    strpg = resp.text
    if(len(re.findall('Submit solution!',strpg)) == 0):
        return False
    if(len(re.findall(problemcode,strpg)) == 0):
        return False
    return True
    
def valid_hackerrank_problem(problemcode, url):
    if problemcode == '':
        return False
    
    resp = rq.get(url)
    if resp.status_code == 404:
        return False
    strpg = resp.text
    if(len(re.findall(problemcode,strpg)) == 0):
        return False
    return True
    
def valid_geeksforgeeks_problem(problemcode, url):
    if problemcode == '':
        return False
    problemcode = problemcode.replace(' ','')
    resp = rq.get(url)
    if resp.status_code == 404:
        return False
    strpg = resp.text
    soup = BeautifulSoup(strpg, 'html.parser')
    problemcodediv = soup.findAll('div', attrs = {'id':'border'})[0]
    fetched_problemcode = problemcodediv.findAll('strong')[0].contents[0].replace(' ','')
    if not problemcode == fetched_problemcode:
        return False
    return True

def validproblem(problemcode, platform, url):
    if platform == 'codechef': return valid_codechef_problem(problemcode, url)
    if platform == 'spoj': return valid_spoj_problem(problemcode, url)
    if platform == 'hackerrank': return valid_hackerrank_problem(problemcode, url)
    if platform == 'geeksforgeeks': return valid_geeksforgeeks_problem(problemcode, url)
    return False
