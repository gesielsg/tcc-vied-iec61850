#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import queue
import shutil
import signal
import subprocess
import threading
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import font as tkfont, messagebox

PASTA = Path(__file__).resolve().parent
ARQUIVO = PASTA / "AjustesMU.txt"
SCRIPT_MU = PASTA / "mu"
EXEC_PADRAO = "./mu1 lo"

ORDEM = [
    ("ia",  "Corrente A",           "Ia"),
    ("aia", "Ângulo da corrente A", "ang Ia"),
    ("ib",  "Corrente B",           "Ib"),
    ("aib", "Ângulo da corrente B", "ang Ib"),
    ("ic",  "Corrente C",           "Ic"),
    ("aic", "Ângulo da corrente C", "ang Ic"),
    ("va",  "Tensão A",             "Va"),
    ("ava", "Ângulo da tensão A",   "ang Va"),
    ("vb",  "Tensão B",             "Vb"),
    ("avb", "Ângulo da tensão B",   "ang Vb"),
    ("vc",  "Tensão C",             "Vc"),
    ("avc", "Ângulo da tensão C",   "ang Vc"),
    ("f",   "Frequência",           "freq"),
]
TRIO_I = (("ia", "aia"), ("ib", "aib"), ("ic", "aic"))
TRIO_V = (("va", "ava"), ("vb", "avb"), ("vc", "avc"))

BG, CARTAO, TOPO = "#eef2f7", "#ffffff", "#15263a"
TEXTO, SUAVE, BORDA = "#1f2d3d", "#7d8fa1", "#ccd7e2"
VERDE, VERDE_ON = "#1f8a4c", "#166b3a"
AZUL, AZUL_ON = "#2a6ebb", "#215793"
CLARO, CLARO_ON = "#dde5ed", "#cbd6e2"
VINHO, VINHO_ON = "#a63d3d", "#8a3131"
ERRO, PREV_BG, PREV_FG = "#c0392b", "#10202f", "#d5e4f2"
FASE_COR = {"A": "#d9534f", "B": "#dda033", "C": "#3d7fd9"}


def normalizar(texto):
    try:
        return float(texto.strip().replace(",", "."))
    except ValueError:
        return None


def formatar(valor):
    texto = f"{valor:.6f}".rstrip("0")
    return texto + "0" if texto.endswith(".") else texto


def comandos_do_script():
    if not SCRIPT_MU.exists():
        return "", ""
    texto = SCRIPT_MU.read_text(errors="ignore").replace("\\\n", " ")
    compilar, executar = [], []
    for linha in texto.splitlines():
        limpa = linha.strip()
        if not limpa or limpa.startswith("#"):
            continue
        (executar if limpa.startswith("./") else compilar).append(limpa)
    return " && ".join(compilar), " && ".join(executar)


class InterfaceMU(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ajustes e execução da MU")
        self.configure(bg=BG)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        familia = self._familia(("Ubuntu", "Noto Sans", "DejaVu Sans", "Segoe UI"))
        mono = self._familia(("Ubuntu Mono", "DejaVu Sans Mono", "Courier New"), fixa=True)
        self.f_topo = tkfont.Font(family=familia, size=15, weight="bold")
        self.f_mini = tkfont.Font(family=familia, size=8)
        self.f_secao = tkfont.Font(family=familia, size=9, weight="bold")
        self.f_base = tkfont.Font(family=familia, size=10)
        self.f_botao = tkfont.Font(family=familia, size=10, weight="bold")
        self.f_mono = tkfont.Font(family=mono, size=10)

        self.vars, self.campos, self.botoes = {}, {}, {}
        self.status = tk.StringVar(value="")
        self.processo, self.etapas, self.titulo_etapa = None, [], ""
        self.fila = queue.Queue()
        self.pronto = False

        self._montar()
        self.pronto = True
        self._carregar_arquivo()
        self._atualizar_previa()
        self._estado_botoes(rodando=False)

        self.bind("<Return>", lambda _e: self.gerar())
        self.protocol("WM_DELETE_WINDOW", self.sair)
        self.campos["ia"].focus_set()
        self.minsize(760, 720)
        self._centralizar()
        self.after(100, self._drenar)

    def _familia(self, opcoes, fixa=False):
        disponiveis = set(tkfont.families(self))
        for nome in opcoes:
            if nome in disponiveis:
                return nome
        return tkfont.nametofont("TkFixedFont" if fixa else "TkDefaultFont").actual("family")

    def _centralizar(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = max(0, (self.winfo_screenheight() - self.winfo_height()) // 4)
        self.geometry(f"+{x}+{y}")

    def _campo(self, pai, chave, linha, coluna, unidade):
        var = tk.StringVar()
        var.trace_add("write", lambda *_a: self._atualizar_previa())
        caixa = tk.Frame(pai, bg=CARTAO)
        caixa.grid(row=linha, column=coluna, padx=6, pady=4)
        entrada = tk.Entry(caixa, textvariable=var, width=9, justify="right",
                           font=self.f_base, bg="white", fg=TEXTO, relief="flat",
                           insertbackground=TEXTO, highlightthickness=1,
                           highlightbackground=BORDA, highlightcolor=VERDE)
        entrada.grid(row=0, column=0, ipady=4, ipadx=4)
        tk.Label(caixa, text=unidade, font=self.f_mini, bg=CARTAO,
                 fg=SUAVE).grid(row=0, column=1, padx=(4, 0))
        self.vars[chave], self.campos[chave] = var, entrada

    def _cartao(self, pai, titulo, linha):
        moldura = tk.Frame(pai, bg=CARTAO, highlightbackground=BORDA, highlightthickness=1)
        moldura.grid(row=linha, column=0, sticky="ew", pady=(0, 12))
        tk.Label(moldura, text=titulo, font=self.f_secao, bg=CARTAO, fg=SUAVE).grid(
            row=0, column=0, columnspan=3, sticky="w", padx=14, pady=(10, 2))
        return moldura

    def _trifasico(self, pai, titulo, linha, unidade, trio):
        cartao = self._cartao(pai, titulo, linha)
        tk.Label(cartao, text=f"Módulo ({unidade})", font=self.f_mini,
                 bg=CARTAO, fg=SUAVE).grid(row=1, column=1)
        tk.Label(cartao, text="Ângulo (graus)", font=self.f_mini,
                 bg=CARTAO, fg=SUAVE).grid(row=1, column=2)
        for i, (fase, (k_mod, k_ang)) in enumerate(zip("ABC", trio), start=2):
            tk.Label(cartao, text=f"  Fase {fase}  ", font=self.f_secao, bg=FASE_COR[fase],
                     fg="white").grid(row=i, column=0, padx=(14, 4), pady=4, sticky="w")
            self._campo(cartao, k_mod, i, 1, unidade)
            self._campo(cartao, k_ang, i, 2, "°")
        tk.Frame(cartao, bg=CARTAO, height=8).grid(row=5, column=0)

    def _botao(self, pai, chave, texto, coluna, fundo, ativo, frente, comando):
        b = tk.Button(pai, text=texto, command=comando, font=self.f_botao, bg=fundo,
                      fg=frente, activebackground=ativo, activeforeground=frente,
                      disabledforeground="#9fb0c0", relief="flat", bd=0,
                      highlightthickness=0, cursor="hand2", padx=14, pady=8)
        b.grid(row=0, column=coluna, padx=(0, 8), pady=3)
        self.botoes[chave] = b

    def _montar(self):
        topo = tk.Frame(self, bg=TOPO)
        topo.grid(row=0, column=0, sticky="ew")
        tk.Label(topo, text="Ajustes e execução da MU", font=self.f_topo, bg=TOPO,
                 fg="white").grid(row=0, column=0, sticky="w", padx=18, pady=(14, 0))
        tk.Label(topo, text=f"Pasta: {PASTA}", font=self.f_mini, bg=TOPO,
                 fg="#8ea7c0").grid(row=1, column=0, sticky="w", padx=18, pady=(2, 14))

        corpo = tk.Frame(self, bg=BG, padx=16, pady=16)
        corpo.grid(row=1, column=0, sticky="ew")
        esquerda = tk.Frame(corpo, bg=BG)
        esquerda.grid(row=0, column=0, sticky="n")
        self._trifasico(esquerda, "CORRENTES", 0, "A", TRIO_I)
        self._trifasico(esquerda, "TENSÕES", 1, "V", TRIO_V)
        cartao_f = self._cartao(esquerda, "FREQUÊNCIA", 2)
        tk.Label(cartao_f, text="  Sistema  ", font=self.f_secao, bg="#5a6b7b",
                 fg="white").grid(row=1, column=0, padx=(14, 4), pady=(0, 12), sticky="w")
        self._campo(cartao_f, "f", 1, 1, "Hz")

        painel = tk.Frame(corpo, bg=PREV_BG)
        painel.grid(row=0, column=1, sticky="n", padx=(14, 0))
        tk.Label(painel, text="PRÉVIA DO AjustesMU.txt", font=self.f_secao,
                 bg=PREV_BG, fg="#6f8aa5").grid(row=0, column=0, sticky="w", padx=14, pady=(12, 6))
        self.previa = tk.Text(painel, width=24, height=14, font=self.f_mono, bg=PREV_BG,
                              fg=PREV_FG, relief="flat", bd=0, padx=14, pady=0,
                              highlightthickness=0, cursor="arrow")
        self.previa.grid(row=1, column=0, pady=(0, 14))
        self.previa.tag_configure("ok", foreground=PREV_FG)
        self.previa.tag_configure("falta", foreground="#5d7186")
        self.previa.tag_configure("rotulo", foreground="#6f8aa5")
        self.previa.configure(state="disabled")

        rodape = tk.Frame(self, bg=BG, padx=16)
        rodape.grid(row=2, column=0, sticky="ew")
        linha1 = tk.Frame(rodape, bg=BG)
        linha1.grid(row=0, column=0, sticky="w")
        self._botao(linha1, "tudo", "Gerar + Compilar + Rodar", 0, VERDE, VERDE_ON, "white", self.tudo)
        self._botao(linha1, "gerar", "Só gerar TXT", 1, CLARO, CLARO_ON, TEXTO, self.gerar)
        self._botao(linha1, "compilar", "Compilar", 2, AZUL, AZUL_ON, "white", self.compilar)
        self._botao(linha1, "rodar", "Rodar MU", 3, AZUL, AZUL_ON, "white", self.rodar)
        linha2 = tk.Frame(rodape, bg=BG)
        linha2.grid(row=1, column=0, sticky="w")
        self._botao(linha2, "parar", "Parar MU", 0, VINHO, VINHO_ON, "white", self.parar)
        self._botao(linha2, "limpar", "Limpar campos", 1, CLARO, CLARO_ON, TEXTO, self.limpar)
        self._botao(linha2, "sair", "Sair", 2, CLARO, CLARO_ON, TEXTO, self.sair)

        console = tk.Frame(self, bg=BG, padx=16, pady=10)
        console.grid(row=3, column=0, sticky="nsew")
        console.columnconfigure(0, weight=1)
        console.rowconfigure(1, weight=1)
        tk.Label(console, text="SAÍDA DO GCC E DA MU", font=self.f_secao, bg=BG,
                 fg=SUAVE).grid(row=0, column=0, sticky="w", pady=(0, 4))
        caixa = tk.Frame(console, bg=PREV_BG)
        caixa.grid(row=1, column=0, sticky="nsew")
        caixa.columnconfigure(0, weight=1)
        caixa.rowconfigure(0, weight=1)
        self.console = tk.Text(caixa, height=10, font=self.f_mono, bg=PREV_BG, fg=PREV_FG,
                               relief="flat", bd=0, padx=12, pady=8, wrap="none",
                               highlightthickness=0)
        self.console.grid(row=0, column=0, sticky="nsew")
        barra = tk.Scrollbar(caixa, command=self.console.yview)
        barra.grid(row=0, column=1, sticky="ns")
        self.console.configure(yscrollcommand=barra.set, state="disabled")
        self.console.tag_configure("cmd", foreground="#e5c07b")
        self.console.tag_configure("ok", foreground="#7ec699")
        self.console.tag_configure("erro", foreground="#ef8b7d")

        tk.Label(self, textvariable=self.status, font=self.f_mini, bg=BG, fg=SUAVE,
                 justify="left", wraplength=880).grid(row=4, column=0, sticky="w",
                                                      padx=16, pady=(0, 12))

    def _carregar_arquivo(self):
        if not ARQUIVO.exists():
            self.status.set(f"O arquivo ainda não existe. Será criado em {ARQUIVO}")
            return
        try:
            linhas = [l.strip() for l in ARQUIVO.read_text(encoding="utf-8",
                      errors="ignore").splitlines() if l.strip()]
        except OSError as erro:
            self.status.set(f"Não foi possível ler o arquivo atual: {erro}")
            return
        for (chave, _r, _c), valor in zip(ORDEM, linhas):
            self.vars[chave].set(valor)
        self.status.set(f"{len(linhas)} valor(es) carregado(s) do AjustesMU.txt atual.")

    def _atualizar_previa(self):
        if not self.pronto:
            return
        self.previa.configure(state="normal")
        self.previa.delete("1.0", tk.END)
        for i, (chave, _rotulo, curto) in enumerate(ORDEM, start=1):
            texto = self.vars[chave].get().strip()
            valor = normalizar(texto) if texto else None
            if valor is None:
                self.previa.insert(tk.END, f"{i:>2}  {'- - -':<11}", "falta")
            else:
                self.previa.insert(tk.END, f"{i:>2}  {formatar(valor):<11}", "ok")
            self.previa.insert(tk.END, f"{curto}\n", "rotulo")
        self.previa.configure(state="disabled")

    def coletar(self):
        for entrada in self.campos.values():
            entrada.configure(highlightbackground=BORDA, highlightthickness=1)
        vazios, invalidos, valores = [], [], []
        for chave, rotulo, _c in ORDEM:
            texto = self.vars[chave].get()
            if not texto.strip():
                vazios.append(rotulo)
            else:
                valor = normalizar(texto)
                if valor is None:
                    invalidos.append(f"{rotulo}  ->  '{texto.strip()}'")
                else:
                    valores.append(valor)
                    continue
            self.campos[chave].configure(highlightbackground=ERRO, highlightthickness=2)
        if vazios or invalidos:
            partes = []
            if vazios:
                partes.append("Campos em branco:\n  - " + "\n  - ".join(vazios))
            if invalidos:
                partes.append("Valores não numéricos:\n  - " + "\n  - ".join(invalidos))
            messagebox.showerror("Preenchimento incompleto", "\n\n".join(partes), parent=self)
            self.status.set("Nada foi gravado: corrija os campos destacados em vermelho.")
            return None
        return valores

    def _log(self, texto, tag=""):
        no_fim = self.console.yview()[1] >= 0.999
        self.console.configure(state="normal")
        self.console.insert(tk.END, texto.rstrip("\n") + "\n", tag)
        if int(self.console.index("end-1c").split(".")[0]) > 3000:
            self.console.delete("1.0", "1000.0")
        if no_fim:
            self.console.see(tk.END)
        self.console.configure(state="disabled")

    def _ocupado(self):
        return self.processo is not None and self.processo.poll() is None

    def _estado_botoes(self, rodando):
        for chave in ("tudo", "compilar", "rodar", "limpar"):
            self.botoes[chave].configure(state="disabled" if rodando else "normal")
        self.botoes["parar"].configure(state="normal" if rodando else "disabled")

    def _executar(self, comando, titulo):
        if self._ocupado():
            messagebox.showwarning("Processo em andamento",
                                   "Pare o processo atual antes de iniciar outro.", parent=self)
            return False
        self._log(f"\n$ {comando}", "cmd")
        try:
            self.processo = subprocess.Popen(
                comando, shell=True, cwd=str(PASTA), stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, text=True, bufsize=1, start_new_session=True)
        except OSError as erro:
            self._log(f"Falha ao iniciar o processo: {erro}", "erro")
            self.etapas.clear()
            return False
        self.titulo_etapa = titulo
        self.status.set(f"{titulo}: em andamento...")
        self._estado_botoes(rodando=True)
        threading.Thread(target=self._ler_saida, args=(self.processo,), daemon=True).start()
        return True

    def _ler_saida(self, processo):
        for linha in processo.stdout:
            self.fila.put(("saida", linha.rstrip("\n")))
        processo.stdout.close()
        self.fila.put(("fim", processo.wait()))

    def _drenar(self):
        try:
            while True:
                tipo, dado = self.fila.get_nowait()
                if tipo == "saida":
                    self._log(dado)
                else:
                    self._finalizar(dado)
        except queue.Empty:
            pass
        self.after(100, self._drenar)

    def _finalizar(self, codigo):
        titulo, self.processo = self.titulo_etapa, None
        self._estado_botoes(rodando=False)
        if codigo == 0:
            self._log(f"[{titulo}] concluído com sucesso.", "ok")
            self.status.set(f"{titulo}: concluído.")
            if self.etapas:
                self.etapas.pop(0)()
        elif codigo in (130, -2, -15, 143):
            self._log(f"[{titulo}] interrompido.", "cmd")
            self.status.set(f"{titulo}: interrompido.")
            self.etapas.clear()
        else:
            self._log(f"[{titulo}] terminou com código {codigo}.", "erro")
            self.status.set(f"{titulo}: código de saída {codigo}. Veja a saída abaixo.")
            self.etapas.clear()

    def gerar(self):
        valores = self.coletar()
        if valores is None:
            return False
        try:
            tmp = ARQUIVO.with_name(ARQUIVO.name + ".tmp")
            tmp.write_text("\n".join(formatar(v) for v in valores) + "\n", encoding="utf-8")
            os.replace(tmp, ARQUIVO)
        except OSError as erro:
            messagebox.showerror("Erro ao gravar",
                                 f"Não foi possível escrever em:\n{ARQUIVO}\n\n{erro}", parent=self)
            return False
        self._log(f"AjustesMU.txt gravado às {datetime.now():%H:%M:%S} "
                  f"({len(valores)} valores).", "ok")
        if self._ocupado():
            self.status.set(f"AjustesMU.txt gravado às {datetime.now():%H:%M:%S}. A MU em "
                            "execução aplica os novos valores em até 10 ms.")
        else:
            self.status.set(f"AjustesMU.txt gravado às {datetime.now():%H:%M:%S}.")
        return True

    def compilar(self):
        compilar, _ = comandos_do_script()
        if not compilar:
            messagebox.showerror("Script não encontrado",
                                 f"Não encontrei a linha de compilação em:\n{SCRIPT_MU}",
                                 parent=self)
            self.etapas.clear()
            return False
        return self._executar(compilar, "Compilação")

    def rodar(self):
        _, executar = comandos_do_script()
        executar = executar or EXEC_PADRAO
        if "&&" not in executar and shutil.which("stdbuf"):
            executar = "stdbuf -oL -eL " + executar
        if os.geteuid() != 0:
            self._log("Aviso: a MU costuma precisar de root para publicar Sampled Values. "
                      "Se falhar, feche e reabra com:  sudo -E python3 interface.py", "erro")
        return self._executar(executar, "Execução da MU")

    def tudo(self):
        if not self.gerar():
            return
        self.etapas = [self.rodar]
        self.compilar()

    def parar(self):
        self.etapas.clear()
        if not self._ocupado():
            return
        try:
            os.killpg(os.getpgid(self.processo.pid), signal.SIGINT)
            self._log("(SIGINT enviado, equivale ao Ctrl+C)", "cmd")
            self.after(3000, self._forcar_parada)
        except (ProcessLookupError, PermissionError, OSError) as erro:
            self._log(f"Não foi possível parar o processo: {erro}", "erro")

    def _forcar_parada(self):
        if self._ocupado():
            try:
                os.killpg(os.getpgid(self.processo.pid), signal.SIGKILL)
                self._log("(SIGKILL enviado)", "erro")
            except OSError:
                pass

    def limpar(self):
        for var in self.vars.values():
            var.set("")
        for entrada in self.campos.values():
            entrada.configure(highlightbackground=BORDA, highlightthickness=1)
        self.campos["ia"].focus_set()
        self.status.set("Campos limpos. O arquivo no disco não foi alterado.")

    def sair(self):
        if self._ocupado():
            if not messagebox.askyesno("Processo em andamento",
                                       "A MU ainda está rodando. Encerrar e sair?", parent=self):
                return
            self.etapas.clear()
            try:
                os.killpg(os.getpgid(self.processo.pid), signal.SIGKILL)
            except OSError:
                pass
        self.destroy()


if __name__ == "__main__":
    InterfaceMU().mainloop()