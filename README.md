# Saas - Extração de Informações de Sites 🌐

Uma aplicação web interativa construída com Streamlit que permite extrair e analisar conteúdo de sites usando IA, possibilitando fazer perguntas sobre o conteúdo extraído.

## 🚀 Funcionalidades

- 🔑 Gerenciamento seguro de API Key da OpenAI
- 🌐 Extração de conteúdo de qualquer URL
- 💬 Sistema de perguntas e respostas sobre o conteúdo extraído
- 🤖 Análise de conteúdo usando IA (GPT-3.5-turbo)
- 📊 Interface amigável e responsiva

## 🛠️ Tecnologias Utilizadas

- **Streamlit**: Framework para criação da interface web
- **LangChain**: Framework para desenvolvimento de aplicações com LLMs
- **OpenAI GPT-3.5**: Modelo de linguagem para processamento do conteúdo
- **Hugging Face**: Embeddings para processamento de texto
- **ChromaDB**: Banco de dados vetorial para armazenamento eficiente
- **Python**: Linguagem de programação principal

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Uma chave de API válida da OpenAI
- Conexão com a internet

## ⚙️ Instalação

1. Clone o repositório:
```bash
git clone [URL-do-repositório]
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## 🚀 Como Usar

1. **Inicie o aplicativo**:
```bash
streamlit run app3.py
```

2. **Configure sua API Key**:
   - Insira sua chave de API da OpenAI no campo apropriado
   - Clique em "Registrar API Key"
   - Aguarde a confirmação de registro

3. **Extraia informações**:
   - Cole a URL do site que deseja analisar
   - Clique em "Carregar URL"
   - Aguarde o processamento do conteúdo

4. **Faça perguntas**:
   - Digite sua pergunta sobre o conteúdo
   - Clique em "Enviar Pergunta"
   - Aguarde a resposta gerada pela IA

## ⚠️ Limitações e Considerações

- O aplicativo requer uma API Key válida da OpenAI
- Há limites de requisições baseados no seu plano da OpenAI
- O processamento de sites muito grandes pode levar mais tempo
- Alguns sites podem ter restrições de acesso ao conteúdo

## 🔒 Segurança

- A API Key é armazenada apenas durante a sessão
- Não há armazenamento permanente de dados sensíveis
- As requisições são feitas de forma segura via HTTPS

## 🤝 Contribuições

Contribuições são bem-vindas! Para contribuir:
1. Faça um Fork do projeto
2. Crie uma Branch para sua Feature (`git checkout -b feature/AmazingFeature`)
3. Faça o Commit de suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Faça o Push para a Branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👤 Autor

Mauro Guimarães

---

⭐️ Se este projeto te ajudou, considere dar uma estrela!
