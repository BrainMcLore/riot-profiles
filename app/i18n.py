"""UI catalogs. Portuguese strings target Portugal (pt-PT), not Brazil."""
import json
from .core import atomic_json

LANGUAGES = {'ru': 'Русский', 'en': 'English', 'uk': 'Українська', 'pt-PT': 'Português (Portugal)'}

# Each row is Russian / English / Ukrainian / European Portuguese.
ROWS = [
('Отмена', 'Cancel', 'Скасувати', 'Cancelar'),
('Сохранить', 'Save', 'Зберегти', 'Guardar'),
('НЕОФИЦИАЛЬНЫЙ ПРОЕКТ  •  v', 'UNOFFICIAL PROJECT  •  v', 'НЕОФІЦІЙНИЙ ПРОЄКТ  •  v', 'PROJETO NÃO OFICIAL  •  v'),
('ТВОИ ПРОФИЛИ', 'YOUR PROFILES', 'ТВОЇ ПРОФІЛІ', 'OS TEUS PERFIS'),
('+ Добавить профиль', '+ Add profile', '+ Додати профіль', '+ Adicionar perfil'),
('Переименовать', 'Rename', 'Перейменувати', 'Mudar o nome'),
('Удалить профиль', 'Delete profile', 'Видалити профіль', 'Eliminar perfil'),
('Выбери профиль', 'Choose a profile', 'Вибери профіль', 'Escolhe um perfil'),
('Отдельные приложения, аккаунты и сохранения для каждого профиля.', 'Separate apps, accounts and saved data for each profile.', 'Окремі застосунки, облікові записи та збереження для кожного профілю.', 'Aplicações, contas e dados guardados separados para cada perfil.'),
('▶  ЗАПУСТИТЬ', '▶  LAUNCH', '▶  ЗАПУСТИТИ', '▶  INICIAR'),
('Открыть Riot Mobile', 'Open Riot Mobile', 'Відкрити Riot Mobile', 'Abrir Riot Mobile'),
('Ярлык профиля', 'Profile shortcut', 'Ярлик профілю', 'Atalho do perfil'),
('Холодный запуск', 'Cold boot', 'Холодний запуск', 'Arranque a frio'),
('Закрыть Android', 'Close Android', 'Закрити Android', 'Fechar Android'),
('Android готов.', 'Android is ready.', 'Android готовий.', 'O Android está pronto.'),
('Первый шаг: установи компоненты Android. Android Studio не нужна.', 'First, install the Android components. Android Studio is not required.', 'Спочатку встанови компоненти Android. Android Studio не потрібна.', 'Primeiro, instala os componentes do Android. Não precisas do Android Studio.'),
('Установить Android', 'Install Android', 'Встановити Android', 'Instalar Android'),
('ТВОЙ ПРОФИЛЬ.\nТВОЁ ПРОСТРАНСТВО.', 'YOUR PROFILE.\nYOUR SPACE.', 'ТВІЙ ПРОФІЛЬ.\nТВІЙ ПРОСТІР.', 'O TEU PERFIL.\nO TEU ESPAÇO.'),
('Профиль', 'Profile', 'Профіль', 'Perfil'),
('Добавь профиль и выбери его в списке.', 'Add a profile and select it in the list.', 'Додай профіль і вибери його зі списку.', 'Adiciona um perfil e seleciona-o na lista.'),
('Добавь первый профиль', 'Add your first profile', 'Додай перший профіль', 'Adiciona o primeiro perfil'),
('Новый профиль', 'New profile', 'Новий профіль', 'Novo perfil'),
('Название профиля:', 'Profile name:', 'Назва профілю:', 'Nome do perfil:'),
('Новое название:', 'New name:', 'Нова назва:', 'Novo nome:'),
('Удалить профиль?', 'Delete profile?', 'Видалити профіль?', 'Eliminar perfil?'),
('Удалить «{name}» и ВСЕ его приложения, аккаунты и данные?\nЭто действие нельзя отменить.', 'Delete “{name}” and ALL its apps, accounts and data?\nThis cannot be undone.', 'Видалити «{name}» та ВСІ його застосунки, облікові записи й дані?\nЦю дію неможливо скасувати.', 'Eliminar «{name}» e TODAS as suas aplicações, contas e dados?\nEsta ação não pode ser anulada.'),
('Запуск: ', 'Launching: ', 'Запуск: ', 'A iniciar: '),
('Сначала закрой Android профиля, затем нажми «Холодный запуск».', 'Close this profile’s Android window first, then select Cold boot.', 'Спочатку закрий Android профілю, а потім натисни «Холодний запуск».', 'Primeiro, fecha o Android deste perfil e depois seleciona «Arranque a frio».'),
('Дожидаюсь Android. Первый запуск может занять несколько минут…', 'Waiting for Android. The first boot may take a few minutes…', 'Очікування Android. Перший запуск може тривати кілька хвилин…', 'A aguardar o Android. O primeiro arranque pode demorar alguns minutos…'),
('Открыт Riot Mobile или его страница в Google Play.', 'Riot Mobile or its Google Play page is open.', 'Відкрито Riot Mobile або його сторінку в Google Play.', 'O Riot Mobile ou a respetiva página no Google Play está aberto.'),
('Открыт профиль «{name}». Для переключения выбери другой слева и нажми «Запустить».', 'Profile “{name}” is open. To switch, select another profile on the left and click Launch.', 'Профіль «{name}» відкрито. Щоб перемкнутися, вибери інший ліворуч і натисни «Запустити».', 'O perfil «{name}» está aberto. Para mudar, seleciona outro perfil à esquerda e clica em «Iniciar».'),
('Команда закрытия отправлена. Дождись сохранения состояния.', 'Close requested. Wait for the state to be saved.', 'Команду закриття надіслано. Дочекайся збереження стану.', 'Foi pedido o encerramento. Aguarda até o estado ficar guardado.'),
('На рабочем столе создан ярлык прямого запуска этого профиля.', 'A direct-launch shortcut was created on the desktop.', 'На робочому столі створено ярлик прямого запуску цього профілю.', 'Foi criado um atalho para este perfil no ambiente de trabalho.'),
('Android уже установлен. Добавь профиль или запусти существующий.', 'Android is already installed. Add a profile or launch an existing one.', 'Android уже встановлено. Додай профіль або запусти наявний.', 'O Android já está instalado. Adiciona um perfil ou inicia um existente.'),
('Получаю список компонентов и лицензии с серверов Google…', 'Fetching components and licences from Google…', 'Завантаження списку компонентів і ліцензій із серверів Google…', 'A obter a lista de componentes e as licenças dos servidores da Google…'),
('Установка Android • лицензии Google', 'Android setup • Google licences', 'Встановлення Android • ліцензії Google', 'Instalação do Android • licenças da Google'),
('Будут скачаны Android Emulator, ADB и Android 13 с Google Play.\nAndroid Studio не устанавливается. Загрузка: около 2 ГБ; нужно 15 ГБ на диске.', 'Android Emulator, ADB and Android 13 with Google Play will be downloaded.\nAndroid Studio is not installed. Download: about 2 GB; 15 GB disk space required.', 'Буде завантажено Android Emulator, ADB та Android 13 із Google Play.\nAndroid Studio не встановлюється. Завантаження: близько 2 ГБ; потрібно 15 ГБ на диску.', 'Serão transferidos o Android Emulator, o ADB e o Android 13 com Google Play.\nO Android Studio não é instalado. Transferência: cerca de 2 GB; são necessários 15 GB no disco.'),
('Я прочитал(а) и принимаю приведённые лицензии Google.', 'I have read and accept the Google licences above.', 'Я прочитав(-ла) та приймаю наведені ліцензії Google.', 'Li e aceito as licenças da Google apresentadas acima.'),
('Принять и установить', 'Accept and install', 'Прийняти та встановити', 'Aceitar e instalar'),
('Операция не завершена. Данные профилей сохранены.', 'The operation did not complete. Profile data has been preserved.', 'Операцію не завершено. Дані профілів збережено.', 'A operação não foi concluída. Os dados dos perfis foram preservados.'),
('Готово. Создай профиль и нажми «Запустить».', 'Ready. Create a profile and click Launch.', 'Готово. Створи профіль і натисни «Запустити».', 'Tudo pronto. Cria um perfil e clica em «Iniciar».'),
('Компоненты Android уже установлены.', 'The Android components are already installed.', 'Компоненти Android уже встановлено.', 'Os componentes do Android já estão instalados.'),
('Распаковка: ', 'Extracting: ', 'Розпакування: ', 'A extrair: '),
('Android готов. Создай профиль и запусти его.', 'Android is ready. Create and launch a profile.', 'Android готовий. Створи профіль і запусти його.', 'O Android está pronto. Cria e inicia um perfil.'),
('МБ', 'MB', 'МБ', 'MB'),
('Неподдерживаемый формат profiles.json. Данные не изменены.', 'Unsupported profiles.json format. No data was changed.', 'Непідтримуваний формат profiles.json. Дані не змінено.', 'Formato de profiles.json não suportado. Os dados não foram alterados.'),
('Повторяющийся ID профиля. Данные не изменены.', 'Duplicate profile ID. No data was changed.', 'Повторюється ID профілю. Дані не змінено.', 'ID de perfil duplicado. Os dados não foram alterados.'),
('Некорректный ID профиля.', 'Invalid profile ID.', 'Некоректний ID профілю.', 'ID de perfil inválido.'),
('Название должно содержать от 1 до 64 символов без переносов строк.', 'Use a name with 1–64 characters and no line breaks.', 'Назва має містити від 1 до 64 символів без розривів рядків.', 'O nome deve ter entre 1 e 64 caracteres, sem quebras de linha.'),
('Профиль с таким названием уже существует.', 'A profile with this name already exists.', 'Профіль із такою назвою вже існує.', 'Já existe um perfil com este nome.'),
('Это название уже занято.', 'This name is already in use.', 'Ця назва вже використовується.', 'Este nome já está a ser utilizado.'),
('Сначала закрой Android этого профиля.', 'Close this profile’s Android window first.', 'Спочатку закрий Android цього профілю.', 'Primeiro, fecha o Android deste perfil.'),
('Профиль находится за пределами каталога приложения.', 'The profile is outside the application directory.', 'Профіль розташований за межами каталогу застосунку.', 'O perfil encontra-se fora da pasta da aplicação.'),
('Сначала установи компоненты Android через кнопку «Установить Android».', 'First, install the components using Install Android.', 'Спочатку встанови компоненти кнопкою «Встановити Android».', 'Primeiro, instala os componentes através do botão «Instalar Android».'),
('Нет свободного порта Android Emulator. Закрой один из работающих экземпляров.', 'No Android Emulator port is available. Close a running device.', 'Немає вільного порту Android Emulator. Закрий один із запущених пристроїв.', 'Não há portas disponíveis para o Android Emulator. Fecha uma das instâncias em execução.'),
('Эмулятор не запустился. Смотри emulator.log в папке профиля.', 'The emulator failed to start. Check emulator.log in the profile folder.', 'Емулятор не запустився. Перевір emulator.log у папці профілю.', 'Não foi possível iniciar o emulador. Consulta emulator.log na pasta do perfil.'),
('Запуск затянулся. Подожди и повтори — данные профиля сохранены.', 'Startup is taking longer than expected. Wait and try again; profile data is safe.', 'Запуск триває довше, ніж очікувалося. Зачекай і повтори — дані профілю збережено.', 'O arranque está a demorar mais do que o previsto. Aguarda e tenta novamente; os dados do perfil estão guardados.'),
('Порт занят другим устройством. Команда не отправлена.', 'Another device is using this port. No command was sent.', 'Порт зайнятий іншим пристроєм. Команду не надіслано.', 'A porta está a ser utilizada por outro dispositivo. O comando não foi enviado.'),
('Android ещё не загрузился. Смотри журнал профиля; попробуй холодный запуск.', 'Android has not finished booting. Check the profile log or try a cold boot.', 'Android ще не завантажився. Перевір журнал профілю або спробуй холодний запуск.', 'O Android ainda não terminou o arranque. Consulta o registo do perfil ou tenta um arranque a frio.'),
('Открой Riot Mobile или Google Play вручную внутри Android.', 'Open Riot Mobile or Google Play manually inside Android.', 'Відкрий Riot Mobile або Google Play вручну в Android.', 'Abre o Riot Mobile ou o Google Play manualmente no Android.'),
('Не удалось закрыть профиль. Закрой окно Android крестиком.', 'Could not close the profile. Use the Android window’s close button.', 'Не вдалося закрити профіль. Закрий вікно Android кнопкою закриття.', 'Não foi possível fechar o perfil. Usa o botão de fechar da janela do Android.'),
('Необходимо принять лицензии скачиваемых компонентов Google.', 'Accept the Google component licences before downloading.', 'Потрібно прийняти ліцензії компонентів Google перед завантаженням.', 'É necessário aceitar as licenças dos componentes da Google antes da transferência.'),
('Нужно минимум 15 ГБ свободного места для установки и первого профиля.', 'At least 15 GB of free space is required for installation and the first profile.', 'Для встановлення та першого профілю потрібно щонайменше 15 ГБ вільного місця.', 'São necessários pelo menos 15 GB de espaço livre para a instalação e o primeiro perfil.'),
('Контрольная сумма пакета не совпала. Повтори установку.', 'Package checksum mismatch. Run setup again.', 'Контрольна сума пакета не збігається. Повтори встановлення.', 'A soma de verificação do pacote não corresponde. Repete a instalação.'),
('Установка неполная. Повтори установку компонентов.', 'Installation is incomplete. Install the components again.', 'Встановлення неповне. Повтори встановлення компонентів.', 'A instalação está incompleta. Volta a instalar os componentes.'),
('Закрой все окна Riot Profiles и повтори обновление. Данные профилей сохранены.', 'Close all Riot Profiles windows and retry the update. Profile data is safe.', 'Закрий усі вікна Riot Profiles і повтори оновлення. Дані профілів збережено.', 'Fecha todas as janelas do Riot Profiles e repete a atualização. Os dados dos perfis foram preservados.'),
('Создание ярлыков доступно в EXE-версии.', 'Shortcut creation is available in the EXE version.', 'Створення ярликів доступне в EXE-версії.', 'A criação de atalhos está disponível na versão EXE.'),
('Не удалось создать ярлык на рабочем столе.', 'Could not create a desktop shortcut.', 'Не вдалося створити ярлик на робочому столі.', 'Não foi possível criar um atalho no ambiente de trabalho.'),
('Требуется Windows x64 на процессоре Intel или AMD.', 'Windows x64 on an Intel or AMD processor is required.', 'Потрібна Windows x64 на процесорі Intel або AMD.', 'É necessário Windows x64 com um processador Intel ou AMD.'),
('Google не предлагает нужный стабильный пакет: ', 'Google does not offer the required stable package: ', 'Google не пропонує потрібний стабільний пакет: ', 'A Google não disponibiliza o pacote estável necessário: '),
('Не найден текст лицензии Google для ', 'Google licence text was not found for ', 'Не знайдено текст ліцензії Google для ', 'Não foi encontrado o texto da licença da Google para '),
('Неподдерживаемый алгоритм проверки пакета.', 'Unsupported package checksum algorithm.', 'Непідтримуваний алгоритм перевірки пакета.', 'Algoritmo de verificação do pacote não suportado.'),
('Компоненты Android разрешено скачивать только с dl.google.com.', 'Android components may only be downloaded from dl.google.com.', 'Компоненти Android можна завантажувати лише з dl.google.com.', 'Os componentes do Android só podem ser transferidos de dl.google.com.'),
('Небезопасный путь внутри ZIP.', 'Unsafe path inside the ZIP archive.', 'Небезпечний шлях у ZIP-архіві.', 'Caminho inseguro no arquivo ZIP.'),
('Символические ссылки внутри ZIP не поддерживаются.', 'Symbolic links inside ZIP archives are not supported.', 'Символічні посилання в ZIP-архівах не підтримуються.', 'Não são suportadas ligações simbólicas em arquivos ZIP.'),
('Размер загрузки превысил размер из каталога Google.', 'The download exceeded the size in the Google catalog.', 'Завантаження перевищило розмір із каталогу Google.', 'A transferência excedeu o tamanho indicado no catálogo da Google.'),
('Неожиданная структура ZIP от Google.', 'Unexpected Google ZIP structure.', 'Неочікувана структура ZIP від Google.', 'Estrutura inesperada do arquivo ZIP da Google.'),
('Неожиданная папка пакета: ', 'Unexpected package folder: ', 'Неочікувана папка пакета: ', 'Pasta de pacote inesperada: '),
('Каталог SDK находится за пределами установки.', 'The SDK folder is outside the installation directory.', 'Каталог SDK розташований за межами встановлення.', 'A pasta do SDK encontra-se fora da pasta de instalação.'),
]

CATALOGS = {language: {row[0]: row[index] for row in ROWS} for index, language in enumerate(LANGUAGES)}


def preferences(paths):
    try:
        value = json.loads((paths.data / 'settings.json').read_text(encoding='utf-8'))
        if not isinstance(value, dict):
            return {}
        return value
    except (OSError, ValueError):
        return {}


def save_preferences(paths, language, show_picker=True):
    if language not in LANGUAGES:
        raise ValueError('Unsupported language')
    existing = preferences(paths)
    existing.update(language=language, show_language_picker=bool(show_picker))
    atomic_json(paths.data / 'settings.json', existing)


class Translator:
    def __init__(self, language='en'):
        self.language = language if language in LANGUAGES else 'en'

    def __call__(self, text, **values):
        translated = CATALOGS[self.language].get(text, text)
        return translated.format(**values) if values else translated

    def message(self, text):
        """Translate backend messages without altering technical detail or names."""
        if text in CATALOGS[self.language]:
            return self(text)
        for prefix in ('Распаковка: ', 'Google не предлагает нужный стабильный пакет: ',
                       'Не найден текст лицензии Google для ', 'Неожиданная папка пакета: '):
            if text.startswith(prefix):
                return self(prefix) + text[len(prefix):]
        if text.endswith(' МБ'):
            return text[:-2] + self('МБ')
        return text
