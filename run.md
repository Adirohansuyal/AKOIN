Let’s gooo — love that “done, all working” energy 😄🔥
You’ve got the system running… now you just want the **repeat-run commands** so you don’t forget later.

Here’s your **quick runbook** — bookmark this mentally 👇

---

# 🐳 If You Want to Run the App Again (Docker)

## 🟢 1️⃣ Go to Project Folder

```bash
cd /Users/adityasuyal/Desktop/corep_assistant
```

---

## 🟢 2️⃣ Start Containers

If images already built:

```bash
docker compose up
```

That’s it — no rebuild needed.

---

## 🟢 3️⃣ If You Changed Code

Rebuild + run:

```bash
docker compose up --build
```

Use this when you edit:

* app.py
* rag.py
* streamlit_app.py
* Dockerfile
* requirements.txt

---

# 🛑 To Stop the App

Press:

```
CTRL + C
```

Then run:

```bash
docker compose down
```

Stops + removes containers.

---

# 🔁 Quick Command Cheat Sheet

| Task                    | Command                     |
| ----------------------- | --------------------------- |
| Start app               | `docker compose up`         |
| Rebuild + start         | `docker compose up --build` |
| Stop app                | `docker compose down`       |
| View running containers | `docker ps`                 |
| View logs               | `docker logs corep_backend` |

---

# 🌐 URLs After Starting

Once running:

* UI → [http://localhost:8501](http://localhost:8501)
* API → [http://localhost:8000/docs](http://localhost:8000/docs)

---

# ⚡ Fast Restart Trick

If you just want background run:

```bash
docker compose up -d
```

Then app runs silently.

Stop later:

```bash
docker compose down
```

---

# 🧠 If Ports Busy Again

Run:

```bash
docker compose down
docker stop $(docker ps -q)
```

Then restart.

---

# 🏁 Final “Run Again” Flow

Whenever you reopen laptop:

```bash
cd corep_assistant
docker compose up
```

Open browser → done.

---

You’re now sitting on a fully dockerized GenAI RegTech prototype 🐳📊

If you ever want to:

* Push to Docker Hub
* Deploy to cloud
* Share public demo

…I’ve got you.

For now — ship it 🚀
