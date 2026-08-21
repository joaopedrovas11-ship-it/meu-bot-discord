import os
import io
import random
import qrcode
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

CHAVE_PIX = "07448728555"
PRODUTO = "Attack on Titan Produtos"
PRECO = 19.90

NOME_RECEBEDOR = "Thiago Fabiano"
CIDADE = "ESTANCIA"


# =========================
# BOT
# =========================

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =========================
# GERAR PIX
# =========================

def campo(id_campo, valor):
    return f"{id_campo}{len(valor):02d}{valor}"


def crc16(payload):
    crc = 0xFFFF

    for byte in payload.encode("utf-8"):
        crc ^= byte << 8

        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1

            crc &= 0xFFFF

    return format(crc, "04X")


def gerar_pix(valor):

    valor_formatado = f"{valor:.2f}"

    merchant_account = (
        campo("00", "br.gov.bcb.pix")
        + campo("01", CHAVE_PIX)
    )

    payload = (
        campo("00", "01")
        + campo("26", merchant_account)
        + campo("52", "0000")
        + campo("53", "986")
        + campo("54", valor_formatado)
        + campo("58", "BR")
        + campo("59", NOME_RECEBEDOR[:25])
        + campo("60", CIDADE[:15])
        + campo("62", campo("05", "***"))
    )

    payload += "6304"

    return payload + crc16(payload)


# =========================
# BOTÃO COMPRAR
# =========================

class LojaView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🛒 Comprar",
        style=discord.ButtonStyle.green
    )
    async def comprar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        pedido = random.randint(10000, 99999)

        codigo_pix = gerar_pix(PRECO)

        qr = qrcode.make(codigo_pix)

        imagem = io.BytesIO()

        qr.save(
            imagem,
            format="PNG"
        )

        imagem.seek(0)

        arquivo = discord.File(
            imagem,
            filename="pix.png"
        )

        embed = discord.Embed(
            title="💳 Pagamento via PIX",
            description=(
                f"📦 **Produto:** {PRODUTO}\n"
                f"💰 **Valor:** R$ {PRECO:.2f}\n"
                f"🆔 **Pedido:** #{pedido}\n\n"
                "📱 Escaneie o QR Code com seu banco.\n\n"
                "📋 **PIX Copia e Cola:**"
            ),
            color=discord.Color.green()
        )

        embed.set_image(
            url="attachment://pix.png"
        )

        await interaction.response.send_message(
            content=f"```{codigo_pix}```",
            embed=embed,
            file=arquivo,
            ephemeral=True
        )


# =========================
# COMANDO /PRODUTOS
# =========================

@bot.tree.command(
    name="produtos",
    description="Mostra os produtos disponíveis"
)
async def produtos(
    interaction: discord.Interaction
):

    embed = discord.Embed(
        title= "🛒 Atack-Titan",
        description="Escolha seu produto abaixo!",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="📘 Produtos Jp",
        value="💰 **R$ 19,90**",
        inline=False
    )

    await interaction.response.send_message(
        embed=embed,
        view=LojaView()
    )


# =========================
# BOT ONLINE
# =========================

@bot.event
async def on_ready():

    print(
        f"🤖 Bot conectado como {bot.user}"
    )

    try:

        sincronizados = await bot.tree.sync()

        print(
            f"✅ {len(sincronizados)} comando(s) sincronizado(s)!"
        )

    except Exception as erro:

        print(
            f"❌ Erro: {erro}"
        )


# =========================
# INICIAR
# =========================

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN não foi configurado.")

bot.run(TOKEN)