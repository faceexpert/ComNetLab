# coding: utf-8
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.files.uploadedfile import TemporaryUploadedFile
from simpleapp.forms import UploadImageForm
from PIL import Image
import StringIO
import tempfile
import os
import sys
sys.path.append('../face')
import face_interface as face
import base64
import math

def upload_file(req):
	if req.method == 'POST':
		form = UploadImageForm(req.POST, req.FILES)
		if form.is_valid():
			file = req.FILES['file']
			if type(file) is not TemporaryUploadedFile:
				tmp_file, tmp_path = tempfile.mkstemp()
				tmp_file = os.fdopen(tmp_file, 'wb')
				data = file.read()
				tmp_file.write(data)
				tmp_file.close()
				im = Image.open(StringIO.StringIO(data))
			else:
				tmp_path = file.temporary_file_path()
				im = Image.open(open(tmp_path, 'rb'))

			w, h = im.size
			data = StringIO.StringIO()
			if w * h > 43200 or max(w, h) > 600:
				r = max(math.sqrt(w * h / 43200.), w / 600., h / 600.)
				w, h = map(lambda x: int(math.ceil(x)), (w / r, h / r))
				im.thumbnail((w, h), Image.ANTIALIAS)
			im.save(data, format='jpeg')
			data.seek(0)

			male = req.POST['gender'] == 'm'
			result = int(round((face.get_score_for_male(tmp_path) if male else face.get_score_for_female(tmp_path))[0]))
			if result < 60:
				comment = '同学，你如此天生丽质，一定是照片的角度不够好遮盖了你的旺夫/旺妻气质，重新传一张试试吧~'
			elif male:
				if result <= 70:
					comment = '你是一个胜不骄败不馁的人，总是以一颗平常心去看待周围的一切，冷静的头脑使你能够比较顺利的解决生活中的大部分麻烦。同时，你有着坚强意志力和耐力，不屈不挠，从不放弃。嫁给你的女生只要能够和你同风雨、共患难，就一定能拥有一个幸福的将来。'
				elif result <= 80:
					comment = '在生活中，你善良、热心，能为人设身处地的着想，经常对需要帮助的人施以援手，在朋友圈内颇受好评。家庭生活中，你是一个顾家念家的人，对自己的孩子也十分照顾，经常会帮妻子分担一些家务。做你的妻子能够体会到老公疼惜自己的幸福。'
				else:
					comment = '你是一个在事业和家庭上都十分成功的男人。在事业上，你工作能力强，同时具有一定的领导力，像阳光一样照拂身边的人，备受同事的尊重。你是一个有责任感的人，不仅对每一项应该完成工作兢兢业业，还对自己的家庭十分负责，你对自己的妻子忠贞不二，同时在日常生活中也关怀备至。对孩子要求严格但不会一味约束，嫁给你的女子十分幸运，不仅事业上会更上一层楼，家庭生活也十分美满。'
			else:
				if result <= 70:
					comment = '你心地宽阔，好交朋友又乐于助人，同时也是心思细密，会帮朋友渡过难关。进退有礼，没有令人难以忍受的傲气，较少低潮与挫折，面对逆境也都有克服与转移的一套思维，娶到你等于同时拥有一堆真心好朋友和克服困难的巨大勇气和后动力！'
				elif result <= 80:
					comment = '你很有贵气，有个性却不会自找烦恼，不自找麻烦，自己的生活能够过得舒适不纠结。事业上，既能够荫夫帮夫，也能有适度的协调性和妥协性，能够较周全地帮家里解决问题，分忧解劳。有这样得媳妇是男人的荣幸！'
				elif result <= 90:
					comment = '不得了！能有如此面相，定是不仅旺夫，还能生出具有优良基因的孩子！所生子息也容易心存孝道，聪明多福，未来成就高。不仅如此，身体也是无病无痛，健康长寿的。夫荣子孝，实在好命。这样的女子，不仅旺当代，还旺下一代，遇到了就要积极把握，以免错失先机，被其他的人先追走了！'
				else:
					comment = '旺夫相，要分开一组组来讲的，并不能单就眼眉生得好，或单一个鼻或眼靓，便属于旺夫，这并非说完全不能旺夫，而只是旺一点点而已。当今要的，是一个组合，分三个部分为一组，这三个部位配合得好，才算是旺夫，而且是旺夫程度相当之大；若只有一两样好者，亦属不差，其旺夫之力亦不弱；若果没有，夫运便属平常，好坏则要视乎丈夫自己本身之相貌而定了。而你，一定就是那位“三个部位配合得好”的姑娘了！简直不能更旺！（嫁给我吧）'

			resp = render_to_response('simpleapp/result.html', {
				'img': {
					'content_type': 'image/jpeg',
					'width': w,
					'height': h,
					'base64_data': base64.standard_b64encode(data.read())
					},
				'male': male,
				'comment': comment,
				'result': result
				})
			if type(file) is not TemporaryUploadedFile:
				try: os.remove(tmp_path)
				except: pass
			return resp
	else:
		form = UploadImageForm()
	return render_to_response('simpleapp/upload.html', {'form': form}, context_instance=RequestContext(req))
