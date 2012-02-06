from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from elfinder.operations import Operation

def index(request):
	return render_to_response('elfinder.html', {}, context_instance=RequestContext(request))
def sounds(request):
	return HttpResponseRedirect(u'%s%s'%(settings.STATIC_URL, request.path.split('/', 1)[1]))
	
def connector(request):
	operation = Operation(request.__dict__, get=request.GET.copy(), post=request.POST.copy(), files=request.FILES.copy())
	if operation.runable:
		operation.run()
	out = operation.response.get_result()
	headers = operation.response.headers
	response = HttpResponse(out, mimetype=operation.response.mimetype)
	if headers:
		for head, value in headers.items():
			try:
				response[head] = value
			except Exception, e:
				pass
	return response
