# FERMENTE Video Engine

Este repositório é o motor de geração de vídeos da FERMENTE, baseado em MoneyPrinterTurbo.

## Estado suportado

- Python 3.11+
- WebUI em `http://127.0.0.1:8501`
- API em `http://127.0.0.1:8080`
- Health check em `GET /ping`
- FFmpeg obrigatório
- Edge TTS funciona sem chave
- Fish Audio, OpenAI/Kimi/Gemini e fontes de mídia externas exigem as respectivas chaves

## Inicialização local recomendada

1. Instale Docker Desktop (Windows/macOS) ou Docker Engine + Compose (Linux).
2. Copie `config.example.toml` para `config.toml`.
3. Mantenha `app.api_key` vazio somente se o serviço ficar restrito à própria máquina.
4. Execute:

```bash
docker compose up --build -d
```

5. Verifique:

```bash
curl http://127.0.0.1:8080/ping
```

A resposta esperada é `"pong"`.

6. Abra a WebUI em `http://127.0.0.1:8501`.

## Configuração mínima para o piloto FERMENTE

No WebUI/configuração, use inicialmente:

- idioma da interface: Português;
- idioma do vídeo: Português (Brasil);
- formato: 16:9 para YouTube tradicional ou 9:16 para Shorts;
- TTS inicial: Edge TTS, para validar o pipeline sem custo;
- segundo TTS para comparação: Fish Audio;
- legendas: habilitadas;
- fonte de mídia: Pexels/Pixabay/Coverr ou arquivos locais;
- LLM: um provedor configurado com chave válida para gerar roteiro automaticamente.

O motor também aceita roteiro e mídia locais, o que permite testar montagem, narração e legendas antes de contratar APIs externas.

## Segurança

`config.toml` contém credenciais e não deve ser versionado. Quando `app.api_key` estiver configurado, as rotas `/v1` e os arquivos gerados em `/tasks` exigem o cabeçalho `x-api-key`.

Para publicar o serviço na internet, use proxy reverso HTTPS e defina uma `app.api_key` forte. Não exponha Redis diretamente à internet.

## Verificação automática

O workflow `.github/workflows/fermente-smoke.yml` instala as dependências e o FFmpeg, sobe a API e o WebUI e valida os dois health checks. Um PR só deve ser considerado operacional quando esse smoke test estiver verde.

## O que ainda depende de credenciais externas

O repositório pode ser validado e executado sem chaves externas, mas a geração totalmente automatizada de um vídeo a partir apenas de um tema exige pelo menos:

- uma chave de LLM para roteiro/termos de mídia; e
- uma fonte de mídia com chave, ou mídia local.

Fish Audio é opcional; Edge TTS permite validar a narração gratuitamente. Publicação automática no YouTube exige credenciais próprias do serviço de publicação configurado no projeto.
