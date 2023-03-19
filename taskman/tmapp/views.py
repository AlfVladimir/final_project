import re

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from tmapp.models import Project, Sprint, Status, Task

from .forms import (EditSprintForm, NewSprintForm, ProjectForm, SignupForm,
                    StatusForm, TaskForm)
from .serializers import (ProjectSerializer, SprintSerializer,
                          StatusSerializer, TaskSerializer)


# Задачи
@login_required
def task_new(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)

        if form.is_valid():
            task = form.save(commit=False)
            task.save()

            return redirect('task', id=task.id)
    else:

        initial = {'executor': request.user}
        project_id = request.GET.get('project_id', 0)
        if project_id:
            project_id = re.search('[0-9]+', project_id)[0]
            initial['project'] = int(project_id)
        form = TaskForm(initial=initial)
    return render(request, 'tasknew.html', {
        'form': form
    })


@login_required
def task_edit(request, id):

    task = get_object_or_404(Task, id=id)

    if request.method == 'GET':
        context = {'form': TaskForm(instance=task), 'id': id}
        return render(request, 'taskedit.html', context)
    elif request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task', id)
        else:
            return render(request, 'taskedit.html', {'form': form})


@login_required
def task_detail(request, id):

    task = get_object_or_404(Task, id=id)

    if "_next-status" in request.POST:
        next_status = Status.objects.filter(parent_status=task.status).first()
        if next_status:
            task.status = next_status
            task.save()

    if "_prev-status" in request.POST:
        if task.status.parent_status:
            task.status = task.status.parent_status
            task.save()

    # Отображение истории задачи
    # из стороннего пакета django simple history
    tasks_history_original = Task.history.filter(id=id)
    tasks_history = []
    tasks_history_type = {
        '+': 'Задача создана',
        '-': 'Задача удалена',
        '~': 'Задача изменена',
    }
    for task_h_o in tasks_history_original:
        if task_h_o.prev_record:
            delta = task_h_o.diff_against(task_h_o.prev_record)
            change_list = ''
            for change in delta.changes:
                change_list += task_detail_history_to_text(change)
            if not delta.changes:
                change_list = 'Сохранение без изменений.'
        tasks_history.append({
            'history_date': task_h_o.history_date,
            'type': tasks_history_type[task_h_o.history_type],
            'change_list': change_list if task_h_o.history_type == '~' else ' '
        })

    return render(request, 'taskdetail.html', {
        'task': task,
        'tasks_history': tasks_history,
    })


def task_detail_history_to_text(change):
    """Преобразовываем изменения из таблицы history, в читаемый вид"""
    """в отдельной функции, что бы не засорят логику вьюхи"""

    tasks_history_fields = {
        'project': 'проект',
        'sprint': 'спринт',
        'status': 'статус',
        'name': 'название',
        'content': 'содеражине',
        'executor': 'исполнитель',
        'is_complete': 'завершена',
    }
    change_list = ''
    if change.field == 'project' and not change.new:
        change_list +=\
            f"Задача удалена из проекта №{change.old}. "
    elif change.field == 'project' and change.new:
        change_list +=\
            f"Задача добавлена в проект №{change.new}. "
    elif change.field == 'sprint' and not change.new:
        change_list +=\
            f"Задача удалена из спринта №{change.new}. "
    elif change.field == 'sprint' and change.new:
        change_list +=\
            f"Задача добавлена в спринт №{change.new}. "
    else:
        change_text = str(change.new)
        if len(change_text) > 60:
            change_text = change_text[:60] + '..'
        change_list +=\
            f"""Поле '{tasks_history_fields[change.field]}'"""\
            f""" изменено на '{change_text}'. """
    return change_list


@login_required
def task_list(request):

    tasks = Task.objects.all().order_by('is_complete', '-id')

    return render(request, 'tasklist.html', {
        'tasks': tasks,
    })


@login_required
def task_delete(request, id):
    task = get_object_or_404(Task, id=id)
    if request.method == "POST":
        task.delete()
        return redirect('tasklist')
    return render(request, "taskdelete.html", {'task': task})


# Проеткы
@login_required
def project_list(request):

    projects = Project.objects.all()

    cur_date = timezone.localdate()

    sprints = Sprint.objects.filter(
            Q(date_end__gte=cur_date) & Q(date_start__lte=cur_date)
        ).filter(tasks__is_complete=False).distinct()

    return render(request, 'projectlist.html', {
        'projects': projects,
        'sprints': sprints,
    })


@login_required
def project_edit(request, id):

    project = get_object_or_404(Project, id=id)

    if request.method == 'GET':
        context = {'form': ProjectForm(instance=project), 'id': id}
        return render(request, 'projectedit.html', context)
    elif request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('project', id)
        else:
            return render(request, 'projectedit.html', {'form': form})


@login_required
def project_delete(request, id):
    project = get_object_or_404(Project, id=id)
    if request.method == "POST":
        project.delete()
        return redirect('projectlist')
    return render(request, "projectdelete.html", {'project': project})


@login_required
def project_detail(request, id):

    project = get_object_or_404(Project, id=id)

    sprints = Sprint.objects.filter(project=id)

    tasks = Task.objects.filter(project=id).order_by('is_complete', '-id')

    return render(request, 'projectdetail.html', {
        'project': project,
        'tasks': tasks,
        'sprints': sprints,
    })


@login_required
def project_new(request):

    if request.method == 'POST':
        form = ProjectForm(request.POST)

        if form.is_valid():
            project = form.save(commit=False)
            project.save()

            return redirect('project', id=project.id)
    else:
        form = ProjectForm()

    return render(request, 'projectnew.html', {
        'form': form
    })


# Спринты
@login_required
def sprint_new(request):

    if request.method == 'POST':
        form = NewSprintForm(request.POST)

        if form.is_valid():
            sprint = form.save(commit=False)
            sprint.save()

            # return redirect('project', id=project.id)
            return redirect('project', id=sprint.project.id)
    else:

        initial = {}
        project_id = request.GET.get('project_id', 0)
        if project_id:
            project_id = re.search('[0-9]+', project_id)[0]
            initial['project'] = int(project_id)
        form = NewSprintForm(initial=initial)

    return render(request, 'sprintnew.html', {
        'form': form
    })


@login_required
def sprint_delete(request, id):
    sprint = get_object_or_404(Sprint, id=id)
    project_id = sprint.project.id
    if request.method == "POST":
        sprint.delete()
        return redirect('project', project_id)
    return render(request, "sprintdelete.html", {'sprint': sprint})


@login_required
def sprint_edit(request, id):

    sprint = get_object_or_404(Sprint, id=id)

    if request.method == 'GET':
        context = {'form': EditSprintForm(instance=sprint), 'id': id}
        return render(request, 'sprintedit.html', context)

    elif request.method == 'POST':
        form = EditSprintForm(request.POST, instance=sprint)
        if form.is_valid():
            form.save()
            return redirect('project', sprint.project.id)
        else:
            return render(request, 'sprintedit.html', {'form': form, 'id': id})


# Статусы
@login_required
def status_list(request):

    unsorted_statuses = Status.objects.all()

    statuses = sorted(unsorted_statuses, key=lambda t: t.get_parent_id())

    return render(request, 'statuslist.html', {
        'statuses': statuses,
    })


@login_required
def status_new(request):

    if request.method == 'POST':
        form = StatusForm(request.POST)

        if form.is_valid():
            status = form.save(commit=False)
            status.save()

            return redirect('statuslist')
    else:

        form = StatusForm()

    return render(request, 'statusnew.html', {
        'form': form
    })


@login_required
def status_edit(request, id):

    status = get_object_or_404(Status, id=id)

    if request.method == 'GET':
        context = {'form': StatusForm(instance=status), 'id': id}
        return render(request, 'statusedit.html', context)

    elif request.method == 'POST':
        form = StatusForm(request.POST, instance=status)
        if form.is_valid():
            form.save()
            return redirect('statuslist')
        else:
            return render(request, 'statusedit.html', {'form': form, 'id': id})


@login_required
def status_delete(request, id):
    status = get_object_or_404(Status, id=id)
    if request.method == "POST":
        status.delete()
        return redirect('statuslist')
    return render(request, "statusdelete.html", {'status': status})


# Регистрация
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect('/')
    else:
        form = SignupForm()

    return render(request, 'signup.html', {
        'form': form
    })


# DRF
class TaskDRFViewSet(
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.DestroyModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet,):
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class ProjectDRFViewSet(
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.DestroyModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet,):
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class SprintDRFViewSet(
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.DestroyModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet,):
    permission_classes = [IsAuthenticated]
    queryset = Sprint.objects.all()
    serializer_class = SprintSerializer


class StatusDRFViewSet(
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.DestroyModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet,):
    permission_classes = [IsAuthenticated]
    queryset = Status.objects.all()
    serializer_class = StatusSerializer
