# TCC - Funções de proteção 25, 27, 59 e 81 em um IED virtual IEC 61850

Código do meu TCC em Engenharia Elétrica na UFC. A base é a versão do vIED e da vMU disponível no repositório [matheusxd8147/VIED](https://github.com/matheusxd8147/VIED). Em cima dela fui acrescentando as funções de proteção.

Cada etapa fica numa pasta própria:

- `MU_27_59_81` e `VIED_27_59_81`: funções 27, 59 e 81
- `MU_25`: vMU da função 25. Dá para rodar duas cópias ao mesmo tempo, uma para a linha (`VMU01`) e outra para a barra (`VMU02`), escolhendo qual é qual no arquivo `ID_MU.txt`

## Compilar

```bash
git clone https://github.com/matheusxd8147/VIED ~/VIED
cd ~/VIED && make
git clone https://github.com/gesielsg/tcc-vied-iec61850
cd tcc-vied-iec61850/VIED_27_59_81 && head -2 vied | bash
cd ../MU_27_59_81 && head -2 mu | bash
```

Para rodar, primeiro o vIED (`sudo ./vied1 lo`) e depois a vMU (`sudo ./mu1 lo`). Os ajustes e os testes estão no LEIA-ME de cada pasta.
