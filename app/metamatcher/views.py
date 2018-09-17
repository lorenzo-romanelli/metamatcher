from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from metamatcher.models import SoundRecordings, MatchingRecordings
from pprint import pprint
import json

def index(request):
    return render(request, 'index.html')


def getInputReport(request):
    input_report = MatchingRecordings.objects \
        .all() \
        .values('rec_isrc', 'rec_artist', 'rec_title', 'rec_duration') \
        .distinct() \
        .order_by('rec_artist')
    input_report = [{ k: str(v) for k, v in d.items() } for d in input_report]
    return JsonResponse(input_report, content_type="application/json", safe=False)


@csrf_exempt
def getCandidates(request):
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        data = json.loads(data)
        params = data['params']
        recordings = MatchingRecordings.objects \
            .filter(
                rec_artist=params['artist'],
                rec_title=params['title'],
                rec_duration=params['duration'],
                rec_isrc=params['isrc'],
                score__gt=75) \
            .values(
                'match_rec_id__artist', 
                'match_rec_id__title',
                'match_rec_id__isrc',
                'match_rec_id__duration',
                'score') \
            .order_by('-score')
    return JsonResponse(list(recordings), safe=False)