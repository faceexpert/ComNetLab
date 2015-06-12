from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.files.uploadedfile import TemporaryUploadedFile
from simpleapp.forms import UploadImageForm
import StringIO
import tempfile
import os
import sys
sys.path.append('../face')
import face_interface as face

def upload_file(req):
	if req.method == 'POST':
		form = UploadImageForm(req.POST, req.FILES)
		if form.is_valid():
			file = req.FILES['file']
			if type(file) is not TemporaryUploadedFile:
				tmp_file, tmp_path = tempfile.mkstemp()
				tmp_file = os.fdopen(tmp_file, 'wb')
				tmp_file.write(file.read())
				tmp_file.close()
			else:
				tmp_path = file.temporary_file_path()
			resp = HttpResponse('success, score_male=%s, score_female=%s' % (face.get_score_for_male(tmp_path), face.get_score_for_female(tmp_path)))
			if type(file) is not TemporaryUploadedFile:
				try: os.remove(tmp_file)
				except: pass
			return resp
	else:
		form = UploadImageForm()
	return render_to_response('simpleapp/upload.html', {'form': form}, context_instance=RequestContext(req))
