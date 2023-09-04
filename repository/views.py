from django.shortcuts import render, get_object_or_404, redirect

from .models import Directory, Content, Client, LoginAttempt, UniquePass


def dir_content(request, dir_id):
    dir = get_object_or_404(Directory, id=dir_id)
    content = Content.objects.filter(directory=dir)
    user = request.user
    if Client.objects.filter(directory=dir, user=user).exists():
        return render(request, "repository/repository.html", {"content": content, "dir": dir})
    else:
        return redirect("repository:dir_admin", dir_id=dir_id)


def dir_admin(request, dir_id):
    dir = get_object_or_404(Directory, id=dir_id)

    if request.FILES:
        img = request.FILES.get('image')
        new = Content.objects.create(directory=dir, image=img)

    content = Content.objects.filter(directory=dir)
    return render(request, "repository/admin_repository.html", {"content": content, "dir": dir})


def create_pass(request, dir_id):
    dir = get_object_or_404(Directory, id=dir_id)
    if request.method == 'POST':
        if request.POST.get('passcode'):
            passcode = UniquePass.objects.create(dir=dir, pass_code=request.POST.get('passcode'))
            passcode.save()
            return redirect("repository:dir_admin", dir_id=dir_id)

    return render(request, "repository/create_pass.html", {"dir": dir})


def delete_img(request, content_id, dir_id):
    if Content.objects.filter(id=content_id).exists():
        c = get_object_or_404(Content, id=content_id)
        c.delete()

    return redirect("repository:dir_admin", dir_id=dir_id)


def check_history(request, dir_id):
    dir = get_object_or_404(Directory, id=dir_id)
    clients = Client.objects.filter(directory=dir)
    c_ids = []
    for c in clients:
        c_ids.append(c.id)

    c_list = []
    attempts = LoginAttempt.objects.filter(client__in=c_ids).order_by('time')
    for a in attempts:
        c_list.append(get_object_or_404(Client, id=a.client.id))

    attempt_client = zip(attempts, c_list) if attempts else []

    return render(request, "repository/history.html", {"attempt_client": attempt_client, "dir": dir})


def attempt_detail(request, attempt_id):
    attempt = get_object_or_404(LoginAttempt, id=attempt_id)
    client = get_object_or_404(Client, id=attempt.client.id)
    dir = get_object_or_404(Directory, id=client.directory.id)
    return render(request, "repository/attempt_detail.html", {"attempt": attempt, "client": client, "dir": dir})


def admin_clients(request, dir_id):
    dir = get_object_or_404(Directory, id=dir_id)
    clients = Client.objects.filter(directory=dir)

    if request.method == 'POST':
        if request.POST.get('suggestion'):
            dir.suggestion = request.POST.get('suggestion')
            dir.save()

    return render(request, "repository/list_clients.html", {"clients": clients, "dir": dir})


def add_client(request, dir_id):
    dir = get_object_or_404(Directory, id=dir_id)
    clients = Client.objects.filter(directory=dir)

    if request.method == 'POST':
        if request.FILES:
            csv_file = request.FILES.get('csv_file')
            file_data = csv_file.read().decode("utf-8")

            lines = file_data.split("\n")
            for line in lines:
                try:
                    Client.objects.create(directory=dir, key_words=line)
                except Exception as e:
                    pass
        elif request.POST.get('keywords'):
            Client.objects.create(directory=dir, key_words=request.POST.get('keywords'))

    return render(request, "repository/add_client.html", {"clients": clients, "dir": dir})


def delete_client(request, dir_id, client_id):
    if Client.objects.get(id=client_id).exists():
        c = get_object_or_404(Client, id=client_id)
        c.delete()

    return redirect("repository:admin_clients", dir_id=dir_id)


def client_detail(request, dir_id, client_id):
    client = Client.objects.get(id=client_id)
    attempts = LoginAttempt.objects.filter(client=client_id)
    dir = get_object_or_404(Directory, id=dir_id)

    return render(request, "repository/client_detail.html", {"client": client, "attempts": attempts, "dir": dir})
