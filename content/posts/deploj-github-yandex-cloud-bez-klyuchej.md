---
title: "Деплой из GitHub в Yandex Cloud без ключей: как я настроил публикацию сайта"
slug: "деплой-из-github-в-yandex-cloud-без-ключей-как-я-настроил-публикацию-сайта"
date: 2026-11-15T14:00:00+03:00
draft: false
summary: "Как сайт на Hugo сам публикуется в Yandex Object Storage после слияния в main: GitHub Actions, федерация удостоверений вместо статических ключей, команды настройки и workflow целиком. Что это изменило в работе и почему такая схема безопаснее ключа в секретах."
categories: ["Технологии"]
tags: ["self-hosted", "безопасность", "автоматизация"]
cover:
  image: "/images/github-yandex-deploy-cover.jpg"
  alt: "Рисованная иллюстрация: ветка main в репозитории, обмен токена без ключа и бакет в облаке"
---

Этот сайт собирается Hugo и лежит в бакете Yandex Object Storage. Раньше я публиковал его так: открывал терминал на Mac, запускал `./deploy.sh`, скрипт собирал сайт и заливал изменения через `yc`. Работало, но только с моего ноутбука и только пока `yc` на нём авторизован.

Теперь публикация идёт сама: я сливаю изменения в ветку `main`, GitHub Actions собирает сайт и загружает его в бакет. Ключей доступа к облаку в GitHub при этом нет. Ниже описываю схему, команды настройки и то, что она дала на практике.

## Как устроена схема

В Yandex Cloud есть федерация удостоверений рабочих нагрузок (Workload Identity Federation). Она позволяет внешней системе получить IAM-токен сервисного аккаунта, не храня никакого ключа.

Цепочка такая:

1. Задача GitHub Actions запрашивает у GitHub OIDC-токен. Это подписанный JWT, в котором записано, из какого репозитория и какой ветки идёт запуск.
2. Задача отправляет этот JWT на `auth.yandex.cloud` и просит IAM-токен нужного сервисного аккаунта.
3. Yandex Cloud проверяет подпись по открытым ключам GitHub, сверяет издателя, аудиторию и поле `sub` с настройками федерации и выдаёт IAM-токен.
4. С этим токеном `yc` загружает файлы в бакет.

Доверие задаётся одной строкой: `sub` должен быть равен `repo:<владелец>/<репозиторий>:ref:refs/heads/main`. Токен из другой ветки, другого репозитория или из pull request под это условие не подходит.

У репозиториев, созданных после 15 июля 2026 года, GitHub по умолчанию добавляет в `sub` числовые ID владельца и репозитория. Мой репозиторий старше, и у него формат прежний. Для нового репозитория точное значение нужно взять из [справочника GitHub по OIDC](https://docs.github.com/en/actions/reference/security/oidc), иначе обмен токена закончится отказом.

## Что нужно настроить в облаке

Все команды ниже выполняются один раз, под учётной записью с правами на каталог. Значения в угловых скобках подставьте свои.

Отдельный сервисный аккаунт только для деплоя:

```bash
yc iam service-account create --name github-deploy-site
```

Право загружать и удалять объекты. На отдельный бакет роль можно выдать в консоли, через API или Terraform; команды для этого в `yc` я не нашёл и выдал роль на каталог. Если в каталоге есть другие бакеты, сервисный аккаунт сможет менять и их.

```bash
yc resource-manager folder add-access-binding <ID_каталога> \
  --role storage.editor \
  --service-account-name github-deploy-site
```

Роль `storage.editor` разрешает загружать и удалять объекты, но не даёт управлять ACL и делать бакеты публичными. `storage.uploader` не подходит: с ней нельзя удалять устаревшие файлы.

Федерация для GitHub. Аудитория у GitHub по умолчанию `https://github.com/<владелец>`:

```bash
yc iam workload-identity oidc federation create \
  --name github-actions \
  --issuer "https://token.actions.githubusercontent.com" \
  --audiences "https://github.com/<владелец>" \
  --jwks-url "https://token.actions.githubusercontent.com/.well-known/jwks"
```

Из вывода нужно сохранить `id` федерации. Затем привязка сервисного аккаунта к ветке `main` конкретного репозитория:

```bash
yc iam workload-identity federated-credential create \
  --service-account-id <ID_сервисного_аккаунта> \
  --federation-id <ID_федерации> \
  --external-subject-id "repo:<владелец>/<репозиторий>:ref:refs/heads/main"
```

Проверить, что всё создалось:

```bash
yc iam workload-identity oidc federation list
yc iam workload-identity federated-credential list --service-account-id <ID_сервисного_аккаунта>
```

Последний шаг: записать ID сервисного аккаунта в переменную репозитория. Это не секрет, по нему одному токен не получить.

```bash
gh variable set YC_SA_ID --repo <владелец>/<репозиторий> \
  --body "$(yc iam service-account get github-deploy-site --format json | jq -r .id)"
```

У меня с первого раза не создалась привязка из четвёртой команды. Федерация, роль и переменная были на месте, а список привязок у аккаунта оказался пустым. Поэтому команды `list` я выполняю всегда.

## Workflow

Файл `.github/workflows/deploy.yml` делает две разные вещи. Для pull request он только собирает сайт, для `main` собирает и публикует.

```yaml
name: deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

concurrency:
  group: deploy-${{ github.ref }}
  cancel-in-progress: false

permissions:
  contents: read

env:
  HUGO_VERSION: 0.170.0

jobs:
  build:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Установить Hugo extended
        run: |
          curl -fsSL -o /tmp/hugo.deb \
            "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-amd64.deb"
          sudo dpkg -i /tmp/hugo.deb
      - name: Собрать сайт
        run: hugo --minify --cleanDestinationDir

  deploy:
    if: github.event_name != 'pull_request' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    steps:
      # checkout и установка Hugo такие же, как в build
      - name: Установить Yandex Cloud CLI
        run: |
          curl -fsSL https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash -s -- -i "$HOME/yandex-cloud" -n
          echo "$HOME/yandex-cloud/bin" >> "$GITHUB_PATH"
      - name: Получить IAM-токен через федерацию
        # см. следующий раздел
      - name: Опубликовать
        run: ./deploy.sh
```

`fetch-depth: 0` нужен, потому что Hugo берёт дату изменения страниц из истории git. С неполной историей в sitemap оказались бы неверные даты.

`id-token: write` есть только у задачи `deploy`. Без этого разрешения GitHub не выдаёт OIDC-токен, поэтому задача сборки для pull request до облака дотянуться не может.

## Обмен токена

Шаг получения IAM-токена занимает два запроса `curl`:

```bash
test -n "$SA_ID" || { echo "::error::Не задана переменная репозитория YC_SA_ID"; exit 1; }

# 1. OIDC-токен от GitHub с нужной аудиторией
JWT=$(curl -fsS -H "Authorization: bearer $ACTIONS_ID_TOKEN_REQUEST_TOKEN" \
  "$ACTIONS_ID_TOKEN_REQUEST_URL&audience=$AUDIENCE" | jq -r .value)
echo "::add-mask::$JWT"

# 2. Обмен на IAM-токен сервисного аккаунта
IAM=$(curl -fsS -X POST https://auth.yandex.cloud/oauth/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'grant_type=urn:ietf:params:oauth:grant-type:token-exchange' \
  --data-urlencode 'requested_token_type=urn:ietf:params:oauth:token-type:access_token' \
  --data-urlencode "audience=$SA_ID" \
  --data-urlencode "subject_token=$JWT" \
  --data-urlencode 'subject_token_type=urn:ietf:params:oauth:token-type:id_token' \
  | jq -r .access_token)
test -n "$IAM" && test "$IAM" != null || { echo "::error::Обмен токена не удался"; exit 1; }
echo "::add-mask::$IAM"
echo "YC_IAM_TOKEN=$IAM" >> "$GITHUB_ENV"
```

Здесь две вещи легко перепутать. `AUDIENCE` в первом запросе равна аудитории федерации, то есть `https://github.com/<владелец>`. А `audience` во втором запросе равна ID сервисного аккаунта, чей токен нужен.

`::add-mask::` скрывает оба токена в журнале запуска. IAM-токен по документации действует не больше 12 часов и существует только в окружении этой задачи.

`yc` читает токен из переменной `YC_IAM_TOKEN` и работает без профиля. На этом я споткнулся: мой `deploy.sh` перед загрузкой проверял `yc config list` и требовал выполнить `yc init`. На ноутбуке профиль был, на чистой машине GitHub его нет, и первый деплой остановился на этой проверке, до загрузки файлов. Исправление в одну строку:

```bash
if [ -z "${YC_IAM_TOKEN:-}" ] && ! yc config list &> /dev/null; then
    echo "Yandex CLI не настроен! Выполните: yc init"
    exit 1
fi
```

Отладить такое заранее нельзя: федерация выдаёт токен только для `main`, поэтому первая настоящая проверка случается после слияния. Бакет при этом не пострадал, скрипт упал раньше загрузки.

## Что изменилось на практике

**Публикация больше не привязана к ноутбуку.** Статью можно слить в `main` с телефона через веб-интерфейс GitHub, дальше всё произойдёт без меня. Так ушла на сайт статья про диски для NAS: публикация 2 минуты 21 секунду, 40 загруженных файлов и 26 адресов, отправленных поисковикам через IndexNow.

**Pull request проверяет сборку.** Если в шаблоне ошибка, Hugo упадёт в PR, а не на сайте. Сборка в PR у меня идёт около полутора минут.

**Сборка идёт из чистой копии репозитория.** Папка сайта у меня лежит в iCloud, и он время от времени создаёт копии файлов с суффиксом « 2». Перед публикацией прошлой статьи таких копий нашлось 14, две из них добавляли на сайт лишние страницы. На ноутбуке `deploy.sh` приходится от этого защищать отдельным фильтром. В GitHub Actions таких файлов нет: туда попадает только то, что лежит в git.

**Каждая публикация остаётся в истории.** Во вкладке Actions видно, какой коммит, когда и с каким результатом выкладывался, и журнал загрузки. Первый полный деплой после редизайна шёл 7 минут 15 секунд: загружено 524 файла, удалено 334 устаревших.

**Два деплоя не идут одновременно.** Блок `concurrency` ставит второй запуск в очередь, пока первый не закончится. Без этого два быстрых слияния подряд могли бы загружать и удалять файлы наперегонки.

**Не нужно следить за токеном на ноутбуке.** Раньше `yc` на Mac хранил мой OAuth-токен. Когда `yc` перестал принимать OAuth-токены, выданные после 1 июня 2026 года, пришлось обновлять `yc` и заново входить через браузер. Для CI этот вопрос больше не стоит.

## Почему это безопасно

**В GitHub нечего украсть.** Обычный способ дать CI доступ к облаку: создать статический ключ сервисного аккаунта и положить его в секреты репозитория. Такой ключ живёт, пока его не отзовут, и если он утечёт через журнал, сторонний action или скомпрометированный аккаунт, им можно пользоваться откуда угодно. При федерации в репозитории лежит только ID сервисного аккаунта, по которому токен не получить.

**Токен выдаётся только ветке main этого репозитория.** Yandex Cloud проверяет подпись GitHub и поле `sub`. Форк, другая ветка или чужой репозиторий получат отказ, даже если знают ID сервисного аккаунта и федерации.

**Pull request не может трогать облако.** У задачи сборки нет `id-token: write`, и OIDC-токен ей не выдаётся. Если PR изменит сам workflow и всё-таки запросит токен, в его `sub` будет `pull_request`, а не `ref:refs/heads/main`, и Yandex Cloud откажет в обмене.

**Токен короткий и скрытый.** IAM-токен действует не больше 12 часов, а не годы, и маскируется в журнале. После завершения задачи машина GitHub уничтожается вместе с окружением.

**У сервисного аккаунта минимум прав.** Отдельный аккаунт с ролью `storage.editor` работает с бакетами и объектами, но не управляет ACL и публичным доступом. Создавать ВМ или читать секреты он не может.

У схемы есть ограничения:

* опубликовать сайт может любой, кто может писать в `main`. Защиту ветки и обязательный PR стоит включить в настройках репозитория;
* у меня роль выдана на весь каталог, а не на один бакет;
* если переименовать репозиторий или передать его другому владельцу, GitHub переведёт его на новый формат `sub`, и привязку в Yandex Cloud придётся пересоздать;
* сторонние actions лучше закреплять по хешу коммита, а не по тегу вроде `@v4`. У меня из сторонних только `actions/checkout`, но правило общее.

## Итог

Настройка заняла пять команд в облаке и один файл workflow. Взамен публикация идёт из любого места, сборка проверяется до слияния, каждая выкладка остаётся в журнале, а долгоживущих ключей в GitHub нет совсем. Если вы публикуете статический сайт в Object Storage вручную, эту схему можно повторить почти дословно: поменяются ID, имя репозитория и, для новых репозиториев, формат `sub`.

## Полезные ссылки

* [Yandex Cloud: интеграция с GitHub через федерацию удостоверений](https://yandex.cloud/ru/docs/tutorials/security/wlif-github-integration)
* [Yandex Cloud: настройка федерации удостоверений рабочих нагрузок](https://yandex.cloud/ru/docs/iam/operations/wlif/setup-wlif)
* [Yandex Cloud: роли Object Storage](https://yandex.cloud/ru/docs/storage/security/)
* [Workflow этого сайта на GitHub](https://github.com/skvtmb/starodubov.pro/blob/main/.github/workflows/deploy.yml)
* [CMR и SMR: какие диски ставить в NAS](/cmr-и-smr-какие-диски-ставить-в-nas-и-почему-das-на-usb-хуже-nas/): статья, опубликованная этой схемой
