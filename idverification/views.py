import os

from django.shortcuts import render, redirect
from django.http import HttpResponse
from repository.models import Directory, Client, UniquePass, LoginAttempt
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib import messages
from idverification.IdDetector import *
from django.http.response import StreamingHttpResponse
import repository.views

camera_g = None
face_frame_g = None
id_frame_g = None
other_faces_g = None
dir_id_g = None
user_id_g = None
credentials_path_g = None


def home(request):
    global camera_g
    if camera_g is not None:
        try:
            camera_g.release()
        except:
            pass
    logout(request=request)
    cerca = request.GET.get("repository_search")
    resultats = []
    if cerca:
        resultats = Directory.objects.filter(name__icontains=cerca)
    return render(request, "idverification/home.html", {"resultats": resultats})


def create_dir(request):
    if request.method == "GET":
        return render(request, "idverification/create_dir.html", {"taken": False})
    if request.method == "POST":
        name = request.POST.get("name")
        if Directory.objects.filter(name__exact=name).exists():
            return render(request, "idverification/create_dir.html", {"taken": True})
        else:
            suggestion = request.POST.get("suggestion")
            dir = Directory.objects.create(name=name, suggestion=suggestion)
            return redirect("idverification:add_admin", dir_id=dir.id)


def add_admin(request, dir_id):
    dir = Directory.objects.get(id=dir_id)
    if request.method == "GET":
        return render(request, "idverification/add_admin.html", {"dir": dir})
    if request.method == "POST":
        if dir.admin_credentials:
            dir.admin_credentials.delete()
        dir.admin_credentials = request.FILES.get('credentials')
        dir.save()

        if not check_face(dir.admin_credentials.path):
            messages.success(request, ("No s'a trobat cap rostre a la teva imatge, torna-ho a intentar."))
            return render(request, "idverification/add_admin.html", {"dir": dir})

        user = User(username=dir.name)
        user.save()
        dir.user = user
        dir.save()
        return redirect("idverification:identity_check", dir_id=dir.id, credentials_path=dir.admin_credentials.path,
                        user_id=dir.user.id)


def identity_check_admin(request, dir_id):
    dir = Directory.objects.get(id=dir_id)
    return redirect("idverification:identity_check", dir_id=dir.id, user_id=dir.user.id,
                    credentials_path=dir.admin_credentials.path)


def select_user(request, dir_id):
    dir = Directory.objects.get(id=dir_id)
    if request.method == "GET":
        return render(request, "idverification/select_user.html", {"dir": dir})
    if request.method == "POST":
        if UniquePass.objects.filter(dir=dir, pass_code__exact=request.POST.get('keywords')):
            if Client.objects.filter(directory=dir).exists():
                user = Client.objects.filter(directory=dir)[0].user
            else:
                user = User.objects.create(username="unique")
                user.save()
                client = Client.objects.create(directory=dir, key_words="null", user=user)
                client.save()
            login(request, user)
            return redirect("repository:dir_content", dir_id=dir_id)

        if Client.objects.filter(directory=dir, key_words__iexact=request.POST.get('keywords')).count() == 1:
            client = Client.objects.get(directory=dir, key_words__iexact=request.POST.get('keywords'))
            if client.credentials:
                return redirect("idverification:identity_check",
                                dir_id=dir_id, credentials_path=client.credentials.path, user_id=client.user.id)
            else:
                return redirect("idverification:add_credentials", dir_id=dir_id, client_id=client.id)
        else:
            messages.success(request, ("Les teves paraules clau no coincideixen amb cap client, "
                                       "revisa-les o contacta amb l'administrador del directori."))
            return render(request, "idverification/select_user.html", {"dir": dir})


def add_credentials(request, dir_id, client_id):
    dir = Directory.objects.get(id=dir_id)
    client = Client.objects.get(id=client_id)
    if request.method == "GET":
        return render(request, "idverification/add_credentials.html", {"dir": dir, "key_words": client.key_words})
    if request.method == "POST":
        if client.credentials:
            client.credentials.delete()
        client.credentials = request.FILES.get('credentials')
        client.save()

        detected_letters = extract_letters(client.credentials.path)
        print(detected_letters)
        if detected_letters == "error":
            messages.success(request, ("Hi ha hagut un error inesperat processant la teva imatge."))
            return render(request, "idverification/add_credentials.html",
                          {"dir": dir, "key_words": client.key_words})
        if detected_letters is None:
            messages.success(request, ("No s'a trobat cap paraula a la imatge"))
            return render(request, "idverification/add_credentials.html",
                          {"dir": dir, "key_words": client.key_words})
        elif detected_letters == "no face":
            messages.success(request, ("No s'a trobat cap rostre a la teva imatge, torna-ho a intentar."))
            return render(request, "idverification/add_credentials.html",
                          {"dir": dir, "key_words": client.key_words})
        for word in client.key_words.split():
            if not any(word.lower() in detected_word.lower() for detected_word in detected_letters):
                messages.success(request, ("Aquest document no conté les teves paraules clau "
                                           "les paraules detectades son:" + str(detected_letters)))
                return render(request, "idverification/add_credentials.html",
                              {"dir": dir, "key_words": client.key_words})

        if client.user:
            client.user.delete()
        user = User(username=str(dir.id) + "_" + client.key_words)
        user.save()
        client.user = user
        client.save()
        return redirect("idverification:identity_check", dir_id=dir.id, user_id=client.user.id,
                        credentials_path=client.credentials.path)


def identity_check(request, dir_id, user_id, credentials_path):
    global dir_id_g
    dir_id_g = dir_id
    global user_id_g
    user_id_g = user_id
    global credentials_path_g
    credentials_path_g = credentials_path

    return render(request, 'idverification/id_camera.html')


def gen_frame(request, camera):
    global credentials_path_g
    checker = Id_camera_checker(credentials_path_g)
    while True:
        frame = camera.get_frame()
        result = checker.process_frame(frame)
        if result[0] == True:
            global id_frame_g
            id_frame_g = result[2]

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + result[1] + b'\r\n\r\n')
        time.sleep(0.1)


def video_feed(request):
    global camera_g
    camera_g = VideoCamera()
    return StreamingHttpResponse(gen_frame(request, camera_g),
                                 content_type='multipart/x-mixed-replace; boundary=frame')


def check_complete(request):
    global id_frame_g
    if id_frame_g is not None:
        return redirect('idverification:identity_check2')
    else:
        messages.success(request, ("Encara no s'ha validat el document, segueix intentant-ho. "
                                   "Si segueix sense funcionar prova a canviar l'iluminació de l'habitació"))
        global dir_id_g
        global user_id_g
        global credentials_path_g
        return redirect("idverification:identity_check",
                        dir_id=dir_id_g,
                        user_id=user_id_g,
                        credentials_path=credentials_path_g)


def identity_check2(request):
    return render(request, 'idverification/face_camera.html')


def gen_frame2(request, camera):
    global credentials_path_g
    face_checker = Face_camera_check(credentials_path_g)
    while True:
        frame = camera.get_frame()
        result = face_checker.process_frame(frame)
        if result[0] == True:
            global face_frame_g
            face_frame_g = result[3]
            global other_faces_g
            other_faces_g = result[2]

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + result[1] + b'\r\n\r\n')

        time.sleep(0.1)


def check_complete2(request):
    global face_frame_g
    if face_frame_g is None:
        messages.success(request, ("Encara no s'ha validat el teu rostre, segueix intentant-ho. "
                                   "Si segueix sense funcionar prova a canviar l'iluminació de l'habitació"))
        return redirect("idverification:identity_check2")

    global user_id_g
    user = User.objects.get(id=user_id_g)
    global dir_id_g
    dir = Directory.objects.get(id=dir_id_g)
    global id_frame_g

    if user_id_g != dir.user.id:
        client = client = Client.objects.get(user=user)

        num_attempt = LoginAttempt.objects.filter(client=client).count()

        id_path = 'attempts/client_' + str(client.id) + '/attempt' + str(num_attempt) + '/id_frame.jpg'
        face_path = 'attempts/client_' + str(client.id)+ '/attempt' + str(num_attempt) + '/face_frame.jpg'

        result = cv2.imwrite(id_path, id_frame_g)
        cv2.imwrite(face_path, face_frame_g)
        attempt = LoginAttempt.objects.create(client=Client.objects.get(user=user),
                                              id_frame=id_path,
                                              face_frame=face_path)

        global other_faces_g

        if other_faces_g is not None:
            if len(other_faces_g) > 0:
                path_img = 'attempts/client_' + str(client.id) + '/attempt' + str(num_attempt) + '/failed_face1.jpg'
                cv2.imwrite(path_img, other_faces_g[0])
                attempt.failed_frame1 = path_img
            if len(other_faces_g) > 1:
                path_img = 'attempts/client_' + str(client.id) + '/attempt' + str(num_attempt) + '/failed_face2.jpg'
                cv2.imwrite(path_img, other_faces_g[1])
                attempt.failed_frame2 = path_img
            if len(other_faces_g) > 2:
                path_img = 'attempts/client_' + str(client.id) + '/attempt' + str(num_attempt) + '/failed_face3.jpg'
                cv2.imwrite(path_img, other_faces_g[2])
                attempt.failed_frame3 = path_img
            if len(other_faces_g) > 3:
                path_img = 'attempts/client_' + str(client.id) + '/attempt' + str(num_attempt) + '/failed_face4.jpg'
                cv2.imwrite(path_img, other_faces_g[3])
                attempt.failed_frame4 = path_img
            if len(other_faces_g) > 4:
                path_img = 'attempts/client_' + str(client.id) + '/attempt' + str(num_attempt) + '/failed_face5.jpg'
                cv2.imwrite(path_img, other_faces_g[4])
                attempt.failed_frame5 = path_img

        attempt.save()

    global camera_g
    camera_g.__del__()

    login(request=request, user=user)
    if user_id_g == dir.user.id:
        return redirect("repository:dir_admin", dir_id=dir_id_g)
    else:
        return redirect("repository:dir_content", dir_id=dir_id_g)


def video_feed2(request):
    global camera_g
    return StreamingHttpResponse(gen_frame2(request, camera_g),
                                 content_type='multipart/x-mixed-replace; boundary=frame')
