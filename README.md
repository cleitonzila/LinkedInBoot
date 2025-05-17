# Gerador de Postagens LinkedIn para Certificados da Alura

## Descrição

Esse projeto fornece um serviço web para gerar postagens automáticas de LinkedIn a partir de certificados de conclusão de cursos da Alura. A aplicação é escrita em Python, utilizando Flask, Google GenAI (gemini-2.0-flash) com agentes ADK, e dispõe de uma interface simples em HTML/CSS (Bootstrap).

## Funcionalidades

* **Upload de certificado (PDF)**: o usuário envia o PDF do certificado da Alura.
* **Extração de texto**: utiliza PyPDF2 para extrair o texto do PDF.
* **Agente extrator de título**: identifica o nome exato do curso no texto extraído.
* **Agente buscador**: pesquisa conteúdos e tecnologias do curso via Google Search.
* **Agente escritor**: gera um post inspirador e profissional para LinkedIn.
* **Interface web**: template `index.html` com formulário de upload e exibição de resultado.
* **Deploy em AWS Lightsail**: aplicação configurada para rodar continuamente em servidor Lightsail.


## Pré-requisitos

* Conta Google com acesso à API GenAI e chave de API configurada.
* Python 3.8 ou superior.
* Variável de ambiente `GOOGLE_API_KEY` definida em `.env`.

## Instalação

1. Clone este repositório:
2. Crie e ative um ambiente virtual:
3. Instale as dependências:

## Configuração

1. Crie um arquivo `.env` na raiz do projeto com o conteúdo:
2. Certifique-se de que a porta 8000 esteja liberada no firewall (AWS Lightsail ou localmente).

## Execução Local

Para rodar em modo de desenvolvimento:
Abra no navegador: [http://localhost:8000/](http://localhost:8000/)

Teste disponivel em: http://aluralinkedinposts.icu
![{8BB1B37B-E193-4BB4-9D7E-5927E69D38CA}](https://github.com/user-attachments/assets/115c4ca1-7c83-4ffe-8348-3095d8105506)
