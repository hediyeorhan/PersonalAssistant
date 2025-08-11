const chatBox = document.getElementById("chat-box");
const messageInput = document.getElementById("message");
const sendBtn = document.getElementById("send-btn");

// Modal elementleri
const modal = document.getElementById("reminder-modal");
const modalYes = document.getElementById("reminder-yes");
const modalNo = document.getElementById("reminder-no");

let pendingMessage = ""; // Hatırlatma sorusu bekleyen mesaj

// Mesajı chat kutusuna ekle
function addMessage(text, sender) {
    const div = document.createElement("div");
    div.className = sender === "user" ? "user-msg" : "agent-msg";

    if (sender === "agent") {
        div.innerHTML = text;
    } else {
        div.textContent = text;
    }

    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Normal mesaj gönder
function sendNormalMessage(msg, extraData = null) {
    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg, extra_data: extraData })
    })
    .then(res => res.json())
    .then(data => {
        const responseText = data.response;

        if (responseText.includes("Hatırlatma ister misiniz?")) {
            // Popup aç
            pendingMessage = msg;
            modal.style.display = "flex";
        } else {
            addMessage(responseText.replace(/\n/g, "<br><br>"), "agent");
            loadTodayReminders()
        }

    })
    .catch(() => {
        addMessage("Sunucu ile bağlantı kurulamadı.", "agent");
    });

}

// Mesaj gönderme ana fonksiyonu
function sendMessage() {
    const msg = messageInput.value.trim();
    if (!msg) return;

    addMessage(msg, "user");
    messageInput.value = "";

    if (msg.toLowerCase().includes("sil") || msg.toLowerCase().includes("tamamla")) {
        let ids = prompt("Lütfen ID değerlerini ',' ile ayırarak giriniz:");
        if (!ids) {
            addMessage("İşlem iptal edildi.", "agent");
            return;
        }
        const id_list = ids.split(",").map(s => s.trim());
        sendNormalMessage(msg, { id_list });
    }
    else {
        sendNormalMessage(msg);
    }
}

// Modal butonları
modalYes.addEventListener("click", () => {
    modal.style.display = "none";
    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: pendingMessage, extra_data: { reminder_confirm: true } })
    })
    .then(res => res.json())
    .then(data => {
        addMessage(data.response.replace(/\n/g, "<br><br>"), "agent");
        pendingMessage = "";
        loadTodayReminders()
    });
});

modalNo.addEventListener("click", () => {
    modal.style.display = "none";
    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: pendingMessage, extra_data: { reminder_confirm: false } })
    })
    .then(res => res.json())
    .then(data => {
        addMessage(data.response.replace(/\n/g, "<br><br>"), "agent");
        pendingMessage = "";
        loadTodayReminders()
    });
});

// Gönderme eventleri
sendBtn.addEventListener("click", sendMessage);
messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage();
});


function loadTodayReminders() {
    fetch("/api/today_reminders")
        .then(res => res.json())
        .then(data => {
            const reminderList = document.getElementById("reminder-list");
            reminderList.innerHTML = "";  // Önceki içeriği temizle

            if (data.length === 0) {
                reminderList.innerHTML = "<li>Henüz hatırlatıcı yok</li>";
                return;
            }

            data.forEach(reminder => {
                const li = document.createElement("li");
                li.innerHTML = `<strong>${reminder.due_date}</strong> - ${reminder.title}`;
                reminderList.appendChild(li);
            });
        })
        .catch(() => {
            const reminderList = document.getElementById("reminder-list");
            reminderList.innerHTML = "<li>Hatırlatıcılar yüklenirken hata oluştu.</li>";
        });
}

window.addEventListener("load", () => {
    loadTodayReminders();
});
