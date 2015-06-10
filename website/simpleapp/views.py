from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from simpleapp.forms import UploadImageForm
from PIL import Image
import StringIO

def upload_file(req):
	if req.method == 'POST':
		form = UploadImageForm(req.POST, req.FILES)
		if form.is_valid():
			#TODO
			im = Image.open(StringIO.StringIO(req.FILES['file'].read()))
			return HttpResponse('success, format=%s, width=%d, height=%d' % (im.format, im.size[0], im.size[1]))
	else:
		form = UploadImageForm()
	return render_to_response('simpleapp/upload.html', {'form': form}, context_instance=RequestContext(req))
