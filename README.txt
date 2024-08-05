# Aplikacja do generowania artykułów w HTML - dla Oxido

## Opis

Aplikacja służy do generowania artykułów w formacie HTML. Używa API OpenAI do przetwarzania tekstu i tworzenia strukturalnych artykułów, które są następnie zapisywane w pliku HTML. Artykuł jest przekształcany w semantyczny HTML z nagłówkami, paragrafami, a także opcjonalnymi miejscami na obrazy z odpowiednimi opisami.

Aplikacja automatycznie tworzy także podgląd wygenerowanego artykułu w formie pliku HTML na podstawie szablonu, który może być następnie użyty do publikacji na stronie internetowej.

## Funkcje aplikacji

- Generowanie artykułów w HTML: Konwertuje tekst w odpowiednią strukturę HTML z nagłówkami, paragrafami, a także dodanymi znacznikami `<img>` i `<figcaption>` dla obrazów.
- Podział na części: Artykuł jest dzielony na mniejsze fragmenty (chunks) w celu przetworzenia przez API OpenAI, aby uniknąć przekroczenia limitu tokenów.
- SEO: Aplikacja dba o odpowiednią strukturę HTML z nagłówkami i semantycznymi tagami, zapewniając lepszą indeksację w wyszukiwarkach.
- Szablon HTML: Zastosowanie szablonu do wyświetlania wygenerowanego artykułu, w tym dodanie marginesów, justowania tekstu i przestrzeni przed nagłówkami.
  
## Wymagania

Aby uruchomić aplikację, musisz mieć zainstalowane następujące narzędzia:

- Python 3.7 lub nowszy
- Biblioteka `fastapi` (do uruchamiania aplikacji)
- Biblioteka `openai` (do komunikacji z OpenAI API)
- Biblioteka `uvicorn` (serwer do uruchamiania aplikacji FastAPI)
- Plik konfiguracyjny `config.ini` zawierający Twój klucz API z OpenAI


## Instalacja

1. Zainstaluj wymagane biblioteki:

   Użyj poniższego polecenia, aby zainstalować wszystkie zależności:

   ```bash
   pip install -r requirements.txt


2. Skonfiguruj OpenAI API:

Utwórz plik konfiguracyjny config.ini w katalogu głównym projektu. Plik powinien zawierać Twój klucz API OpenAI, np.:

ini
Skopiuj kod
[openai]
api_key = Twój_Klucz_API

[LanguageModel]
model = gpt-3.5-turbo  # lub inny model, którego używasz

Na potrzeby zadania w pliku config.ini umieszczono już klucz API OpenAI.


3. Przygotuj plik tekstowy:

Aplikacja oczekuje pliku input.txt w katalogu głównym projektu. W tym pliku powinien znajdować się tekst, który chcesz przetworzyć na HTML.


4. Szablon HTML:

Upewnij się, że plik szablon.html znajduje się w katalogu głównym projektu. Jest to plik szablonu HTML, w którym artykuł będzie umieszczany. Jeśli chcesz dostosować finalny wygląd artykułu, edytuj ten plik.


## Uruchamianie aplikacji

1. Uruchom aplikację.

Aby uruchomić aplikację, uruchom poniższe polecenie w terminalu (w katalogu głównym projektu):

cd "ścieżka do folderu głównego aplikacji"

.\venv\Scripts\activate

uvicorn app:app --reload

Serwer będzie dostępny pod adresem http://127.0.0.1:8000.


2. Testowanie aplikacji.

Po uruchomieniu serwera możesz przetestować działanie aplikacji, otwierając przeglądarkę i przechodząc do http://127.0.0.1:8000.
Aby przetworzyć artykuł, otwórz nowy terminal nie zamykając poprzedniego, następnie przejdź do folderu głównego projektu używaj następujących komend:

cd "ścieżka do folderu głównego aplikacji"

curl -X POST "http://127.0.0.1:8000/process_text" -H "accept: application/json"


3. Plik HTML z artykułem:

Po przetworzeniu tekstu przez aplikację, wygenerowany artykuł zostanie zapisany w pliku artykul.html. Dodatkowo, aplikacja utworzy podgląd w pliku podglad.html, który będzie zawierał artykuł w szablonie HTML.

4. Przykładowe zapytanie
Aby przetworzyć tekst z pliku input.txt, wyślij zapytanie POST na endpoint /process_text. Aplikacja automatycznie zidentyfikuje plik i przekaże go do przetworzenia przez API OpenAI.



Aplikacja została stworzona jako zadanie testowe dla zespołu Oxido.
