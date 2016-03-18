from django.http import HttpResponse
from evidenceCollector.models import Log

import datetime
import time


def index(request, contentid, event):

    sessionid = request.GET.get('sessionid', 0)
    userid = request.GET.get('userid', 0)
    date = request.GET.get('date', datetime.datetime.now())
    visit_count = request.GET.get('visitCount', 0)

    l = Log(created=date, \
            user_id=userid, \
            content_id=contentid, \
            event=event, \
            visitCount=visit_count, \
            sessionId=sessionid)
    l.save()
    print(l)
    return HttpResponse('ok')
