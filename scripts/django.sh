#!/usr/bin/env bash

run_migrations() {

    log_info "检查 Django Models"

    if [[ -n "$PRIORITY_APP" ]]; then
        MANAGE makemigrations "$PRIORITY_APP" --noinput
    fi

    for app in $APPS_LIST; do

        [[ "$app" == "$PRIORITY_APP" ]] && continue

        MANAGE makemigrations "$app" --noinput
    done

    MANAGE makemigrations --noinput

    log_info "执行 migrate"

    MANAGE migrate --noinput
}

ensure_superuser() {

    log_info "检查超级用户"

    MANAGE shell -c "
from django.contrib.auth import get_user_model

User = get_user_model()

username='${DJANGO_ADMIN_USER:-admin}'
email='${DJANGO_ADMIN_EMAIL:-admin@example.com}'
password='${DJANGO_ADMIN_PASSWORD:-Admin123456}'

user, created = User.objects.get_or_create(
    username=username,
    defaults={
        'email': email,
        'is_superuser': True,
        'is_staff': True,
    }
)

if created:
    user.set_password(password)
    user.save()
    print('Superuser created')
else:
    print('Superuser already exists')
"
}