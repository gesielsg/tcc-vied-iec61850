# vIED com as funções 27, 59 e 81

Programa principal: `server_example_goose.c`. O vIED recebe da vMU as amostras Sampled Values `VMU01`, calcula tensões, correntes e frequência e executa as funções de proteção.

## O que foi acrescentado nesta etapa

- **Função 81:** subfrequência e sobrefrequência, com a frequência calculada a partir das amostras de tensão.
- **Função 27:** subtensão.
- **Função 59:** sobretensão.
- **Reset do trip:** depois que uma função atua, o trip e a sinalização de "atuou" ficam travados, como num relé real. Só voltam ao normal com o reset manual.

## Arquivos de ajuste

| Arquivo | Linha 1 | Linha 2 | Linha 3 | Linha 4 |
|---|---|---|---|---|
| `Ajustes_27.txt` | partida (V) | tempo (s) | | |
| `Ajustes_59.txt` | partida (V) | tempo (s) | | |
| `Ajustes_81.txt` | partida da subfrequência (Hz) | tempo (s) | partida da sobrefrequência (Hz) | tempo (s) |
| `Reset_trip.txt` | o vIED faz o reset quando este arquivo é modificado | | | |

Valores que estão no repositório: 27 em 11040 V (0,8 de 13800 V) com 1 s; 59 em 15180 V (1,1 de 13800 V) com 1 s; 81 em 59 Hz e 61 Hz, as duas com 0,5 s.

Os arquivos das funções que já existiam (`Ajustes_50`, `50N`, `51`, `51N`, `51V`, `67`, `67N`) estão zerados para o teste mostrar só a 27, a 59 e a 81.

## Compilar e rodar

```bash
cd VIED_27_59_81
head -2 vied | bash      # só compila (gera o vied1)
sudo ./vied1 lo          # roda na interface lo
```

Rode o vIED antes da vMU. Com a vMU desligada não há tensão medida e a 27 atuaria logo de cara.

Para fazer o reset do trip, em outro terminal:

```bash
touch Reset_trip.txt
```

Se aparecer "Starting server failed", é porque já tem um `vied1` ou `mu1` aberto: `sudo pkill -x vied1; sudo pkill -x mu1` e rode de novo.

## Outros arquivos

- `static_model.c` e `static_model.h`: modelo de dados do vIED, gerado a partir do `VIED_21L1.IID`.
- `VIED_Parametros.c` e `vied_ajustes`: programa do código original para editar os ajustes pelo terminal.
