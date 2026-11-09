# Racha! — torneios na quadra

Página HTML local conectada à API FastAPI. Permite criar torneios e times, abrir partidas e atualizar o placar tocando no lado laranja ou roxo. Cada ponto é salvo no banco de dados.

## Testar no Windows

1. Abra `iniciar-local.cmd` com duplo clique. Na primeira execução, o script instala as dependências com `uv` caso a pasta `.venv` ainda não exista.
2. Abra [http://127.0.0.1:8000/](http://127.0.0.1:8000/) no navegador.
3. Crie um torneio. Ele aparecerá na lista inicial; clique nele para entrar.
4. Dentro do torneio, adicione pelo menos dois times e crie uma partida entre eles.
5. Clique em **Abrir placar**. Toque no lado laranja ou roxo para somar um ponto; use **Desfazer ponto** para corrigir.

O script usa `racha-local.db` (SQLite) dentro desta pasta para facilitar o teste. Os dados continuam disponíveis ao reiniciar. Feche a janela do script para parar o servidor.

## Usar o banco configurado na API

Se preferir a conexão de `DATABASE_URL` definida no `.env`, execute dentro de `tournament-api`:

```powershell
.venv\Scripts\python.exe -m uvicorn main:app --reload
```

A página estará no mesmo endereço. A documentação da API fica em `/docs`. O servidor cria tabelas ausentes ao iniciar; bancos antigos cuja tabela `partidas` não possui `fase_id` precisam de migração antes de receber novas partidas.

## Aplicativo Android de teste

O APK está em [`android-app/Racha-Android-debug.apk`](android-app/Racha-Android-debug.apk). Instale no Android para abrir o Racha! como aplicativo. Ele usa a mesma API e o mesmo banco da página do PC.

Para conectar um celular físico:

1. No PC, feche o servidor anterior caso a porta 8000 já esteja em uso. Abra `iniciar-rede-local.cmd` e mantenha a janela aberta.
2. Conecte o celular e o PC à mesma rede Wi-Fi.
3. Na primeira tela do aplicativo, informe `http://IP_DO_PC:8000`, usando o IPv4 do PC mostrado pela janela do servidor.
4. Para trocar o endereço depois, toque em **Servidor** no topo da página dentro do aplicativo.

No emulador Android, `http://10.0.2.2:8000` acessa o servidor do PC. O APK é assinado com uma chave de depuração para testes. A API local não usa contas; execute o servidor de rede apenas em uma rede confiável.

O projeto Android está em `android-app/`. Na máquina de desenvolvimento, é possível gerar novamente o APK com `android-app/build-manual.ps1` usando o Android SDK 36 e o JDK. O aplicativo precisa de acesso à API para carregar torneios e registrar pontos.

## Instalação pelo navegador

A página também possui um manifesto de aplicativo. Em `localhost` ou HTTPS, navegadores compatíveis podem instalar o Racha! como aplicativo web. A interface fica em cache para abrir sem conexão; consultar torneios e alterar pontos exige a API ligada.
