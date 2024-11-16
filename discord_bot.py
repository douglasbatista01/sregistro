# File: discord_bot.py

import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
import json

# Configuração do bot
intents = discord.Intents.default()
intents.members = True  # Necessário para gerenciar membros
bot = commands.Bot(command_prefix="!", intents=intents)

# Carregar dados registrados (se necessário)
DATA_FILE = "dados_registro.json"

def carregar_dados():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def salvar_dados(dados):
    with open(DATA_FILE, "w") as file:
        json.dump(dados, file, indent=4)

# Inicializa o armazenamento de dados
dados_registro = carregar_dados()

# Nome do canal específico
CANAL_REGISTRO = "pedir-set"

# Nome do cargo que será atribuído
CARGO_MEMBRO = "Membro"

# Modal para capturar os dados
class RegistroModal(Modal):
    def __init__(self):
        super().__init__(title="Registro de Jogador")

        self.nome = TextInput(label="Nome", placeholder="Digite seu nome")
        self.id = TextInput(label="ID", placeholder="Digite seu ID")
        self.recrutador = TextInput(label="Nome do Recrutador", placeholder="Digite o nome do recrutador")

        self.add_item(self.nome)
        self.add_item(self.id)
        self.add_item(self.recrutador)

    async def on_submit(self, interaction: discord.Interaction):
        usuario_id = str(interaction.user.id)
        nome = self.nome.value
        id = self.id.value
        recrutador = self.recrutador.value

        # Salvar os dados
        dados_registro[usuario_id] = {
            "Nome": nome,
            "ID": id,
            "Recrutador": recrutador
        }
        salvar_dados(dados_registro)

        # Alterar apelido do usuário
        novo_apelido = f"M | {nome} | {id}"
        try:
            await interaction.user.edit(nick=novo_apelido)

            # Adicionar o cargo de "Membro"
            guild = interaction.guild  # Obter o servidor atual
            cargo_membro = discord.utils.get(guild.roles, name=CARGO_MEMBRO)  # Buscar o cargo
            if cargo_membro:
                await interaction.user.add_roles(cargo_membro)  # Atribuir o cargo
                mensagem_cargo = f"✅ Você recebeu o cargo **{CARGO_MEMBRO}**."
            else:
                mensagem_cargo = f"⚠️ O cargo **{CARGO_MEMBRO}** não foi encontrado no servidor."

            # Confirmação ao usuário
            await interaction.response.send_message(
                f"✅ Registro concluído! Seu nome foi alterado para **{novo_apelido}**.\n{mensagem_cargo}",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Ocorreu um erro ao alterar seu apelido ou atribuir o cargo: {e}", ephemeral=True
            )

# View com botão
class RegistroView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Registrar", style=discord.ButtonStyle.green)
    async def botao_registro(self, interaction: discord.Interaction, button: Button):
        # Verifica se o comando está no canal correto
        if interaction.channel.name != CANAL_REGISTRO:
            await interaction.response.send_message(
                "❌ Este comando só pode ser usado no canal `pedir-set`.", ephemeral=True
            )
            return

        # Exibe o modal
        await interaction.response.send_modal(RegistroModal())

# Evento para enviar o botão no canal
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")
    guild = discord.utils.get(bot.guilds)  # Obter o servidor do bot
    canal = discord.utils.get(guild.text_channels, name=CANAL_REGISTRO)

    if canal:
        # Envia o botão no canal específico
        await canal.send("Clique no botão abaixo para registrar seus dados.", view=RegistroView())

# Rodar o bot
TOKEN = "05c08ebc04bc7ed8437059a7d4131487d3262fda5fc15e409d3e40be2c8f9a76"
bot.run(TOKEN)
