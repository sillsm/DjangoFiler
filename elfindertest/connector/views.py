from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from elfinder.operations import Operation

def index(request):
	return render_to_response('index.html', {}, context_instance=RequestContext(request))
	
def connector(request):
	operation = Operation(request)
	if operation.runable:
		operation.run()
	out = operation.response
	return HttpResponse(out, mimetype="application/json")
