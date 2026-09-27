# Trabalho 5 — Pinball com colisão por polígonos (SAT)

Fork de `Trab4/polygonCollision`. É um pinball onde a bola sofre gravidade
e colide com o cenário usando o SAT que já tínhamos no Trab4, só que
estendido pra funcionar entre **círculo (a bola)** e **polígono**
(a maioria dos obstáculos de um pinball não é retângulo nem círculo).

## Como rodar

```bash
pip install pygame
python3 main.py
```

## Controles

| Tecla | Ação |
|---|---|
| `←` / `A` | Flipper esquerdo |
| `→` / `D` / `L` | Flipper direito |
| `ESPAÇO` (segurar/soltar) | Carrega e lança a bola |
| `R` | Reinicia |
| `ESC` | Sai |

## O que veio do Trab4 e o que é novo

- **`shape.py`** — `Polygon` é o mesmo do Trab4 (bounding box, teste de
  convexidade, decomposição convexa, ponto-dentro-do-polígono). Tirei
  o código de arrastar vértice com o mouse (não precisava aqui) e
  adicionei `set_points`, usado pelos flippers pra atualizar a forma
  a cada frame que giram.
- **`collision.py`** — `polygon`/`convex`/`axes`/`project` são os
  mesmos do Trab4. O que é novo é `circle_polygon`: mesmo SAT, mas
  testando também o eixo do centro do círculo até o vértice mais
  próximo (senão erra quando quem toca primeiro é um canto), e
  projetando o círculo como `centro ± raio`. Funciona com qualquer
  polígono, inclusive côncavo (via decomposição).
- **`ball.py`** — física da bola: gravidade, integração, velocidade
  máxima, rastro visual.
- **`flipper.py`** — o flipper é um trapézio afunilado (não é
  retângulo nem círculo), gira em torno de um pivô. Ao colidir, além
  de refletir, soma a velocidade tangencial do ponto de impacto
  (ω × r) na bola — é o que dá o "chute".
- **`entities.py`** — `Wall` (só reflete), `Bumper` (hexágono: reflete
  e soma pontos) e `BonusTrigger` (pentágono: não reflete, só detecta
  que a bola passou por dentro via `point_inside` e aplica o efeito).
- **`main.py`** — monta a mesa, o loop do jogo, o lançador e o placar.

## Onde cada regra do enunciado aparece

- **Regiões que não são só retângulo/círculo:** cantos triangulares,
  defletor do lançador, slingshots (triângulos), bumpers (hexágonos),
  zona-bônus (pentágono) e os flippers (trapézios).
- **Efeito que NÃO muda a trajetória:** a `BonusTrigger` (zona verde).
  A bola passa reto por dentro; ao entrar, ganha pontos e um pequeno
  boost de velocidade *na mesma direção* em que já estava indo — a
  colisão aqui só detecta a passagem, nunca reposiciona/reflete a bola.
- **Efeito que impede/reflete o movimento:** paredes, slingshots e
  flippers refletem a bola. Os bumpers fazem as duas coisas ao mesmo
  tempo: refletem (com restituição > 1, "chutando" a bola pra longe)
  e somam pontos, como um bumper de pinball de verdade.

## Limitações conhecidas

- A calha do lançador se reconecta ao campo por cima sem válvula
  unidirecional; em teoria dá pra bola voltar pra calha depois de já
  estar em jogo (raro na prática).
- Sem som.
