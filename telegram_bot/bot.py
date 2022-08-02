from django.conf import settings


TG_API = settings.TG_API_TOKEN

def main():
    
    print(f'Im tg bot with key: \n{TG_API}')


if __name__ == '__main__':
    main()
