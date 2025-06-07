# 🚀 Presto

[![Presto.png](https://i.postimg.cc/wvZ0sTPL/Presto-Banner-para-Reddit.png)](https://postimg.cc/k67B0C2w)

[![Licença MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Feito com Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Status: Alpha](https://img.shields.io/badge/Status-Beta-orange.svg)](https://github.com/pedrohtomazi/Presto/releases/tag/v0.1.0)

Presto é um projeto inovador que visa centralizar o acesso a conteúdos acadêmicos e resumos de estudo, começando como um assistente interativo via WhatsApp e evoluindo para uma plataforma web e um aplicativo móvel completos.

---

## 🎯 Visão do Futuro: De Bot a Plataforma Completa

Atualmente, o Presto opera como um bot interativo no WhatsApp, oferecendo acesso simplificado a uma biblioteca de resumos. No entanto, nossa visão de futuro é expandir o Presto para se tornar uma **plataforma educacional robusta e acessível através de um aplicativo móvel dedicado e um portal web abrangente.**

Esta migração permitirá:

* **Experiência de Usuário Aprimorada:** Interfaces gráficas intuitivas e ricas em funcionalidades, impossíveis de replicar em um ambiente de chat.
* **Gerenciamento de Conteúdo Avançado:** Ferramentas para upload, organização e curadoria de resumos com maior flexibilidade.
* **Interação em Comunidade:** Funcionalidades sociais para que estudantes colaborem, compartilhem e avaliem conteúdos.
* **Escalabilidade e Desempenho:** Uma arquitetura mais robusta para lidar com um volume crescente de usuários e dados.
* **Recursos Inovadores:** Integração de AI para personalização de aprendizado, busca avançada e muito mais.

Este repositório representa a base do backend Python que continuará a alimentar as funcionalidades centrais da plataforma, tanto para a versão via WhatsApp quanto para as futuras interfaces web e móveis.

## ✨ Funcionalidades Atuais (MVP - Minimum Viable Product)

A versão beta do Presto já entrega um conjunto de funcionalidades essenciais:

* **Navegação por Biblioteca:**
    * Listagem de universidades.
    * Filtragem de cursos por universidade.
    * Seleção de disciplinas por curso.
    * Acesso a resumos de disciplinas.
* **Gestão de Perfil de Usuário:**
    * Visualização do status de membro (pagante/gratuito).
    * Consulta de resumos restantes.
* **Comandos Administrativos:**
    * Ferramentas para listagem de grupos e envio de mensagens em massa (acesso restrito).
* **Controle de Fluxo:**
    * Comando `/menu` para reinício da interação.
    * Gerenciamento de estado da conversa por usuário.

## 🛠️ Tecnologias

O backend do Presto é construído utilizando as seguintes tecnologias:

* **Python:** Linguagem de programação principal.
* **Flask:** Micro-framework web para orquestração das requisições via webhook.
* **MySQL:** Banco de dados relacional para persistência de dados de usuários, universidades, cursos, disciplinas e resumos.
* **WhatsApp API (via Ferramenta Externa):** Integração para comunicação assíncrona com usuários.
* **Bibliotecas Python:**
    * `python-dotenv`: Gerenciamento de variáveis de ambiente.
    * `requests`: Requisições HTTP.
    * `PyMySQL`: Conexão com MySQL.
    * `threading`: Gerenciamento de processos concorrentes para timers.
    * `openai-whisper`: (Presente nas dependências) Potencial para transcrição de áudio.

## 📁 Estrutura do Projeto

A organização do projeto segue uma abordagem modular para facilitar a manutenção e o desenvolvimento:
