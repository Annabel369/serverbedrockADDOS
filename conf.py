import glob
import json
import os
import tkinter as tk
from tkinter import ttk

# --- CONFIGURAÇÃO DE CORES (CREEPER TERMINAL) ---
BG_DARK = "#0A0A0A"
FG_LIME = "#55FF55"
BG_FIELD = "#141414"
BORDER_GREEN = "#1E8C1E"
BTN_ACTIVE_BG = "#55FF55"
BTN_ACTIVE_FG = "#000000"

COLOR_ACTIVE = "#55AAFF"   # Azul para ativo
COLOR_INACTIVE = "#FF5555" # Vermelho para desativado

# Desenho exato do seu logo customizado em pixel art
CREEPER_LOGO_CUSTOM = """
██████████████████████████████
███████      █████      ██████
███████      █████      ██████
██████████████████████████████
████████████      ████████████
█████████              ███████
█████████      ████    ███████
██████████████████████████████
"""

# --- ALERTAS ---
def mostrar_alerta(titulo, mensagem, tipo="info"):
    alerta = tk.Toplevel(app)
    alerta.title(titulo)
    alerta.configure(bg=BG_DARK)
    alerta.resizable(False, False)
    alerta.geometry("450x220")
    alerta.transient(app)
    alerta.grab_set()

    cor_borda = "#FF5555" if tipo == "erro" else BORDER_GREEN

    outer = tk.Frame(alerta, bg=cor_borda, bd=2)
    outer.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    inner = tk.Frame(outer, bg=BG_DARK)
    inner.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    lbl_t = tk.Label(inner, text=f"[ {titulo.upper()} ]", bg=BG_DARK, fg=cor_borda,
                     font=("Courier", 11, "bold"))
    lbl_t.pack(pady=(15, 10))

    lbl_m = tk.Label(inner, text=mensagem, bg=BG_DARK, fg=FG_LIME,
                     font=("Courier", 9), justify=tk.LEFT, wraplength=400)
    lbl_m.pack(pady=(0, 15), padx=10)

    btn_ok = tk.Button(inner, text="[ OK ]", bg=BG_DARK, fg=FG_LIME,
                       activebackground=FG_LIME, activeforeground=BG_DARK,
                       font=("Courier", 10, "bold"), relief=tk.SOLID, bd=1,
                       cursor="hand2", command=alerta.destroy)
    btn_ok.pack(ipady=3, ipadx=15, pady=(0, 10))

# --- FUNÇÕES DE ARQUIVO ---
def escanear_pastas(tipo_pack):
    if not os.path.exists(tipo_pack):
        return []
    return sorted([d for d in os.listdir(tipo_pack) if os.path.isdir(os.path.join(tipo_pack, d))])

def buscar_com_coringa(tipo_pack, termo):
    termo = termo.strip()
    if not termo:
        return escanear_pastas(tipo_pack)
    caminhos = glob.glob(os.path.join(tipo_pack, f"*{termo}*"))
    return sorted([os.path.basename(p) for p in caminhos if os.path.isdir(p)])

def ler_manifest(pasta_tipo, nome_pasta):
    caminho_manifest = os.path.join(pasta_tipo, nome_pasta, "manifest.json")
    if not os.path.exists(caminho_manifest):
        raise FileNotFoundError(f"O arquivo '{caminho_manifest}' nao foi encontrado.")

    with open(caminho_manifest, "r", encoding="utf-8") as f:
        dados = json.load(f)

    header = dados.get("header", {})
    uuid = header.get("uuid")
    version_raw = header.get("version", [1, 0, 0])

    if not uuid:
        raise ValueError(f"Nao foi possivel encontrar o 'uuid' no header de '{caminho_manifest}'.")

    if isinstance(version_raw, list):
        version_list = version_raw
        version_str = ".".join(map(str, version_raw))
    else:
        version_str = str(version_raw)
        try:
            version_list = [int(x) for x in version_str.split(".")]
        except ValueError:
            version_list = [1, 0, 0]

    return uuid, version_str, version_list

def carregar_json(caminho):
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def salvar_json(caminho, dados):
    pasta_pai = os.path.dirname(caminho)
    if pasta_pai:
        os.makedirs(pasta_pai, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

# --- LISTMOD INTELIGENTE ---
def carregar_listmod():
    caminho = "listMod.json"
    if not os.path.exists(caminho):
        salvar_json(caminho, [])
    return carregar_json(caminho)

def salvar_listmod(dados):
    salvar_json("listMod.json", dados)

def atualizar_listmod(path, uuid, version, status):
    lista = carregar_listmod()
    existente = False
    for item in lista:
        if item["uuid"] == uuid:
            item["path"] = path
            item["version"] = version
            item["status"] = status
            existente = True
            break
    if not existente:
        lista.append({"path": path, "uuid": uuid, "version": version, "status": status})
    salvar_listmod(lista)

def listar_pacotes_com_status(tipo_pack):
    lista = carregar_listmod()
    resultado = []
    for item in lista:
        if item["path"].startswith(tipo_pack):
            nome = os.path.basename(item["path"])
            status = item.get("status", "desativado")
            resultado.append((nome, status))
    return resultado

def atualizar_listbox():
    list_bp.delete(0, tk.END)
    
    for nome, status in listar_pacotes_com_status("behavior_packs"):
        cor = COLOR_ACTIVE if status == "ativo" else COLOR_INACTIVE
        list_bp.insert(tk.END, f"[BP] {nome}")
        list_bp.itemconfig(tk.END, fg=cor)

    for nome, status in listar_pacotes_com_status("resource_packs"):
        cor = COLOR_ACTIVE if status == "ativo" else COLOR_INACTIVE
        list_bp.insert(tk.END, f"[RP] {nome}")
        list_bp.itemconfig(tk.END, fg=cor)

# --- FUNÇÕES PRINCIPAIS ---
def adicionar_pacotes():
    nome_mundo = entry_mundo.get().strip()
    bp_nome = combo_bp.get().strip()
    rp_nome = combo_rp.get().strip()

    if not nome_mundo:
        mostrar_alerta("Aviso", "Preencha o nome da pasta do Mundo.", "erro")
        return
    if not bp_nome and not rp_nome:
        mostrar_alerta("Aviso", "Selecione ou digite pelo menos um pacote (BP ou RP).", "erro")
        return

    caminho_valid_packs = "valid_known_packs.json"
    valid_packs = carregar_json(caminho_valid_packs)
    pasta_mundo = os.path.join("worlds", nome_mundo)

    pacotes = []
    if bp_nome: pacotes.append(("behavior_packs", bp_nome))
    if rp_nome: pacotes.append(("resource_packs", rp_nome))

    mensagens = []
    arquivos_modificados = set()

    for pasta_tipo, nome_pasta in pacotes:
        try:
            pastas_encontradas = buscar_com_coringa(pasta_tipo, nome_pasta)
            if not pastas_encontradas:
                raise FileNotFoundError(f"Nenhuma pasta encontrada em '{pasta_tipo}' com: '{nome_pasta}'")

            nome_pasta_real = pastas_encontradas[0]
            uuid, version_str, version_list = ler_manifest(pasta_tipo, nome_pasta_real)
            caminho_relativo = f"{pasta_tipo}/{nome_pasta_real}"

            # Atualiza valid_known_packs.json
            existente = False
            for item in valid_packs:
                if item.get("path") == caminho_relativo:
                    item["uuid"] = uuid
                    item["version"] = version_str
                    item["file_system"] = "RawPath"
                    existente = True
                    break

            if not existente:
                valid_packs.append({
                    "file_system": "RawPath",
                    "path": caminho_relativo,
                    "uuid": uuid,
                    "version": version_str,
                })
            arquivos_modificados.add(caminho_valid_packs)

            # Atualiza world_*.json
            nome_arquivo_world = (
                "world_behavior_packs.json"
                if pasta_tipo == "behavior_packs"
                else "world_resource_packs.json"
            )
            caminho_world_json = os.path.join(pasta_mundo, nome_arquivo_world)
            world_packs = carregar_json(caminho_world_json)

            existente_mundo = False
            for item in world_packs:
                if item.get("pack_id") == uuid:
                    item["version"] = version_list
                    existente_mundo = True
                    break
            if not existente_mundo:
                world_packs.append({"pack_id": uuid, "version": version_list})

            salvar_json(caminho_world_json, world_packs)
            arquivos_modificados.add(caminho_world_json)

            # Atualiza memória inteligente
            atualizar_listmod(caminho_relativo, uuid, version_str, "ativo")

            mensagens.append(f"✔ {nome_pasta_real}\n   UUID: {uuid}\n   Versao: {version_str}")

        except Exception as e:
            mostrar_alerta("Erro ao Adicionar", str(e), "erro")
            return

    salvar_json(caminho_valid_packs, valid_packs)

    mostrar_alerta(
        "Sucesso",
        f"OPERACAO CONCLUIDA!\nTotal de {len(arquivos_modificados)} arquivos atualizados no servidor.\n\n"
        + "\n\n".join(mensagens),
    )
    atualizar_listbox()


def remover_pacotes():
    nome_mundo = entry_mundo.get().strip()
    bp_nome = combo_bp.get().strip()
    rp_nome = combo_rp.get().strip()

    if not bp_nome and not rp_nome:
        mostrar_alerta("Aviso", "Selecione ou digite o pacote que deseja remover.", "erro")
        return

    caminho_valid_packs = "valid_known_packs.json"
    valid_packs = carregar_json(caminho_valid_packs)
    pasta_mundo = os.path.join("worlds", nome_mundo)

    pacotes = []
    if bp_nome: pacotes.append(("behavior_packs", bp_nome))
    if rp_nome: pacotes.append(("resource_packs", rp_nome))

    removidos_count = 0
    arquivos_modificados = set()

    for pasta_tipo, nome_pasta in pacotes:
        pastas_encontradas = buscar_com_coringa(pasta_tipo, nome_pasta)
        nome_busca = pastas_encontradas[0] if pastas_encontradas else nome_pasta
        caminho_relativo = f"{pasta_tipo}/{nome_busca}"

        uuid = None
        version_str = "?"
        try:
            uuid, version_str, _ = ler_manifest(pasta_tipo, nome_busca)
        except Exception:
            pass

        # Remove de valid_known_packs.json
        tamanho_antes = len(valid_packs)
        valid_packs = [item for item in valid_packs if not (
            item.get("path") == caminho_relativo or (uuid and item.get("uuid") == uuid)
        )]
        if len(valid_packs) < tamanho_antes:
            removidos_count += 1
            arquivos_modificados.add(caminho_valid_packs)

        # Remove dos arquivos do mundo
        if nome_mundo and uuid:
            nome_arquivo_world = "world_behavior_packs.json" if pasta_tipo == "behavior_packs" else "world_resource_packs.json"
            caminho_world_json = os.path.join(pasta_mundo, nome_arquivo_world)
            world_packs = carregar_json(caminho_world_json)

            tamanho_world_antes = len(world_packs)
            world_packs = [item for item in world_packs if not (uuid and item.get("pack_id") == uuid)]

            if len(world_packs) < tamanho_world_antes:
                salvar_json(caminho_world_json, world_packs)
                arquivos_modificados.add(caminho_world_json)

        # Atualiza memória inteligente como desativado
        if uuid:
            atualizar_listmod(caminho_relativo, uuid, version_str, "desativado")

    salvar_json(caminho_valid_packs, valid_packs)

    mostrar_alerta(
        "Remocao Concluida",
        f"REMOÇÃO REALIZADA COM SUCESSO!\n\n"
        f"• {removidos_count} pacote(s) removido(s).\n"
        f"• Total de {len(arquivos_modificados)} arquivos modificados no servidor.",
    )
    atualizar_listbox()


def atualizar_combos():
    combo_bp["values"] = escanear_pastas("behavior_packs")
    combo_rp["values"] = escanear_pastas("resource_packs")


# --- INTERFACE TKINTER ---
app = tk.Tk()
app.title("CREEPER ADD-ON MANAGER")
app.geometry("580x720")
app.configure(bg=BG_DARK)
app.resizable(False, False)

# Configuração de Temas para Combobox
style = ttk.Style()
style.theme_use("default")
style.configure("TCombobox", fieldbackground=BG_FIELD, background=BG_DARK,
                foreground=FG_LIME, bordercolor=BORDER_GREEN, insertcolor=FG_LIME, arrowcolor=FG_LIME)

# Linha Verde Superior
canvas_line = tk.Canvas(app, bg=BG_DARK, highlightthickness=0, height=12, width=580)
canvas_line.pack(fill=tk.X, pady=(5, 0))
canvas_line.create_line(15, 6, 565, 6, fill=FG_LIME, width=4)

# Moldura principal
outline_frame = tk.Frame(app, bg=BORDER_GREEN, bd=2)
outline_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 15))
main_frame = tk.Frame(outline_frame, bg=BG_DARK)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Logo
lbl_creeper = tk.Label(main_frame, text=CREEPER_LOGO_CUSTOM, bg=BG_DARK, fg=FG_LIME,
                       font=("Courier", 8, "bold"), justify=tk.CENTER)
lbl_creeper.pack(pady=(0, 2))

lbl_title = tk.Label(main_frame, text="CREEPER ADD-ON MANAGER", bg=BG_DARK, fg=FG_LIME,
                     font=("Courier", 13, "bold"))
lbl_title.pack(pady=(0, 15))

# Campo Mundo
lbl_mundo = tk.Label(main_frame, text="PASTA DO MUNDO (/worlds/):", bg=BG_DARK, fg=FG_LIME,
                     font=("Courier", 10, "bold"))
lbl_mundo.pack(anchor=tk.W)
entry_mundo = tk.Entry(main_frame, bg=BG_FIELD, fg=FG_LIME, insertbackground=FG_LIME,
                       font=("Courier", 10), relief=tk.SOLID, bd=1)
entry_mundo.insert(0, "Bedrock level")
entry_mundo.pack(fill=tk.X, pady=(2, 12), ipady=4)

# Combobox Behavior Pack
lbl_bp = tk.Label(main_frame, text="BEHAVIOR PACK (SELECIONE OU USE *CORINGA*):",
                  bg=BG_DARK, fg=FG_LIME, font=("Courier", 10, "bold"))
lbl_bp.pack(anchor=tk.W)
combo_bp = ttk.Combobox(main_frame, font=("Courier", 10))
combo_bp.pack(fill=tk.X, pady=(2, 12), ipady=3)

# Combobox Resource Pack
lbl_rp = tk.Label(main_frame, text="RESOURCE PACK (SELECIONE OU USE *CORINGA*):",
                  bg=BG_DARK, fg=FG_LIME, font=("Courier", 10, "bold"))
lbl_rp.pack(anchor=tk.W)
combo_rp = ttk.Combobox(main_frame, font=("Courier", 10))
combo_rp.pack(fill=tk.X, pady=(2, 18), ipady=3)

# Botões
btn_frame = tk.Frame(main_frame, bg=BG_DARK)
btn_frame.pack(fill=tk.X, pady=(0, 10))
btn_add = tk.Button(btn_frame, text="[ + ] ADICIONAR / ATIVAR", bg=BG_DARK, fg=FG_LIME,
                    activebackground=FG_LIME, activeforeground=BG_DARK,
                    font=("Courier", 10, "bold"), relief=tk.SOLID, bd=1,
                    cursor="hand2", command=adicionar_pacotes)
btn_add.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=6)

btn_del = tk.Button(btn_frame, text="[ X ] REMOVER PACOTE", bg=BG_DARK, fg="#FF5555",
                    activebackground="#FF5555", activeforeground="#000000",
                    font=("Courier", 10, "bold"), relief=tk.SOLID, bd=1,
                    cursor="hand2", command=remover_pacotes)
btn_del.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0), ipady=6)

# Memória inteligente
lbl_mem = tk.Label(main_frame, text="MEMÓRIA DE PACOTES (listMod.json):",
                   bg=BG_DARK, fg=FG_LIME, font=("Courier", 10, "bold"))
lbl_mem.pack(anchor=tk.W, pady=(10, 0))

list_bp = tk.Listbox(main_frame, bg=BG_FIELD, fg=FG_LIME, font=("Courier", 10), height=6)
list_bp.pack(fill=tk.X, padx=5, pady=5)

btn_mem_refresh = tk.Button(
    main_frame,
    text="🔄 Atualizar Memória",
    bg=BG_DARK,
    fg=FG_LIME,
    activebackground=FG_LIME,
    activeforeground=BG_DARK,
    font=("Courier", 10, "bold"),
    relief=tk.SOLID,
    bd=1,
    cursor="hand2",
    command=atualizar_listbox,
)
btn_mem_refresh.pack(fill=tk.X, pady=(5, 10))

# Inicializa combobox e memória
atualizar_combos()
atualizar_listbox()

app.mainloop()