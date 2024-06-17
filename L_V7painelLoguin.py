import io
import threading
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import requests
import tkinter as tk
from tkinter import messagebox
from PIL import ImageGrab
import pyautogui
import pytesseract
import datetime
from unidecode import unidecode
import pickle

# Diretório onde o arquivo será salvo
SAVE_FILE_PATH = "C:/Users/usuario.pkl"


class Login:
    USERNAME = "user"
    PASSWORD = "123"

    def __init__(self, parent):
        self.parent = parent
        self.parent.title("Login")
        self.parent.geometry("300x180")

        self.label_user = tk.Label(parent, text="Usuário:")
        self.label_user.pack()
        self.entry_user = tk.Entry(parent)
        self.entry_user.pack()
        self.entry_user.bind('<Return>', self.on_enter)

        self.label_password = tk.Label(parent, text="Senha:")
        self.label_password.pack()
        self.entry_password = tk.Entry(parent, show="*")
        self.entry_password.pack()
        self.entry_password.bind('<Return>', self.on_enter)

        self.save_user_var = tk.IntVar()
        self.save_user_checkbox = tk.Checkbutton(
            parent, text="Salvar usuário", variable=self.save_user_var)
        self.save_user_checkbox.pack()

        self.load_saved_username()

        self.button_login = tk.Button(
            parent, text="Login", command=self.check_login)
        self.button_login.pack()

    def on_enter(self, event):
        self.check_login()

    def check_login(self):
        user = self.entry_user.get()
        password = self.entry_password.get()
        if user.lower() == self.USERNAME and password == self.PASSWORD:
            if self.save_user_var.get() == 1:
                self.save_username(user)
                print("Username saved.")
            self.parent.destroy()
            verificador = Verificador()
            verificador.executar()
        else:
            messagebox.showerror(
                "Erro de Login", "Usuário ou senha incorretos.")

    def save_username(self, username):
        with open(SAVE_FILE_PATH, 'wb') as file:
            pickle.dump(username, file)

    def load_saved_username(self):
        try:
            with open(SAVE_FILE_PATH, 'rb') as file:
                saved_username = pickle.load(file)
                self.entry_user.insert(0, saved_username)
                self.save_user_var.set(1)
        except FileNotFoundError:
            pass


class Verificador:
    TESSERACT_CMD = r"caminho do tesseract"
    SEARCH_TERMS = ["termo1", "termo2", "termo3"]  # termos de busca2
    SEARCH_PRIMARI = ["primariterm1", "primariterm2",
                      "necessário resolver"]  # termos de busca1
    EMAIL_FROM = 'email gmail'
    EMAIL_TO = 'email a ser enviado'
    EMAIL_PASSWORD = 'senha gmail app'
    EMAIL_SUBJECT = "assunto email"
    EMAIL_BODY = "<p> body do email </p>"

    def __init__(self):
        self.verificando = False
        self.root = tk.Tk()
        self.root.title("Controle do Verificador")

        self.play_button = tk.Button(
            self.root, text="Play", command=self.iniciar_verificacao)
        self.play_button.pack()

        self.stop_button = tk.Button(
            self.root, text="Stop", command=self.parar_verificacao, state=tk.DISABLED)
        self.stop_button.pack()

    def iniciar_verificacao(self):
        self.verificando = True
        self.play_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        threading.Thread(target=self.verificar_loop).start()

    def parar_verificacao(self):
        self.verificando = False
        self.play_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.root.destroy()

    def verificar_loop(self):
        try:
            while self.verificando:
                time.sleep(1)
                largura_tela, altura_tela = pyautogui.size()
                centro_x, centro_y = largura_tela / 2, altura_tela / 2
                regiao = (0, 0, largura_tela, altura_tela)
                imagem = ImageGrab.grab(regiao)

                pytesseract.pytesseract.tesseract_cmd = self.TESSERACT_CMD
                image = imagem.convert('RGB')
                extracted_text = pytesseract.image_to_string(
                    image, lang="por").lower()
                extracted_text = unidecode(extracted_text)

                if any(unidecode(term.lower()) in extracted_text for term in self.SEARCH_PRIMARI):
                    pyautogui.moveTo(centro_x, centro_y)
                    time.sleep(1)
                    pyautogui.click(button='left')
                    time.sleep(1)
                    pyautogui.typewrite(' ')
                    time.sleep(2)

                    found_secondary_term = False
                    for i in range(3):
                        time.sleep(1)
                        tela2 = pyautogui.screenshot()
                        tela2_text = unidecode(
                            pytesseract.image_to_string(tela2, lang="por")).lower()
                        for term in self.SEARCH_TERMS:
                            if unidecode(term.lower()) in tela2_text:
                                print(f"Termo encontrado: {term}")
                                found_secondary_term = True
                                self.fazer_ligacao(term)
                                self.enviar_email(tela2)
                                time.sleep(120)
                                break

                        if found_secondary_term:
                            break

                    if not found_secondary_term:
                        pyautogui.hotkey('f12')
                else:
                    pass
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
        finally:
            self.parar_verificacao()
            self.root.quit()

    def fazer_ligacao(self, term):
        hora_atual = datetime.datetime.now().astimezone(
            datetime.timezone(datetime.timedelta(hours=-3)))
        inicio = datetime.time(22, 0)
        fim = datetime.time(5, 0)

        if inicio <= hora_atual.time() or hora_atual.time() <= fim:
            params = {
                "user": "@usertelegram",
                "text": f"{term}",
                "lang": "en-GB-Standard-B",
                "rpt": "1"
            }
        else:
            params = {
                "user": "@2usertelegram",
                "text": f"{term}",
                "lang": "en-GB-Standard-B",
                "rpt": "1"
            }

        response = requests.get(
            "http://api.callmebot.com/start.php", params=params)
        print(f"Response from CallMeBot: {response.text}")

    def enviar_email(self, imagem_anexo):
        msg = MIMEMultipart()
        msg['Subject'] = self.EMAIL_SUBJECT
        msg['From'] = self.EMAIL_FROM
        msg['To'] = self.EMAIL_TO

        msg.attach(MIMEText(self.EMAIL_BODY, 'html'))

        img_data = io.BytesIO()
        imagem_anexo.save(img_data, format='PNG')
        img_data.seek(0)
        imagem_anexo = MIMEImage(img_data.read())
        img_data.close()
        imagem_anexo.add_header('Content-Disposition',
                                'attachment; filename="screenshot.png"')
        msg.attach(imagem_anexo)

        with smtplib.SMTP('smtp.gmail.com', 587) as s:
            s.starttls()
            s.login(self.EMAIL_FROM, self.EMAIL_PASSWORD)
            s.sendmail(self.EMAIL_FROM, self.EMAIL_TO,
                       msg.as_string().encode('utf-8'))

    def executar(self):
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    login = Login(root)
    root.mainloop()
