# Создание репозитория на GitHub и деплой сайта

Пошаговая инструкция: как выложить проект в GitHub (ветка `main`) и задеплоить сайт на GitHub Pages.

## 1. Создать репозиторий на GitHub

1. Зайдите на [github.com](https://github.com) и нажмите **New repository** (или **+** → **New repository**).
2. Заполните:
   - **Repository name** — например, `starodubov.pro` или `blog`.
   - **Description** — по желанию.
   - **Public**.
   - **Не** ставьте галочки «Add a README», «Add .gitignore», «Choose a license» — в проекте уже есть свои файлы.
3. Нажмите **Create repository**.

На следующем экране GitHub покажет команды для связи с локальным репозиторием — они понадобятся в шаге 3.

---

## 2. Проверить локальный репозиторий

В каталоге проекта выполните:

```bash
# Текущая ветка (должна быть main или переименуйте)
git branch

# Если ветка называется не main, переименовать и использовать её как основную:
# git branch -M main

# Подмодуль темы должен быть инициализирован
git submodule status
```

Если подмодуль не инициализирован:

```bash
git submodule update --init --recursive
```

Убедитесь, что все нужные файлы добавлены и есть хотя бы один коммит:

```bash
git status
git add .
git status   # проверьте, что нет лишнего (секреты, public/)
git commit -m "Initial commit: Hugo site with Narrow theme"
```

---

## 3. Подключить GitHub и отправить main

Подставьте вместо `YOUR_USERNAME` и `YOUR_REPO` свой логин и имя репозитория:

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

Если `origin` уже есть и указывает на другой URL:

```bash
git remote set-url origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

Отправить ветку `main` на GitHub:

```bash
git branch -M main
git push -u origin main
```

Готово: репозиторий на GitHub, ветка `main` запушена.

---

## 4. Включить GitHub Pages и задеплоить сайт

Сайт на Hugo удобно деплоить через **GitHub Actions**: при каждом пуше в `main` собирается Hugo и результат публикуется на GitHub Pages.

### 4.1. Workflow для GitHub Actions

В репозитории уже есть файл `.github/workflows/hugo.yml`: при пуше в `main` он собирает Hugo (с подмодулем темы) и публикует результат на GitHub Pages. Ничего создавать вручную не нужно — достаточно закоммитить и запушить (см. шаг 4.3).

### 4.2. Включить Pages в настройках GitHub

1. Репозиторий на GitHub → **Settings** → **Pages**.
2. В блоке **Build and deployment**:
   - **Source:** GitHub Actions.
3. Сохраните настройки.

### 4.3. Запустить деплой

Закоммитьте и запушьте workflow:

```bash
git add .github/workflows/hugo.yml
git commit -m "Add GitHub Actions workflow for Hugo deploy"
git push origin main
```

Деплой запустится автоматически. Статус смотрите во вкладке **Actions**. После успешного выполнения сайт будет доступен по адресу:

```
https://YOUR_USERNAME.github.io/YOUR_REPO/
```

Для организации:

```
https://ORGANIZATION.github.io/YOUR_REPO/
```

### 4.4. Свой домен (опционально)

Если хотите использовать домен вроде `starodubov.pro`:

1. **Settings** → **Pages** → **Custom domain** — укажите домен и сохраните.
2. В DNS у регистратора добавьте запись (обычно CNAME или A), как подскажет GitHub.
3. В `config/_default/hugo.yaml` уже указан `baseURL: https://starodubov.pro/` — при смене домена измените его на новый URL.

---

## 5. Дальнейшая работа

- Локальная разработка: `hugo server` (сайт на http://localhost:1313).
- Публикация изменений: правки в коде и контенте → `git add` → `git commit` → `git push origin main`. После пуша GitHub Actions снова соберёт и задеплоит сайт.

---

## Важно: секреты

В репозитории не должно быть ключей, паролей и токенов. Файлы вроде `.env`, `*.pem`, `credentials` уже перечислены в `.gitignore`. Учётные данные для деплоя (например, Yandex Cloud) храните только локально или в GitHub Secrets, если понадобятся для других сценариев.
