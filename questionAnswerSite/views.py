from django.shortcuts import render
from questionAnswerSite.models import Questions
from questionAnswerSite.models import Answers
from questionAnswerSite.models import Votes
from questionAnswerSite.models import Pictures
from questionAnswerSite.models import Tags
from django.shortcuts import redirect
from google.appengine.ext import db
from google.appengine.api import users


from google.appengine.ext import blobstore

import re
import datetime
import logging
import random

logger = logging.getLogger(__name__)

# Create your views here.
def home(request):
	return render(request, "questionAnswerSite/home.html")


def about(request):
	return render(request, "questionAnswerSite/about.html")


def convertToHtmlAndImage(input):
	try:
		output= re.compile(r'(http(s)?://\S*[^(.jpg)(.png)(.gif)](\s|$))').sub(r'<a href="\1">\1</a>',input)
		output=re.compile(r'(http://\S*[(.jpg)(.png)(.gif)](\s|$))').sub(r'<img src="\1" style="width:304px;height:228px">', output)
	except:
		return input
	return output

def question(request, identifier):
	myKey = db.Key.from_path('Questions', identifier)
	question = db.get(myKey)
	logging.info("The id is: " + identifier)

	answers_gb = Answers.all()
	answers = answers_gb.ancestor(question)


	question.description=convertToHtmlAndImage(question.description)
	question.title=convertToHtmlAndImage(question.title)

	for ans in answers:
		ans.title=convertToHtmlAndImage(ans.title)
		ans.description=convertToHtmlAndImage(ans.description)
		ans.put
	


	return render(request, "questionAnswerSite/review.html", {'question': question,'answers':answers})

def reviews(request,count):
	user = users.get_current_user()
	if user:
		a='aaa'
		#return render(request,'login.html', { 'user':user, 'google_url': users.create_login_url('/reviews/') })
	else:
		return render(request,'login.html', { 'user':user, 'google_url': users.create_login_url('/reviews/') })

	if request.method == 'POST':
		items = request.POST
		tag=items['tagNam']
		all_tags = db.Query(Tags)
		filterTags=all_tags.filter("tag_name =", tag)
		questions=[]
		for tmp_tag in filterTags:
			identifier = tmp_tag.question_id
			myKey = db.Key.from_path('Questions', identifier)
			question = db.get(myKey)
			questions.append(question)

		tag_names = db.GqlQuery("SELECT DISTINCT tag_name FROM Tags")
		return render(request, "questionAnswerSite/reviews.html", {'tag_names':tag_names,'questions': questions})

	if count=='':
		count =0

	tag_names = db.GqlQuery("SELECT DISTINCT tag_name FROM Tags")
	offset=int(count);
	count=int(count)+10;
	questions = db.GqlQuery("SELECT * FROM Questions ORDER BY modifydate DESC LIMIT 10 OFFSET "+str(offset))
	return render(request, "questionAnswerSite/reviews.html", {'next':str(count),'tag_names':tag_names,'questions': questions})

def add_review(request):
	user = users.get_current_user()
	if user:
		a='aaa'
	else:
		return render(request,'login.html', { 'user':user, 'google_url': users.create_login_url('/reviews/') })

	logging.info("The id is: " + str(user))

	if request.method == 'POST':
		items = request.POST
		keyVal=str(random.getrandbits(32))
		r = Questions(key_name=keyVal)
		#r = Questions(description=items['review'], title=items['title'], star_rating=0)
		r.title=items['title']
		r.description=items['description']
		r.createdate = datetime.datetime.now()
		r.modifydate= datetime.datetime.now()
		r.identifier=keyVal
		r.author=user
		r.put()
		if items['tag']:
			tags=items['tag'].split(':')
			for i in tags:
				tag = Tags()
				tag.tag_name=i
				tag.question_id=keyVal
				tag.put()

		return redirect('/reviews')
	else:
		return render(request, 'questionAnswerSite/add_review.html')


# def add_answer(request,identifier):
# 	user = users.get_current_user()
# 	if user:
# 		a='aaa'
# 	else:
# 		return render(request,'login.html', { 'user':user, 'google_url': users.create_login_url('/reviews/') })

# 	logging.info("The id is: " + str(user))

# 	if request.method == 'POST':
# 		items = request.POST
# 		r = Questions(description=items['review'], title=items['title'], star_rating=0)
# 		r.createdate = datetime.datetime.now()
# 		r.author=user
# 		r.identifier = str(random.getrandbits(32))
# 		r.put()
# 		return redirect('/reviews')
# 	else:
# 		return render(request, 'questionAnswerSite/add_review.html')

def my_question(request):
	user = users.get_current_user()
	if user:
		a='aaa'
		#return render(request,'login.html', { 'user':user, 'google_url': users.create_login_url('/reviews/') })
	else:
		return render(request,'login.html', { 'user':user, 'google_url': users.create_login_url('/myquestions/') })

	questions = db.Query(Questions)
	questions.filter("author =", user)

	

	return render(request, "questionAnswerSite/myquestions.html", {'questions': questions})



def modify_question(request,identifier):
	user = users.get_current_user()
	if user:
		a='aaa'
	else:
		return render(request,'login.html', { 'user':user, 'google_url': users.create_login_url('/reviews/') })
	myKey = db.Key.from_path('Questions', identifier)
	question = db.get(myKey)

	all_tags = db.Query(Tags)
	filterTags=all_tags.filter("question_id =", identifier)
	tagStr=''
	for tag in filterTags:
		tagStr=tagStr+tag.tag_name+':'
	tagStr=tagStr[:-1]

	logging.info("The id is: " + identifier)
	return render(request, "questionAnswerSite/modify_question.html", {'tagStr':tagStr,'question': question})

def modify_question_act(request):
	user = users.get_current_user()
	if user:
		a='aaa'
		#return render(request,'login.html', { 'user':user, 'google_url': users.create_login_url('/reviews/') })
	else:
		return render(request,'login.html', { 'user':user, 'google_url': users.create_login_url('/myquestions/') })

	if request.method == 'POST':
		items = request.POST
		idVal=items['identifier']
		myKey = db.Key.from_path('Questions', idVal)
		question = db.get(myKey)
		logging.info("The id is: " + idVal)
		question.modifydate= datetime.datetime.now()
		question.title=items['title']
		question.description=items['description']
		question.put()

		all_tags = db.Query(Tags)
		my_tags= all_tags.filter("question_id =", idVal)
		for tag in my_tags:
			db.delete(tag)

		if items['tag']:
			tags=items['tag'].split(':')
			for i in tags:
				tag = Tags()
				tag.tag_name=i
				tag.question_id=idVal
				tag.put()


	return redirect('/my_question')

def delete_question(request,identifier):
	user = users.get_current_user()
	if user:
		a='aaa'
	else:
		return render(request,'login.html', { 'user':user, 'google_url': users.create_login_url('/reviews/') })
	myKey = db.Key.from_path('Questions', identifier)
	db.delete(myKey)

	all_tags = db.Query(Tags)
	my_tags= all_tags.filter("question_id =", identifier)
	for tag in my_tags:
		db.delete(tag)
	#return render(request, "questionAnswerSite/test.html", {'field': identifier})
	return redirect('/my_question')






#########################ANSWER.

def add_answer_page(request,identifier):
	user = users.get_current_user()
	if user:
		a='aaa'
	else:
		return render(request,'login.html', { 'user':user, 'google_url': users.create_login_url('/reviews/') })

	logging.info("The id is: " + str(user))

	myKey = db.Key.from_path('Questions', identifier)
	question = db.get(myKey)
	return render(request, "questionAnswerSite/add_answer_page.html", {'question': question})

def add_answer(request,identifier):
	user = users.get_current_user()
	if user:
		a='aaa'
	else:
		return render(request,'login.html', { 'user':user, 'google_url': users.create_login_url('/reviews/') })
	if request.method == 'POST':
		items = request.POST
		myKey = db.Key.from_path('Questions', identifier)
		question = db.get(myKey)

		keyVal=str(random.getrandbits(32))
		r = Answers(key_name=keyVal,parent=question)
		r.title=items['title']
		r.createdate = datetime.datetime.now()
		r.modifydate= datetime.datetime.now()
		r.identifier=keyVal
		r.author=user
		r.put()
	return redirect('/reviews')
	

#########################VOTE.

def vote(request,identifier,voteVal,type):
	user = users.get_current_user()
	if user:
		a='aaa'
	else:
		return render(request,'login.html', { 'user':user, 'google_url': users.create_login_url('/reviews/') })

	y=str(identifier)+str(user)
	#return render(request, "questionAnswerSite/test.html", {'field': id})
	#keyVal=str(random.getrandbits(32))
	myKey = db.Key.from_path('Votes', y)
	vote = db.get(myKey)
	voteVal=int(voteVal)-2
	#return render(request, "questionAnswerSite/test.html", {'field1': int(voteVal),'field2':i})
	if((vote is None) or (int(vote.val) != voteVal)):
		#return render(request, "questionAnswerSite/test.html", {'field': k})
		if vote is None:
			curVote=0
		else:
			curVote=vote.val
		objs = db.GqlQuery("SELECT * FROM "+ type +" WHERE identifier=:1",identifier)
		for obj in objs:
			obj.votes = obj.votes + int(voteVal)
			obj.put()
		vote=Votes(key_name=y)
		vote.author=user
		vote.val=curVote+int(voteVal)
		vote.voteFor=identifier
		vote.createdate = datetime.datetime.now()
		vote.put()

	return redirect('/reviews')
	#Votes


def add_pic(request):
	user = users.get_current_user()
	if user:
		a='aaa'
	else:
		return render(request,'login.html', { 'user':user, 'google_url': users.create_login_url('/reviews/') })

	upload_url = blobstore.create_upload_url('/upload/serve')
	return render(request,'questionAnswerSite/add_img.html', { 'upload_url':upload_url })


def list_all_img(request):
	user = users.get_current_user()
	if user:
		a='aaa'
	else:
		return render(request,'login.html', { 'user':user, 'google_url': users.create_login_url('/reviews/') })


	mypictures = db.Query(Pictures)
	mypictures.filter("author =", user.email())
	#return render(request, "questionAnswerSite/test.html", {'field1': user.email()})
	#mypictures = db.GqlQuery("SELECT * FROM Pictures WHERE author = " + user.email())
	return render(request,'questionAnswerSite/list_img.html', { 'mypictures':mypictures })


def delete_img(request,blobKey):
	user = users.get_current_user()
	if user:
		a='aaa'
	else:
		return render(request,'login.html', { 'user':user, 'google_url': users.create_login_url('/reviews/') })

	#return render(request, "questionAnswerSite/test.html", {'field1': blobKey})
	picKey = db.Key.from_path('Pictures', str(blobKey))
	pic = db.get(picKey)
	db.delete(pic)

	mypictures = db.Query(Pictures)
	mypictures.filter("author =", user.email())
	return render(request,'questionAnswerSite/list_img.html', { 'mypictures':mypictures })