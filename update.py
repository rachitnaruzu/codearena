import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "codearena.settings")
django.setup()
    
from codelabs.models import Problem, Customuser
from django.contrib.auth.models import User
import threading
import json
import sys
from codelabs.webscrape import fetch_interviewbit, fetch_spoj, fetch_hackerrank_rating, fetch_hackerrank_problems, fetch_hackerrank, fetch_codechef, fetch_geeksforgeeks, fetch_topcoder, fetch_codeforces
from django.db.models import Sum

prog_bar_length = 50
progress = 0
max_prog = 0
lock = threading.Lock()
    
def get_platform_handle(user,platform):
    if platform == 'spoj':
        return user.customuser.spojhandle
    if platform == 'hackerrank':
        return user.customuser.hackerrankhandle
    if platform == 'codechef':
        return user.customuser.codechefhandle
    if platform == 'geeksforgeeks':
        return user.customuser.geeksforgeekshandle
    if platform == 'topcoder':
        return user.customuser.topcoderhandle
    if platform == 'codeforces':
        return user.customuser.codeforceshandle
    if platform == 'interviewbit':
        return user.customuser.interviewbithandle
    return None
    
def get_platform_flag(user,platform):
    if platform == 'spoj':
        return user.customuser.spojflag
    if platform == 'hackerrank':
        return user.customuser.hackerrankflag
    if platform == 'codechef':
        return user.customuser.codechefflag
    if platform == 'geeksforgeeks':
        return user.customuser.geeksforgeeksflag
    if platform == 'topcoder':
        return user.customuser.topcoderflag
    if platform == 'codeforces':
        return user.customuser.codeforcesflag
    if platform == 'interviewbit':
        return user.customuser.interviewbitflag
    return None

def mark_invalid(user,platform):
    if platform == 'spoj':
        user.customuser.spojflag = 3
    if platform == 'hackerrank':
        user.customuser.hackerrankflag = 3
    if platform == 'codechef':
        user.customuser.codechefflag = 3
    if platform == 'geeksforgeeks':
        user.customuser.geeksforgeeksflag = 3
    if platform == 'topcoder':
        user.customuser.topcoderflag = 3
    if platform == 'codeforces':
        user.customuser.codeforcesflag = 3
    if platform == 'interviewbit':
        user.customuser.interviewbitflag = 3
    
def mark_valid(user,platform):
    if platform == 'spoj':
        user.customuser.spojflag = 1
    if platform == 'hackerrank':
        user.customuser.hackerrankflag = 1
    if platform == 'codechef':
        user.customuser.codechefflag = 1
    if platform == 'geeksforgeeks':
        user.customuser.geeksforgeeksflag = 1
    if platform == 'topcoder':
        user.customuser.topcoderflag = 1
    if platform == 'codeforces':
        user.customuser.codeforcesflag = 1
    if platform == 'interviewbit':
        user.customuser.interviewbitflag = 1
        
def mark_zero_rating(user,platform):
    if platform == 'spoj':
        user.customuser.spojrating = 0.0
    if platform == 'codechef':
        user.customuser.codecheflongrating = 0.0
        user.customuser.codechefshortrating = 0.0
        user.customuser.codechefltimerating = 0.0
    if platform == 'hackerrank':
        user.customuser.hackerrankrating = 0.0
    if platform == 'geeksforgeeks':
        user.customuser.geeksforgeeksrating = 0.0
    if platform == 'topcoder':
        user.customuser.topcoderrating = 0.0
        user.customuser.topcodermaxrating = 0.0
    if platform == 'codeforces':
        user.customuser.codeforcesrating = 0.0
        user.customuser.codeforcesmaxrating = 0.0
    if platform == 'interviewbit':
        user.customuser.interviewbitrating = 0.0
        
def mark_rating(user,platform,rating):
    if platform == 'spoj':
        user.customuser.spojrating = rating[0]
    if platform == 'codechef':
        user.customuser.codecheflongrating = rating[0]
        user.customuser.codechefshortrating = rating[1]
        user.customuser.codechefltimerating = rating[2]
    if platform == 'hackerrank':
        user.customuser.hackerrankrating = rating[0]
    if platform == 'geeksforgeeks':
        user.customuser.geeksforgeeksrating = rating[0]
    if platform == 'topcoder':
        user.customuser.topcoderrating = rating[0]
        user.customuser.topcodermaxrating = rating[1]
    if platform == 'codeforces':
        user.customuser.codeforcesrating = rating[0]
        user.customuser.codeforcesmaxrating = rating[1]
    if platform == 'interviewbit':
        user.customuser.interviewbitrating = rating[0]
    
    
fetch = { 
            'spoj' : fetch_spoj,
            'hackerrank' : fetch_hackerrank,
            'codechef' : fetch_codechef,
            'geeksforgeeks' : fetch_geeksforgeeks,
            'topcoder' : fetch_topcoder,
            'codeforces' : fetch_codeforces,
            'interviewbit' : fetch_interviewbit
          }
    
def update_progress():
    lock.acquire()
    try:
        global progress
        progress += 1
        hashnum = int((progress * prog_bar_length)/max_prog)
        spacenum = prog_bar_length - hashnum
        sys.stdout.write("\r[{}{}] {}%".format("#" * hashnum," " * spacenum,(hashnum * 100)/prog_bar_length))
    finally:
        lock.release()
    
    
def update_platform(users,platform):
    for user in users:
        update_progress()
        platform_flag = get_platform_flag(user,platform)
        if(platform_flag == 3):
            continue
            
        platform_handle = get_platform_handle(user, platform)
        
        solved, rating = fetch[platform](platform_handle)
        
        user_platform_problems = user.problem_set.filter(platform=platform)
        user_platform_problems_list = [problem for problem in user_platform_problems]
        
        if(solved == False):
            if(platform_flag == 2):
                if user_platform_problems_list:
                    user.problem_set.remove(*user_platform_problems_list)
                mark_invalid(user,platform)
                mark_zero_rating(user, platform)
                user.save()
                user.customuser.save()
            continue
            
        if(platform_flag == 2):
            if user_platform_problems_list:
                    user.problem_set.remove(*user_platform_problems_list)
            mark_valid(user,platform)
            user_platform_problems = user.problem_set.filter(platform=platform)
            
        mark_rating(user,platform,rating)
        
        total_platform_problems = Problem.objects.filter(platform=platform)
        unsolved_platform_problems = total_platform_problems.exclude(code__in = user_platform_problems.values('code'))
        
        for problem in unsolved_platform_problems:
            if problem.code in solved:
                user.problem_set.add(problem)
                
        user.save()
        user.customuser.save()
        
def update_codelabs():
    users = User.objects.filter(is_active = False)
    for user in users:
        user.delete()
    
    users = User.objects.all()
    for user in users:
        points = user.problem_set.all().aggregate(Sum('points'))['points__sum']
        user.customuser.points = points if points else 0
        user.customuser.save()
        
    problems = Problem.objects.all()
    for problem in problems:
        problem.solved = problem.users.count()
        problem.save()
    
                
#@app.route('/')
def run():
    global max_prog
    global progress
    users = User.objects.all()
    
    progress = 0
    max_prog = 0
    
    no_of_platforms = 7
    length = len(users)
    max_prog = length * no_of_platforms
    
    
    thread_list = []
    thread_list.append(threading.Thread(target=update_platform, args=[users,"spoj"]))
    thread_list.append(threading.Thread(target=update_platform, args=[users,"hackerrank"]))
    thread_list.append(threading.Thread(target=update_platform, args=[users,"codechef"]))
    thread_list.append(threading.Thread(target=update_platform, args=[users,"geeksforgeeks"]))
    thread_list.append(threading.Thread(target=update_platform, args=[users,"topcoder"]))
    thread_list.append(threading.Thread(target=update_platform, args=[users,"codeforces"]))
    thread_list.append(threading.Thread(target=update_platform, args=[users,"interviewbit"]))
    
    for thread in thread_list:
        thread.start()
    
    for thread in thread_list:
        thread.join()
     
    update_codelabs()
    print("\ndone\n")


run()
    
    


