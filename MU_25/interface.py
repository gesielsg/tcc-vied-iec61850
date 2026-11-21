#!/usr/bin/env python3
import os
import signal
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

PASTA = Path(__file__).resolve().parent
ARQUIVO = PASTA / "AjustesMU.txt"
CHAVES = ["ia", "aia", "ib", "aib", "ic", "aic", "va", "ava", "vb", "avb", "vc", "avc", "f"]

BG, CARTAO, TEXTO, SUAVE, BORDA = "#eef2f7", "#ffffff", "#1f2d3d", "#7d8fa1", "#ccd7e2"
FASE_COR = {"A": "#d9534f", "B": "#dda033", "C": "#3d7fd9"}
FONTE = "DejaVu Sans"


class InterfaceMU(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ajustes e execução da MU")
        self.configure(bg=BG)
        self.columnconfigure(0, weight=1)
        self.vars, self.campos, self.botoes = {}, {}, {}
        self.processo, self.valores, self.ja_rodou = None, None, False

        tk.Label(self, text="Ajustes e execução da MU", font=(FONTE, 15, "bold"), bg="#15263a",
                 fg="white", anchor="w", padx=18, pady=14).grid(row=0, column=0, sticky="ew")
        corpo = tk.Frame(self, bg=BG, padx=16, pady=16)
        corpo.grid(row=1, column=0, sticky="ew")
        corpo.columnconfigure(0, weight=1)
        self._trifasico(corpo, "CORRENTES", 0, "i", "A")
        self._trifasico(corpo, "TENSÕES", 1, "v", "V")
        cartao = self._cartao(corpo, "FREQUÊNCIA", 2)
        self._rotulo(cartao, "Sistema", "#5a6b7b", 1)
        self._campo(cartao, "f", 1, 1, "Hz")

        botoes = tk.Frame(corpo, bg=BG)
        botoes.grid(row=3, column=0, sticky="w")
        self._botao(botoes, "rodar", "Gerar + Compilar + Rodar", 0, 0, "#1f8a4c", "white", self.rodar)
        self._botao(botoes, "gerar", "Só gerar TXT", 0, 1, "#dde5ed", TEXTO, self.gerar)
        self._botao(botoes, "parar", "Parar MU", 1, 0, "#a63d3d", "white", self.parar)
        self._botao(botoes, "sair", "Sair", 1, 1, "#dde5ed", TEXTO, self.sair)

        self.painel = tk.Label(self, text="\n\n", font=("DejaVu Sans Mono", 10),
                               bg="#10202f", fg="#d5e4f2",
                               justify="left", anchor="w", padx=14, pady=10)
        self.painel.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 16))

        try:
            for chave, valor in zip(CHAVES, ARQUIVO.read_text().split()):
                self.vars[chave].set(valor)
        except OSError:
            pass
        self._estado_botoes()
        self.bind("<Return>", lambda _e: self.gerar())
        self.protocol("WM_DELETE_WINDOW", self.sair)

    def _rotulo(self, pai, texto, cor, linha):
        tk.Label(pai, text=f"  {texto}  ", font=(FONTE, 9, "bold"), bg=cor, fg="white").grid(
            row=linha, column=0, padx=(14, 4), pady=(4, 12 if texto == "Sistema" else 4), sticky="w")

    def _campo(self, pai, chave, linha, coluna, unidade):
        caixa = tk.Frame(pai, bg=CARTAO)
        caixa.grid(row=linha, column=coluna, padx=6, pady=4)
        self.vars[chave] = tk.StringVar()
        self.campos[chave] = tk.Entry(caixa, textvariable=self.vars[chave], width=9,
                                      justify="right", font=(FONTE, 10), relief="flat",
                                      highlightthickness=1, highlightbackground=BORDA)
        self.campos[chave].grid(row=0, column=0, ipady=4, ipadx=4)
        tk.Label(caixa, text=unidade, font=(FONTE, 8), bg=CARTAO, fg=SUAVE).grid(
            row=0, column=1, padx=(4, 0))

    def _cartao(self, pai, titulo, linha):
        cartao = tk.Frame(pai, bg=CARTAO, highlightbackground=BORDA, highlightthickness=1)
        cartao.grid(row=linha, column=0, sticky="ew", pady=(0, 12))
        tk.Label(cartao, text=titulo, font=(FONTE, 9, "bold"), bg=CARTAO, fg=SUAVE).grid(
            row=0, column=0, columnspan=3, sticky="w", padx=14, pady=(10, 2))
        return cartao

    def _trifasico(self, pai, titulo, linha, g, unidade):
        cartao = self._cartao(pai, titulo, linha)
        for coluna, texto in ((1, f"Módulo ({unidade})"), (2, "Ângulo (graus)")):
            tk.Label(cartao, text=texto, font=(FONTE, 8), bg=CARTAO, fg=SUAVE).grid(
                row=1, column=coluna)
        for i, fase in enumerate("ABC", start=2):
            self._rotulo(cartao, f"Fase {fase}", FASE_COR[fase], i)
            self._campo(cartao, g + fase.lower(), i, 1, unidade)
            self._campo(cartao, "a" + g + fase.lower(), i, 2, "°")
        tk.Frame(cartao, bg=CARTAO, height=8).grid(row=5, column=0)

    def _botao(self, pai, chave, texto, linha, coluna, fundo, frente, comando):
        self.botoes[chave] = tk.Button(pai, text=texto, command=comando, bg=fundo, fg=frente,
                                       font=(FONTE, 10, "bold"), relief="flat", bd=0,
                                       highlightthickness=0, padx=14, pady=8)
        self.botoes[chave].grid(row=linha, column=coluna, padx=(0, 8), pady=3, sticky="w")

    def _mostrar_envio(self):
        """Valores que a MU esta enviando; com a MU parada, tudo em 0."""
        if not self.ja_rodou:
            return
        valores = self.valores if self._rodando() else [0] * len(CHAVES)
        v = {c: f"{x:g}" for c, x in zip(CHAVES, valores)}
        fase = lambda g: "  ".join(f"{g.upper()}{f} {v[g + f]:>5}∠{v['a' + g + f] + '°':<5}"
                                    for f in "abc")
        self.painel.configure(text=f"{fase('i')}\n{fase('v')}\nf {v['f']} Hz")

    def _rodando(self):
        return self.processo is not None and self.processo.poll() is None

    def _estado_botoes(self):
        rodando = self._rodando()
        self.botoes["rodar"].configure(state="disabled" if rodando else "normal")
        self.botoes["parar"].configure(state="normal" if rodando else "disabled")

    def _acompanhar(self):
        if self._rodando():
            self.after(200, self._acompanhar)
            return
        self._estado_botoes()
        self._mostrar_envio()
        if self.processo.returncode not in (0, 130, -2, -9, -15, 143):
            messagebox.showerror("MU", f"A compilação ou a MU terminou com código "
                                 f"{self.processo.returncode}. Veja o terminal.", parent=self)

    def _sinal(self, sinal, processo=None):
        processo = processo or self.processo
        if processo is not None and processo.poll() is None:
            try:
                os.killpg(os.getpgid(processo.pid), sinal)
            except OSError:
                pass

    def gerar(self):
        valores = []
        for chave in CHAVES:
            try:
                valores.append(float(self.vars[chave].get().replace(",", ".")))
                self.campos[chave].configure(highlightbackground=BORDA, highlightthickness=1)
            except ValueError:
                self.campos[chave].configure(highlightbackground="#c0392b", highlightthickness=2)
        if len(valores) < len(CHAVES):
            messagebox.showerror("MU", "Corrija os campos em vermelho.", parent=self)
            return False
        tmp = ARQUIVO.with_name("AjustesMU.txt.tmp")
        tmp.write_text("".join(f"{v:.10g}\n" for v in valores))
        os.replace(tmp, ARQUIVO)
        self.valores = valores
        self._mostrar_envio()
        return True

    def rodar(self):
        if not self.gerar():
            return
        self.processo = subprocess.Popen(["bash", "-e", "mu"], cwd=PASTA, start_new_session=True)
        self.ja_rodou = True
        self._estado_botoes()
        self._mostrar_envio()
        self.after(200, self._acompanhar)

    def parar(self):
        processo = self.processo
        self._sinal(signal.SIGINT)
        self.after(3000, lambda: self._sinal(signal.SIGKILL, processo))

    def sair(self):
        if self._rodando():
            if not messagebox.askyesno("MU", "A MU ainda está rodando. Encerrar e sair?",
                                       parent=self):
                return
            self._sinal(signal.SIGKILL)
        self.destroy()


if __name__ == "__main__":
    InterfaceMU().mainloop()
