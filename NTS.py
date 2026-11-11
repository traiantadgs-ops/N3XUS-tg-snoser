import requests
import random
import string
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from colorama import Fore, Style, init

init()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def generate_random_phone():
    return f"+79{ ''.join( random.choice( '0123456789' ) for _ in range ( 9 ) ) }"

def generate_random_email():
    domains = [ "gmail.com", "mail.ru", "rambler.ru", "ya.ru" ]
    name_length = random.randint( 5, 10 )
    letters = "abcdefghijklmnopqrstuvwxyz1234567890"
    email_name = ''.join( random.choice( letters ) for _ in range (name_length ) )
    return f"{ email_name }@{random.choice( domains ) }"

# ПОЛНЫЙ СБОРНИК КАТЕГОРИЙ И ТЕКСТОВ ЖАЛОБ
complaint_types = {
    "Спам": [
        "Пользователь {user} ID: {user_id} использует чат для рассылки рекламы и спама, что нарушает правила сообщества. Прошу удалить его сессию и заблокировать возможность отправки нежелательных сообщений.",
        "Здравствуйте, хочу пожаловаться на {user} ID: {user_id}, он использует спам для продвижения своего канала из-за чего невозможно общаться в группе, прошу принять меры по удалению аккаунта. Спасибо",
        "Доброго времени суток, прошу принять меры по рассылке спама. ID: {user_id} пользователя.",
        "Жалоба на рассылку рекламы. Пользователь {user} с ID: {user_id} спамит по группам, прошу принять меры",
        "Hello, I want to complain about ID: {user_id}, he uses spam to promote his channel, which makes it impossible to communicate in the group, please take steps to delete the account. Thank you",
        "Good day, I ask you to take measures to send spam. ID: {user_id} of the user.",
        "Complaint about sending advertisements. User with ID: {user_id} is spamming groups, please take action"
    ],
    "Порнография": [
        "Добрый день, прошу заблокировать доступ к порнографическому контенту. Акаунту {user} с  ID: {user_id}. Проблема в том что он занимается продажей детской порнографией",
        "Здравствуйте, хочу подать жалобу на порнографию.  Пользиватель {user} с  ID: {user_id} продает детскую порнографию, прошу принять меры по удалению акаунта. Спасибо",
        "Данный пользиватель {user} с ID: {user_id} растространяет запрешеный детский контент (дп,цп) прошу вас удалить данный акаунт. Спасибо",
        "Good afternoon, please block access to pornographic content. Account with ID: {user_id}. The problem is that it sells child pornography",
        "Hello, I want to file a complaint about pornography. User ID: {user_id} sells child pornography, please take steps to delete the account. Thank you",
        "This user with ID: {user_id} distributes prohibited children's content (dp, cp), I ask you to delete this account. Thank you",
        "Пользователь {user_id} распространяет порнографические материалы. Прошу заблокировать его аккаунт за нарушение правил платформы. Ссылка на материалы: {id}",
        "Обнаружено распространение порнографии пользователем {user_id}. Прошу принять меры. Ссылка на материалы: {id}",
        "Добрый день, прошу заблокировать аккаунт с  ID: {user_id}. Проблема в том,что он занимается продажей детской порнографией, вот ссылка на нарушение: {id}",
        "Здравствуйте, хочу подать жалобу на порнографию.  Пользователь с  ID: {user_id} продает детскую порнографию,вот ссылка на нарушение:{id},прошу принять меры по удалению акаунта. Спасибо",
        "Данный пользователь с ID: {user_id} растространяет запрещеный детский контент (дп,цп) прошу вас удалить данный акаунт.Также ссылка на нарушение:{id}.Спасибо",
        "Добрый день, прошу заблокировать аккунт с айди: {user_id} за распространение порнографии, точнее этот человек размещает порнографию, а также детскую порнографию в чатах ({id}) и так далее, что может повлиять на психику людей, которые находятся в этих чатах, а также это нарушает вашу политику, прошу заблокировать данного человека, также на момент жалобы у этого человека на аватарке было неприличное фото, поэтому прошу вас отреагировать на это быстро и четко. Заранее спасибо!",
        "Hello, I want to file a complaint about pornography. User with ID: {user_id} sells child pornography,link to violation: {id},please take steps to delete the account. Thank you",
        "Good afternoon, please block the account with ID: {user_id}. The problem is that he is selling child pornography.Link to violation: {id}.",
        "This user with ID: {user_id} distributes prohibited children's content (dp, cp),and link to violation: {id},I ask you to delete this account. Thank you",
        "Good afternoon, I ask you to block the account with ID: {user_id} for distributing pornography, more precisely, this person posts pornography, as well as child pornography in chats and so on,link to violation: {id},which can affect the psyche of people who are in these chats, and also violates your policy, I ask you to block this person, also at the time of the complaint this person had an indecent photo on his avatar, so I ask you to respond to this quickly and clearly. Thank you in advance!" 
    ],
    "Фишинг": [
        "Здравствуйте, сообщаю о подозрительной попытке фишинга. Акк: {user} ID: {user_id}.",
        "Добрый день, прошу обратить внимание на пользивателя {user} с ID: {user_id} он создает фишинг сылки, прошу принять меры по удалению данного акаунта",
        "Жалоба на фишинг. Пожалуйста, примите меры. {user} с ID: {user_id} использует фишинг для получения личных данных других пользывателей, прошу принять меры по удалению акаунта. Спасибо",
        "Hello, I'm reporting a suspicious phishing attempt. ID: {user_id}.",
        "Good afternoon, please pay attention to the user with ID: {user_id}, he creates phishing links, please take measures to delete this account",
        "Phishing complaint. Please take action. ID: {user_id} uses phishing to obtain personal information of other users, please take action to delete the account. Thank you"    
    ],
    "Дианон": [
        "Здравствуйте уважаемая поддержка телеграмм,хочу пожаловаться на пользователя {user} с ID:{user_id} дело в том что он нарушает правила телеграмм, он продает услули деанона, занимается терроризмом , а еще хочу сообщить что он оскорбляет чужие личности! ",
        "Здравствуйте уважаемая поддержка. Пользователь {user} вашей платформы Telegram с ID: {user_id}, угрожает дean0минuзациеё и свaтuнг0м. Требую удалить его аккаунт для безопасности других пользователей.",
        "Telegram, деактивируйте аккаунт {user} с ID: {user_id}, так как с него мне поступают многочисленные угрозы дean0н0м и сват0м, пугает также моих друзей, говорит, что сольёт их данные в сеть",
        "Данный пользователь {user} с ID: {user_id}, угрожает мне д0kсинг0м и свaтuнг0м. Он хочет слить мои данные в сеть. Просьба удалить его аккаунт для безопастности",
        "Telegram, деактивируйте аккаунт {user}, Id:  {user_id}, так как с него мне поступают многочисленные угрозы дean0н0м и сват0м, пугает также моих друзей, говорит, что сольёт их данные в сеть",
        "Данный пользователь {user}, id: {user_id}, угрожает мне     д0kсинг0м и свaтuнг0м. Он хочет слить мои данные в сеть. Просьба удалить его аккаунт для безопастности.",
        "Здравствуйте уважаемая поддержка. Пользователь {user} вашей платформы Telegram с id: {user_id}, угрожает дean0минuзациеё и свaтuнг0м. Требую удалить его аккаунт для безопасности других пользователей.",
        "Привествую Вас. Я являюсь родителем моего ребёнка и ему поступют угрозы об сливе данных с данного аккаунта {user}, id:{user_id}. Прошу удалить его аккаунт, так как теперь у моего ребёнка нарушена психика!",
        "Мне сказали, что телеграм самый безопасный мессенджер, только сейчас этот пользователь {user} id: {user_id} хочет слить мои данные.",
        "Hello, dear telegram moderator, I want to complain to you about a channel that sells doxing and swatting services ID: {user_id}, I ask you to take measures to delete the account.",
        "Good day, I ask you to take action on my complaint. The telegram user under ID: {id} is engaged in selling the services of Doxing and Swatting, I ask you to take action. Thank you.",
        "This account under ID: {user_id} is engaged in doxing and swatting, please take measures to delete the account."
    ],
    "Мошенничество": [
        "Уважаемая служба поддержки!Хочу сообщить о случае мошенничества. Пользователь {user} с ID: {user_id} пишет людям и предлагает услугу по выводу Notcoin на карту. После перевода Notcoin пользователь добавляет в черный список и отказывается переводить Notcoin. Прошу принять меры по удалению аккаунта. Спасибо!",
        "Добрый день!Прошу рассмотреть жалобу на мошенничество. Пользователь {user} с ID: {user_id} занимается мошенничеством, прошу принять меры по блокировке аккаунта.",
        "Обращаюсь к вам с жалобой на пользователя {user} с ID: {user_id}. Данный пользователь обманным путем получил от меня Notcoin, пообещав вывод на карту, но после получения средств заблокировал меня. Прошу принять меры и вернуть мои средства.",
        "Прошу обратить внимание на действия пользователя {user} с ID: {user_id}.Он предлагает услуги по выводу Notcoin, но после получения оплаты отказывается выполнять свои обязательства и блокирует пользователей. Это мошенник!",
        "ВНИМАНИЕ! Мошенник!Пользователь {user} с ID: {user_id} обманывает людей, предлагая несуществующие услуги. Будьте бдительны и не переводите ему свои средства!",
        "Я стал жертвой мошенничества со стороны пользователя {user} с ID: {user_id}.Прошу принять меры по блокировке его аккаунта и возврату моих средств.",
        "Требую наказать мошенника {user} с ID: {user_id}!Он обманул меня и многих других пользователей. Прошу принять меры!",
        "Обращаюсь к вам с просьбой о помощи.Пользователь {user} с ID: {user_id} обманным путем завладел моими средствами. Прошу вернуть мои Notcoin и заблокировать мошенника.",
        "Сколько можно терпеть мошенников на вашей платформе? Пользователь с ID: {user_id} продолжает обманывать людей. Прошу принять срочные меры!",
        "Dear support service, I want to report a case of fraud. A user with ID: {user_id} writes to people and offers a service to help them withdraw notcoin to a card. After transferring the notcoin, the user is blacklisted and refuses to transfer the notcoin, I ask you to take measures to delete the account.  Thank you",
        "Good afternoon, I ask you to consider a complaint about fraud. The user with ID: {user_id} is engaged in fraud, I ask you to take measures to assign the account.",
        "Fraud complaint against user ID: {user_id}. Please take action."
    ],
    "Премиум": [
        "Good afternoon Telegram support! Account ID: {user_id} purchased premium in your messenger to send spam messages and bypass Telegram restrictions. Please check this complaint and take action!"        
    ],
    "Домогательство": [
        "I ask you to delete user ID: {user_id}, he writes to my friends and asks them to send their intimate photos, please take action",
        "I ask you to delete user ID: {user_id}, he writes to my friend who is 15 years old and asks for intimate photos, I ask you to take punitive measures.  Thank you",
        "User ID: {user_id}, writes to minors and asks for intimate photographs, please take punitive measures.",
        "User ID: {user_id}, writes to my underage friends and asks for intimate photos, please take punitive measures.",
        "User ID: {user_id}, writes to my underage friends and asks them to send him intimate photos, I ask them to take punitive measures.",
        "User ID: {user_id}, writes to my friends and asks them to send him intimate photos, I ask them to take punitive measures.  Thank you"
    ],
    "Религия": [
        "User ID: {user_id} provokes people into conflicts, and also affects religion for the sake of conflict, I ask you to take action against this user",
        "User ID: {user_id} provokes people into conflicts, please take action.  Thank you",
        "User ID: {user_id} provokes people into conflicts by affecting religions, please take measures to remove this user",
        "I ask you to delete user {user} ID: {user_id}, he provokes other users into conflicts by touching on religions and this is obscene behavior. Please treat with understanding and take punitive measures"
    ],
    "Канал": [
        "Hello, Telegram support! I want to file a complaint against the Telegram channel link: {id}, this channel distributes methods of doxing, hacking, and swatting. Please remove this channel. Thank you.",
        "Good afternoon, I want to complain about the telegram channel link: {id}, this channel publishes personal information of users, please take measures to delete the channel. Thanks.",
        "This channel: channel link {id} published my personal information without my consent. Please take action!",
        "I want to complain about the channel: channel link {id}. In the post from the date of publication, my photos and full name were published without my knowledge and consent. I ask you to remove the publication and take action against the channel that violates the confidentiality of users.",
        "Channel link {id} violates the rules of the Telegram platform by publishing personal information of users without their consent. I demand action!"
    ],
    "Группа": [
        "Hello, Telegram Support, I want to file a complaint against the group with ID: {id} for the reason: distribution of prohibited content. Please take action to block the group!",
        "Good day, I ask you to take action on my complaint. Group ID: {id} is used to distribute illegal materials, please block the group. Thanks!",
        "I want to complain about group ID: {id} for violating community guidelines, please take action."
    ],
    "Вирт": [
        "Good afternoon, Telegram support! Account {user} ID: {user_id} uses a virtual number purchased on the website for number activation. It has nothing to do with the number, the number has nothing to do with it. Please sort this out. Thanks in advance!"
    ],
    "Насилие": [        
        "Hello, Telegram support! I want to report a case of animal cruelty. User ID: {id} has shared content depicting animal abuse. I urge you to take immediate action and remove the content/block the user.",
        "I am writing to report a disturbing instance of animal abuse that I encountered on Telegram. User ID: {id} is responsible for sharing this content. I kindly request you to investigate this matter and take appropriate action to prevent further harm to animals."
    ],
    "Сессия": [
        "Здраствуйте,меня взломали и выкинули с аккаунта {user}. Теперь Я не могу зайти на аккаунт так как мгновенно выкидывают меня с аккаунта. Прошу помогите, удалите аккаунт или обнулите сессии, там было очень много важной информации. Вот мой ID: {user_id}",
        "Здраствуйте, я попался на фишинг ссылку и меня как то взломали, на моем аккаунте {user} было очень много важных вещей, поэтому прошу вас обнулите пожалуйста сессию или же удалите аккаунт.Вот мой айди: {user_id}",
        "Здравствуйте, у меня украли аккаунт {user} с айди {user_id}, при попытке зайти на него, тот кто украл аккаунт не даёт мне зайти и отключает мою сессию, прошу вас пожалуйста отключить все сессии на данном аккаунте.",
        "Hello, I fell for a phishing link and somehow got hacked, there were a lot of important things on my account {user}, so I ask you to reset the session or delete the account. Here is my ID: {user_id}",
        "Hello, my account {user} with ID {user_id} was stolen, when I try to log into it, the one who stole the account does not allow me to log in and disables my session, I ask you to please disable all sessions on this account."
    ]
}       

def get_user_input():
    clear_screen()
    user_id = input(Fore.CYAN + "   Введите ID: " + Style.RESET_ALL)
    user = input(Fore.CYAN + "   Введите @: " + Style.RESET_ALL) 
    id = input(Fore.CYAN + "   Введите cсылку на нарушение (или для сноса канала/группы): " + Style.RESET_ALL)
    total_requests = int(input(Fore.CYAN + "   Сколько всего жалоб отправить (например, 10000): " + Style.RESET_ALL))
    print(Fore.CYAN + "   Выберите тип жалобы:" + Style.RESET_ALL)
    for i, complaint_type in enumerate(complaint_types.keys()):
        print(f"   {i+1}. {complaint_type}")
    choice = int(input(Fore.CYAN + "   Выберите номер типа жалобы: " + Style.RESET_ALL)) - 1 
    chosen_complaint_type = list(complaint_types.keys())[choice]
    return user_id, user, id, total_requests, chosen_complaint_type 

active_proxies = []
proxy_lock = threading.Lock()
file_lock = threading.Lock()
is_running = True

def check_single_proxy(ip):
    """Проверяет прокси на живость"""
    proxy = {"http": f"http://{ip}", "https": f"http://{ip}"}
    try:
        test = requests.get("https://telegram.org", proxies=proxy, timeout=1.5)
        if test.status_code == 200:
            return proxy
    except:
        pass
    return None

def single_scanner_worker():
    """Один поток-сканер: качает и постоянно ищет рабочие прокси"""
    global is_running, active_proxies
    api_url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=2000&country=all&ssl=yes"
    
    while is_running:
        try:
            res = requests.get(api_url, timeout=4)
            if res.status_code == 200:
                proxies_list = [line.strip() for line in res.text.splitlines() if line.strip()]
                random.shuffle(proxies_list)
                
                for ip in proxies_list:
                    if not is_running:
                        break
                    
                    proxy = check_single_proxy(ip)
                    if proxy:
                        proxy_str = proxy['http'].replace("http://", "")
                        
                        # Сохраняем в файл рабочих прокси
                        with file_lock:
                            with open("working_proxies.txt", "a", encoding="utf-8") as f:
                                f.write(proxy_str + "\n")

                        # Добавляем в активный пул (всегда держим до 10 штук)
                        with proxy_lock:
                            if proxy not in active_proxies and len(active_proxies) < 10:
                                active_proxies.append(proxy)
        except:
            pass
        time.sleep(1)

def worker_task(user_id, user, id_link, chosen_type, sites_pool):
    """Отправка жалобы через рабочий прокси из пула"""
    global active_proxies
    
    while is_running:
        with proxy_lock:
            if active_proxies:
                proxy = random.choice(active_proxies)
                break
        time.sleep(0.2)

    if not is_running:
        return False

    proxy_str = proxy['http']
    random_site = random.choice(sites_pool)
    data = random_site['data'].copy()

    if 'tg_feedback_appeal' in data:
        data['tg_feedback_appeal'] = random.choice(complaint_types[chosen_type]).format(user_id=user_id, user=user, id=id_link)
        data['tg_feedback_email'] = generate_random_email()
        data['tg_feedback_phone'] = generate_random_phone()
    else:
        data['name'] = user
        data['email'] = f"{user_id}@example.com"
        data['message'] = random.choice(complaint_types[chosen_type]).format(user_id=user_id, user=user, id=id_link)

    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0"
        ])
    }

    session = requests.Session()
    try:
        response = session.post(random_site['url'], headers=headers, data=data, proxies=proxy, timeout=3)
        response.raise_for_status()
        print(f"{Fore.GREEN}[+] Отправлено через {proxy_str}{Style.RESET_ALL}")
        return True
    except Exception:
        # Мертвый прокси сразу вырезается из пула, а 10 сканеров тут же найдут замену
        with proxy_lock:
            if proxy in active_proxies:
                active_proxies.remove(proxy)
        return False

def main():
    global is_running
    user_id, user, id_link, total_requests, chosen_complaint_type = get_user_input()

    sites = [
        {'url': 'https://telegram.org/support?setln=ru', 'data': {'tg_feedback_appeal': '...', 'tg_feedback_email': '...', 'tg_feedback_phone': '...'}},
        {'url': 'https://telegram.org/support', 'data': {'name': '...', 'email': '...', 'message': '...'}}
    ]

    print(Fore.CYAN + "\n[i] Запускаем 10 потоков-сканеров для быстрого сбора живых прокси..." + Style.RESET_ALL)

    # Запускаем РОВНО 10 СКАНЕРОВ в фоновом режиме
    for _ in range(10):
        t = threading.Thread(target=single_scanner_worker, daemon=True)
        t.start()

    # Ждем пока наберется первая десятка для старта
    while len(active_proxies) < 10:
        print(f"   {Fore.YELLOW}[!] Накопление прокси: {len(active_proxies)}/10{Style.RESET_ALL}", end="\r")
        time.sleep(0.5)

    print(Fore.GREEN + "\n[✓] Набрано 10 рабочих прокси! Запускаем пулемёт и фоновое сохранение в working_proxies.txt...\n" + Style.RESET_ALL)

    sent_count = 0
    max_threads = 10

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = []
        
        for _ in range(total_requests):
            futures.append(executor.submit(worker_task, user_id, user, id_link, chosen_complaint_type, sites))

        for future in as_completed(futures):
            if future.result():
                sent_count += 1
            with proxy_lock:
                pool_size = len(active_proxies)
            print(f"[{Fore.YELLOW}* Успешно: {sent_count}/{total_requests} | Активных прокси в пуле: {pool_size}/10 {Style.RESET_ALL}", end="\r")

    is_running = False
    print(f"\n\n{Fore.GREEN}Все задачи выполнены! Рабочие прокси сохранены в working_proxies.txt{Style.RESET_ALL}")
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()
