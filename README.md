## Documentação API siFatec
```markdown
# 📦 Instalação do SQLAlchemy e FastAPI

Este guia ajuda a configurar um ambiente com **SQLAlchemy** e **FastAPI**, incluindo recomendações sobre o uso de ambiente virtual.

---

## ✅ Instalação do SQLAlchemy

Se você estiver usando o Python do sistema:

```bash
pip install sqlalchemy
```

Ou, se estiver usando `pip3`:

```bash
pip3 install sqlalchemy
```

---

## 🛡️ Recomendado: Use um ambiente virtual

Isolar suas dependências é uma boa prática. Para criar e ativar um ambiente virtual:

```bash
python3 -m venv venv
source venv/bin/activate
```

Em seguida, instale o SQLAlchemy dentro do ambiente virtual:

```bash
pip install sqlalchemy
```

---

## 🧪 Verifique o ambiente do Python

Às vezes, o Python usado no terminal não é o mesmo em que o pacote foi instalado.

Verifique com:

```bash
which python
which pip
```

Certifique-se de que ambos apontam para o mesmo ambiente (por exemplo, para o diretório `venv` se estiver usando ambiente virtual).

---

## 🚀 Instalação do FastAPI + Uvicorn + SQLAlchemy

Se você estiver usando FastAPI com SQLAlchemy, pode instalar tudo com um único comando:

```bash
pip install fastapi uvicorn sqlalchemy
```

---

## 📝 Extras

Para rodar sua aplicação FastAPI com o `uvicorn`, use:

```bash
uvicorn app.main:app --reload
```

> Substitua `app.main:app` pelo caminho correto do seu módulo principal.

---

Feito com 💻 por JV.
```

Se quiser, posso adicionar uma seção com instruções para o Thunder Client ou exemplo de uso da API também. Só avisar!
