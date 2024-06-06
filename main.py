from google.oauth2 import service_account
from kivymd.uix.banner.banner import MDFlatButton
from kivymd.app import MDApp
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.screen import MDScreen
from kivy.metrics import dp
from kivymd.uix.screenmanager import MDScreenManager
from kivy.clock import Clock
from kivymd.uix.dialog import MDDialog
import pyrebase
from google.cloud import storage
from google.cloud import firestore
from kivy.properties import StringProperty
import os
from kivy.uix.popup import Popup
import urllib.request
import io
from kivy.uix.filechooser import FileChooserListView

# Configuração do Firebase
firebase_config = {
    "apiKey": "AIzaSyDGIpe8MXvlfSf0hlMDQpzYfxqJQW5Slz4",
    "authDomain": "doaacao-d8007.firebaseapp.com",
    "projectId": "doaacao-d8007",
    "storageBucket": "doaacao-d8007.appspot.com",
    "messagingSenderId": "514229025973",
    "appId": "1:514229025973:web:45aeba200277c3281fd2fc",
    "measurementId": "G-XBHH0SL00T",
    "databaseURL": "https://doaacao-d8007.firebaseio.com"
}

# Inicialize Pyrebase
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
# Carregar as credenciais do arquivo JSON
credentials = service_account.Credentials.from_service_account_file('doaacao-d8007-firebase-adminsdk-f1gr1-00fedc3805.json')

# Criar uma instância do cliente de armazenamento com as credenciais fornecidas
storage_client = storage.Client(credentials=credentials)

# Inicialize Firestore
cred_path = "doaacao-d8007-firebase-adminsdk-f1gr1-00fedc3805.json"  # Caminho para o arquivo de chave de conta de serviço
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
firestore_client = firestore.Client()

def enviarEspecificacoesCampanha(titulo, descricao, outrasInformacoes):
        try:
            # Adiciona as especificações da campanha à coleção "Publicacao"
            doc_ref = firestore_client.collection("Publicacao").add({
                "titulo": titulo,
                "descricao": descricao,
                "outrasInformacoes": outrasInformacoes
            })
            print("Especificação da campanha enviada com ID: ", doc_ref[1].id)
            # Aqui você pode adicionar qualquer lógica adicional, como exibir uma mensagem de sucesso para o usuário.
        except Exception as e:
            print("Erro ao enviar especificações da campanha: ", e)
            # Aqui você pode adicionar lógica para lidar com erros, como exibir uma mensagem de erro para o usuário.

class SplashScreen(MDScreen):
    pass

class LoginScreen(MDScreen):
    dialog = None

    def login_user(self):
        email = self.ids.login_email.text
        password = self.ids.login_password.text

        try:
            auth.sign_in_with_email_and_password(email, password)
            self.manager.current = 'menu_screen'
        except Exception as e:
            self.show_error_dialog("Email ou senha incorretos")

    def show_error_dialog(self, message):
        if not self.dialog:
            self.dialog = MDDialog(
                text=message,
                buttons=[
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                ],
            )
        self.dialog.text = message
        self.dialog.open()

class RegisterScreen(MDScreen):
    dialog = None

    def register_user(self):
        email = self.ids.email_field.text
        password = self.ids.password_field.text
        confirm_password = self.ids.confirm_password_field.text
        username = self.ids.username_field.text  # Obtendo o nome de usuário

        if password != confirm_password:
            self.show_error_dialog("As senhas não coincidem")
            return
        
        try:
            user = auth.create_user_with_email_and_password(email, password)
            
            # Salvar o nome de usuário, email e senha no Firestore
            user_id = user['localId']
            user_ref = firestore_client.collection("users").document(user_id)
            user_ref.set({
                "username": username,
                "email": email,
                "password": password
            })
            
            self.manager.current = 'criar_login'
        except Exception as e:
            self.show_error_dialog(f"Erro ao criar usuário: {e}")

    def show_error_dialog(self, message):
        if not self.dialog:
            self.dialog = MDDialog(
                text=message,
                buttons=[
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                ],
            )
        self.dialog.text = message
        self.dialog.open()

class ImageHandler:
    dialog = None

    @staticmethod
    def show_error_dialog(message):
        if not ImageHandler.dialog:
            ImageHandler.dialog = MDDialog(
                text=message,
                buttons=[
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=("#008080" if message.startswith("Erro") else "#FFFFFF"),
                        on_release=lambda x: ImageHandler.dialog.dismiss()
                    ),
                ],
            )
        ImageHandler.dialog.text = message
        ImageHandler.dialog.open()

    @staticmethod
    def show_info_dialog(message):
        if not ImageHandler.dialog:
            ImageHandler.dialog = MDDialog(
                text=message,
                buttons=[
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=("#008080" if message.startswith("Erro") else "#FFFFFF"),
                        on_release=lambda x: ImageHandler.dialog.dismiss()
                    ),
                ],
            )
        ImageHandler.dialog.text = message
        ImageHandler.dialog.open()

    @staticmethod
    def upload_image(file_path, success_callback, error_callback):
        try:
            # Simulando o upload de imagem
            success_callback(file_path)
        except Exception as e:
            error_callback(f"Erro ao fazer upload da imagem: {e}")


class EditarPerfil(MDScreen):
    dialog = None
    image_path = StringProperty("conta.png") # Crie uma instância de StringProperty
    selected_path = StringProperty("")

    def update_username(self):
        new_username = self.ids.new_username.text
        user = auth.current_user
        user_id = user['localId']

        try:
            user_ref = firestore_client.collection("users").document(user_id)
            user_ref.update({"username": new_username})
            self.show_info_dialog("Nome de usuário atualizado com sucesso.")
        except Exception as e:
            self.show_error_dialog(f"Erro ao atualizar nome de usuário: {e}")

    def reset_password(self):
        email = auth.current_user['email']

        try:
            auth.send_password_reset_email(email)
            self.show_info_dialog("Um email para redefinição de senha foi enviado.")
        except Exception as e:
            self.show_error_dialog(f"Erro ao enviar email de redefinição de senha: {e}")
    
    def reset_email(self):
        new_email = self.ids.new_email.text

        if not new_email:
            self.show_error_dialog("Por favor, insira um novo email.")
            return

        user = auth.current_user

        try:
            if user:
                user_id = user.get("localId")  # Este é o local correto para acessar o UID
                user_ref = firestore_client.collection("users").document(user_id)
                user_ref.update({"email": new_email})
                self.show_info_dialog("O email foi atualizado no Firestore com sucesso.")
            else:
                self.show_error_dialog("Usuário não autenticado.")
        except Exception as e:
            self.show_error_dialog(f"Erro ao redefinir email: {e}")

    def show_error_dialog(self, message):
        if not self.dialog:
            self.dialog = MDDialog(
                text=message,
                buttons=[
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                ],
            )
        self.dialog.text = message
        self.dialog.open()

    def show_info_dialog(self, message):
        if not self.dialog:
            self.dialog = MDDialog(
                text=message,
                buttons=[
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                ],
            )
        self.dialog.text = message
        self.dialog.open()
    
    def on_pre_enter(self, *args):
        self.carregar_imagem_perfil()  # Load profile image when the screen is initialized

    def on_leave(self, *args):
        # Redefine o caminho da imagem para "conta.png" ao sair da tela
        self.image_path = "conta.png"

    def carregar_imagem_perfil(self):
        # Check if there's a current user
        if auth.current_user:
            # Get the ID of the currently authenticated user
            user_id = auth.current_user['localId']

            try:
                # Get the user document reference from Firestore
                user_ref = firestore_client.collection("users").document(user_id)
                user_data = user_ref.get().to_dict()

                # Check if there's a profile image path in Firestore
                if user_data and 'profile_image_storage_path' in user_data:
                    # If there is, construct the storage URL
                    storage_path = user_data['profile_image_storage_path']
                    bucket_name = "doaacao-d8007.appspot.com"  # Replace with your bucket name
                    storage_ref = f"gs://{bucket_name}/{storage_path}"
                    self.image_path = storage_ref
                    # Display the profile image
                    self.ids.perfil_image.source = storage_ref
            except Exception as e:
                print("Error loading profile image:", e)
        else:
            print("No authenticated user.")


    def choose_image(self):
        def on_selection(instance, selected_path):
            if selected_path:
                self.selected_path = selected_path[0]
                print("Selected path:", self.selected_path)

        content = FileChooserListView(filters=['*.png', '*.jpg', '*.jpeg'])
        content.bind(selection=on_selection)

        confirm_button = MDFlatButton(text="Confirmar", size_hint_y=None, height=dp(40))
        confirm_button.bind(on_release=self.upload_selected_image)
        content.add_widget(confirm_button)

        popup = Popup(title="Escolha uma imagem", content=content, size_hint=(0.9, 0.9))
        popup.open()

    def upload_selected_image(self, instance):
        if self.selected_path:
            print("Uploading selected image...")
            self.upload_image(self.selected_path)
        else:
            self.show_error_dialog("Por favor, selecione uma imagem.")

    def upload_image(self, file_path):
        print("Upload de imagem chamado")
        ImageHandler.upload_image(
            file_path,
            success_callback=self.image_upload_success,
            error_callback=self.image_upload_error
        )

    def image_upload_success(self, image_url):
        # Obter o ID do usuário atualmente autenticado
        user_id = auth.current_user['localId']
        
        # Atualizar a referência de imagem no Firestore
        user_ref = firestore_client.collection("users").document(user_id)
        user_ref.update({"profile_image_storage_ref": image_url})

        # Exibir a imagem de perfil atualizada na interface
        self.image_path = image_url
        self.ids.perfil_image.source = image_url
        self.show_info_dialog("Foto de perfil atualizada com sucesso.")

    def image_upload_error(self, message):
        self.show_error_dialog(message)

# Classe para a tela do menu
class MenuScreen(MDScreen):
    image_path=StringProperty("conta.png")
    def on_pre_enter(self, *args):
        self.carregar_imagem_perfil()
        self.carregar_campanhas()
    def carregar_campanhas(self):
        try:
            # Obtém a referência da coleção "Publicacao"
            publicacoes_ref = firestore_client.collection("Publicacao")

            # Limpa a lista antes de adicionar novos itens
            self.ids.campanhas_list.clear_widgets()

            # Busca todas as publicações
            publicacoes = publicacoes_ref.stream()
            for publicacao in publicacoes:
                publicacao_dict = publicacao.to_dict()
                self.adicionar_postagem(
                    publicacao_dict.get("titulo", ""),
                    publicacao_dict.get("descricao", ""),
                    publicacao_dict.get("outrasInformacoes", "")
                )
        except Exception as e:
            print("Erro ao carregar campanhas: ", e)

    def adicionar_postagem(self, titulo, descricao, outras_informacoes):
        self.ids.campanhas_list.add_widget(
            Builder.load_string(f'''
BoxLayout:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(120)  # Ajuste a altura conforme necessário
    padding: dp(10)
    spacing: dp(10)
    MDCard:
        size_hint: 1, None
        height: dp(100)
        orientation: 'vertical'
        elevation: 4
        padding: dp(10)
        BoxLayout:
            orientation: 'vertical'
            spacing: dp(5)
            MDLabel:
                text: "{titulo}"
                theme_text_color: 'Primary'
                font_style: 'H6'
                size_hint_y: None
                height: self.texture_size[1]
            MDLabel:
                text: "{descricao}"
                theme_text_color: 'Secondary'
                size_hint_y: None
                height: self.texture_size[1]
            MDLabel:
                text: "{outras_informacoes}"
                theme_text_color: 'Secondary'
                size_hint_y: None
                height: self.texture_size[1]
            ''')
        )
    
    def carregar_imagem_perfil(self):
        # Verificar se há um usuário autenticado
        if auth.current_user:
            # Obter o ID do usuário autenticado
            user_id = auth.current_user['localId']

            try:
                # Obter a referência do documento do usuário no Firestore
                user_ref = firestore_client.collection("users").document(user_id)
                user_data = user_ref.get().to_dict()

                # Verificar se há uma URL de imagem de perfil no Firestore
                if user_data and 'profile_image_storage_ref' in user_data:
                    # Se houver, atualizar o caminho da imagem
                    storage_ref = user_data['profile_image_storage_ref']
                    self.image_path = storage_ref
                    # Exibir a imagem de perfil
                    self.ids.perfil_image.source = storage_ref
            except Exception as e:
                print("Erro ao carregar imagem de perfil:", e)
        else:
            print("Nenhum usuário autenticado.")

    



class CriacaoCampanha(MDScreen):
    dialog = None
    
    def enviar_especificacoes(self):
        titulo = self.ids.titulo_field.text
        descricao = self.ids.descricao_field.text
        outras_informacoes = self.ids.outras_informacoes_field.text

        # Envie as especificações da campanha para o Firebase
        enviarEspecificacoesCampanha(titulo, descricao, outras_informacoes)

        # Exibe um diálogo de sucesso ou erro
        if not self.dialog:
            self.dialog = MDDialog(
                text="Especificações da campanha enviadas com sucesso.",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                ],
            )
        self.dialog.open()

    def show_error_dialog(self, message):
        if not self.dialog:
            self.dialog = MDDialog(
                text=message,
                buttons=[
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                ],
            )
        self.dialog.text = message
        self.dialog.open()

class MinhasCampanhas(MDScreen):
    pass

class MinhasDoacoes(MDScreen):
    pass

class Favoritos(MDScreen):
    pass

class Configuracoes(MDScreen):
    pass


class App(MDApp, App):
    dialog = None
    
    def build(self):
        Window.size = (dp(300), dp(600))  
        Window.clearcolor = (1, 1, 1, 1)
        self.theme_cls.primary_palette = 'Teal'
        Builder.load_file(("main.kv"))
        global sm
        sm = MDScreenManager()
        sm.add_widget(SplashScreen())
        sm.add_widget(LoginScreen())
        sm.add_widget(RegisterScreen())
        sm.add_widget(MenuScreen())
        sm.add_widget(EditarPerfil())
        sm.add_widget(MinhasCampanhas())
        sm.add_widget(MinhasDoacoes())
        sm.add_widget(Favoritos())
        sm.add_widget(Configuracoes())
        sm.add_widget(CriacaoCampanha())
        return sm
    
    def on_start(self):
        Clock.schedule_once(self.change_screen, 3)

    def change_screen(self, dt):
        sm.current = 'criar_login'
    
    def show_alert_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                text="Tem certeza que você quer sair da sua conta?",
                buttons=[
                    MDFlatButton(
                        text = "CANCELAR",
                        theme_text_color = "Custom",
                        text_color = '#008080',
                        on_release = lambda *args: self.dialog.dismiss()
                    ),
                    MDFlatButton(
                        text = "SAIR",
                        theme_text_color = "Custom",
                        text_color = '#008080',
                        on_release = lambda *args: self.logout_and_dismiss()
                    ),
                ],
            )
        self.dialog.open()
    
    def logout_and_dismiss(self):
        # Fecha o diálogo
        self.dialog.dismiss()
        # Limpa os campos de texto
        self.clear_text_fields()
        # Define a tela atual como 'criar_login'
        self.logout()

    def clear_text_fields(self):
        # Obtém a instância do Screen 'criar_login'
        criar_login_screen = self.root.get_screen('criar_login')
        # Acessa diretamente os widgets de email e senha e define seus textos como vazios
        criar_login_screen.ids.login_email.text = ''
        criar_login_screen.ids.login_password.text = ''

    def logout(self):
        # Define a tela atual como 'criar_login'
        self.root.current = 'criar_login'

         
if __name__ == "__main__":
    App().run()