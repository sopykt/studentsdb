# coding: utf-8

from django.shortcuts import render
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ..models import Group


# Views for Groups

def groups_list(request):
    groups = Group.objects.all()

    order_by = request.GET.get('order_by', '')
    if order_by not in ('id', 'leader'):
        order_by = 'title'
    groups = groups.order_by(order_by)

    reverse_by = request.GET.get('reverse', '')
    if reverse_by == '1':
        groups = groups.reverse()

    # paginate students
    # PageNotAnInteger: if page is not an integer, deliver first page
    # if page is out of range (e.g. 9999), deliver last page of results
    paginator = Paginator(groups, 1)
    page = request.GET.get('page')

    try:
        groups = paginator.page(page)
    except PageNotAnInteger:
        groups = paginator.page(1)
    except EmptyPage:
        groups = paginator.page(paginator.num_pages)


    # groups = (
    #     {"id": 1,
    #      "name": u'МтМ-21',
    #      "leader": {"id": 1, "name": u'Ячменев Олег'}},
    #     {"id": 2,
    #      "name": u'МтМ-22',
    #      "leader": {"id": 2, "name": u'Подоба Віталій'}},
    #     {"id": 3,
    #      "name": u'МтМ-23',
    #      "leader": {"id": 3, "name": u'Іванов Андрій'}}
    # )
    return render(request, 'students/groups_list.html',
                  {'groups': groups,
                   'order_by': order_by,
                   'reverse': reverse_by,
                   'groups_url': reverse('groups')
                   })


def groups_add(request):
    return HttpResponse('<h1>Group Add Form</h1>')


def groups_edit(request, gid):
    return HttpResponse('<h1>Edit Group %s</h1>' % gid)


def groups_delete(request, gid):
    return HttpResponse('<h1>Delete Group %s</h1>' % gid)
