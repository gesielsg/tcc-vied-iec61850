# vMU usada no teste das funções 27, 59 e 81

Programa principal: `vmu.c`. A vMU gera 4800 amostras por segundo (80 por ciclo de 60 Hz) das tensões e correntes definidas no `AjustesMU.txt` e publica tudo em Sampled Values com o nome `VMU01`. Também recebe do vIED, por GOOSE (`CONTROL_BK`), os comandos de abrir e fechar o disjuntor.

## O que mudou em relação ao código original

- A frequência passou a ser lida do `AjustesMU.txt` (linha 13). No original ela era fixa em 60 Hz (80 amostras por ciclo).
- O ângulo da senoide é acumulado amostra a amostra, para a onda não dar salto quando a frequência muda.
- A cada 10 ms a vMU confere se o `AjustesMU.txt` foi modificado e, se foi, relê os valores. Dá para aplicar degraus de tensão e frequência com ela rodando.
- Interface gráfica (`interface.py`) para editar o `AjustesMU.txt` e iniciar a vMU.

## AjustesMU.txt

13 linhas, nesta ordem:

| Linhas | Conteúdo |
|---|---|
| 1 a 6 | corrente (A) e ângulo (graus) das fases A, B e C |
| 7 a 12 | tensão (V) e ângulo (graus) das fases A, B e C |
| 13 | frequência (Hz) |

O arquivo do repositório tem 50 A e 13800 V por fase, ângulos 0°, 240° e 120°, e 60 Hz.

## Compilar e rodar

```bash
cd MU_27_59_81
head -2 mu | bash        # só compila (gera o mu1)
sudo ./mu1 lo            # roda na interface lo
```

Ou pela interface:

```bash
sudo python3 interface.py
```

## Degraus para testar as funções

Com o vIED e a vMU rodando, em outro terminal na pasta da vMU:

```bash
sed -i '7s/.*/10000/' AjustesMU.txt    # tensão A em 10000 V: a 27 atua depois de 1 s
sed -i '7s/.*/13800/' AjustesMU.txt
sed -i '9s/.*/16000/' AjustesMU.txt    # tensão B em 16000 V: a 59 atua depois de 1 s
sed -i '9s/.*/13800/' AjustesMU.txt
sed -i '13s/.*/58.5/' AjustesMU.txt    # 58,5 Hz: a 81 (sub) atua depois de 0,5 s
sed -i '13s/.*/60/'   AjustesMU.txt
sed -i '13s/.*/61.5/' AjustesMU.txt    # 61,5 Hz: a 81 (sobre) atua depois de 0,5 s
sed -i '13s/.*/60/'   AjustesMU.txt
```

Entre um degrau e outro, faça o reset do trip no vIED (`touch Reset_trip.txt` na pasta do vIED).

## Outros arquivos

- `static_model.c` e `static_model.h`: modelo de dados da vMU, gerado a partir do `MU.iid`.
- `sv_publisher_example.c`: exemplo de publicação de Sampled Values da libiec61850, que já vinha na pasta da vMU. Não entra na compilação.
- `Como compilar`: o comando de compilação, para referência.
