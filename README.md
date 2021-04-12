# ptosto_site_with_registration
Просто сайт с регистрацией

Параметры google-каптчи и e-mail-host
задаются в config.ini

В шаблон registration/register.html в тег data-sitekey 
класса "form-group g-recaptcha" задать значение
SITE KEY, полученное от Google Captcha

При попытке входа на сайт с неподтверждёнными
учётными данными вылезает жёлтая плашка вверху
главной панели.