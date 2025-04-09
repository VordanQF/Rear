from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView as BaseLoginView
from .forms import SignUpForm, LoginForm, ProfileUpdateForm, HelpRequestForm
from .models import HelpRequest
import hmac
import hashlib
import time
import json
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from .models import User
from django.conf import settings
def stories(request):
    return render(request, 'main/stories.html')


def support(request):
    return render(request, 'main/support.html')


def glav(request):
    return render(request, 'main/index.html')


@csrf_exempt
def sql_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            sql = data.get('sql')
            params = data.get('params', [])

            if not sql:
                return JsonResponse({'error': 'sql не передан'}, status=400)

            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                # если это SELECT
                if cursor.description:
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    result = [dict(zip(columns, row)) for row in rows]
                    return JsonResponse({'result': result})
                else:
                    return JsonResponse({'result': 'ok'})  # для insert/update/delete

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Only POST allowed'}, status=405)


def profile_view(request):
    user = request.user
    help_requests = user.help_requests.all() if user.role == 'user' else None
    assigned_requests = user.assigned_requests.all() if user.role == 'volunteer' else None
    mentor_profile = getattr(user, 'mentor_profile', None)

    return render(request, 'main/profile.html', {
        'user': user,
        'help_requests': help_requests,
        'assigned_requests': assigned_requests,
        'mentor_profile': mentor_profile,
    })


def create_help_request(request):
    if request.method == 'POST':
        form = HelpRequestForm(request.POST)
        if form.is_valid():
            help_request = form.save(commit=False)
            help_request.user = request.user
            help_request.save()
            return redirect('help_requests_list')
    else:
        form = HelpRequestForm()

    return render(request, 'main/create_help_request.html', {'form': form})


def help_requests_list(request):
    requests = HelpRequest.objects.filter(user=request.user)
    return render(request, 'main/help_requests_list.html', {'requests': requests})



def verify_phone(request):
    step = 'enter_phone'  # Начинаем с шага ввода номера
    message = ''
    status = 'success'

    # Эталонный код для проверки
    correct_code = '1234'

    if request.method == 'POST':
        step = request.POST.get('step')  # Получаем текущий шаг

        if step == 'send_code':
            phone_number = request.POST.get('phone')
            if phone_number:
                # Сохраняем номер телефона в сессии (для дальнейших целей, если нужно)
                request.session['phone_number'] = phone_number

                # Переходим к шагу ввода кода
                step = 'enter_code'  # Переходим к шагу ввода кода

            else:
                status = 'error'


        elif step == 'verify_code':
            entered_code = request.POST.get('code')
            # Логика сравнения введенного кода с эталонным значением
            if entered_code == correct_code:
                # Если код правильный, помечаем пользователя как верифицированного
                request.user.verified = True
                request.user.save()
                return redirect('glav')  # Перенаправляем на главную страницу
            else:
                status = 'error'
                step = 'enter_code'  # Остаёмся на шаге ввода кода

    return render(request, 'main/edit_profile.html', {
        'step': step,
        'status': status
    })

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.city = request.POST.get('city', '')
            user.role = request.POST.get('role', 'user')
            user.phone_number = request.POST.get('phone_number', '')
            user.bio = request.POST.get('bio', '')

            user.save()
            login(request, user)
            return redirect('about/edit')
        else:
            return redirect(f'/login/?open=true&errorname=true')
    return render(request, 'registration/login.html', {'form': SignUpForm()})


def login_view(request):
    form = LoginForm(data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('glav')
            else:
                return redirect(f'/login/?error=true')

    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


class CustomLoginView(BaseLoginView):
    def get_redirect_url(self):
        redirect_to = super().get_redirect_url()
        params = self.request.GET.urlencode()
        if params:
            return f"{redirect_to}?{params}"
        return redirect_to

@csrf_exempt
def telegram_login(request):
    # Логирование метода запроса для отладки
    print("Request method:", request.method)

    # Проверка, что запрос — GET
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    # Получаем параметры из GET-запроса
    data = request.GET.dict()

    # Извлекаем hash, если он есть, или возвращаем ошибку
    check_hash = data.pop("hash", None)
    if not check_hash:
        return JsonResponse({"error": "Missing hash"}, status=400)

    # Создание строки для проверки данных
    data_check_string = "\n".join([f"{k}={data[k]}" for k in sorted(data)])

    # Вычисляем хэш с использованием токена бота
    secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    # Сравниваем вычисленный хэш с переданным
    if calculated_hash != check_hash:
        return JsonResponse({"error": "Invalid hash"}, status=403)

    # Проверяем, что срок действия логина не истек (время не должно превышать 24 часа)
    if time.time() - int(data.get("auth_date", 0)) > 86400:
        return JsonResponse({"error": "Login expired"}, status=403)

    # Извлекаем данные пользователя
    telegram_id = data.get("id")
    username = data.get("username", f"user_{telegram_id}")
    first_name = data.get("first_name", "")
    last_name = data.get("last_name", "")
    photo_url = data.get("photo_url")

    # Находим или создаем пользователя
    user, created = User.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
        }
    )

    # Если пользователь уже существует, обновляем его данные
    if not created:
        user.username = username
        user.first_name = first_name
        user.last_name = last_name

    # Если есть URL фотографии, обновляем аватар
    if photo_url:
        user.avatar = photo_url

    # Сохраняем данные пользователя
    user.save()

    # Авторизация пользователя
    login(request, user)

    # Перенаправляем на главную страницу или личный кабинет
    return HttpResponseRedirect("/")  # редирект на главную или в ЛК