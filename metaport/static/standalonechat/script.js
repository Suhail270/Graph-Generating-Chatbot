const chatbotToggler = document.querySelector(".chatbot-toggler");
const closeBtn = document.querySelector(".close-btn");
const chatbox = document.querySelector(".chatbox");
const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector(".button-24");
const inputInitHeight = chatInput.scrollHeight;

let userMessage = null;
var chat_history = []

const createChatLi = (message, className) => {
    const chatLi = document.createElement("li");
    const logoImage = document.getElementById("logo-image");
    chatLi.classList.add("chat", `${className}`);
    // let chatContent = className === "outgoing" ? `<p></p>` : `<span class="profile-pic"><img src="{% static 'metaport/static/standalonechat/images/logo-round.jpg' %}" alt="Logo"></span><p></p>`;
    let chatContent = className === "outgoing" ? `<p></p>` : `<span>${logoImage.outerHTML}</span><p></p>`;
    chatLi.innerHTML = chatContent;
    chatLi.querySelector("p").innerHTML = message === "Thinking" ? `<div class="lds-facebook"><div></div><div></div><div></div>` : message;
    
    return chatLi; 
}

// const createChatLi = (message, className) => {
//     const chatLi = document.createElement("li");
//     const logoImage = document.getElementById("logo-image");
//     chatLi.classList.add("chat", `${className}`);
  
//     let chatContent;
//     if (message.toLowerCase() === "thinking") {
//         chatContent = `<div class="dots">
//         <span style="--i:1;"></span>
//         <span style="--i:2;"></span>
//         <span style="--i:3;"></span>
//         <span style="--i:4;"></span>
//         <span style="--i:5;"></span>
//         <span style="--i:6;"></span>
//         <span style="--i:7;"></span>
//         <span style="--i:8;"></span>
//         <span style="--i:9;"></span>
//         <span style="--i:10;"></span>
//         <span style="--i:11;"></span>
//         <span style="--i:12;"></span>
//         <span style="--i:13;"></span>
//         <span style="--i:14;"></span>
//         <span style="--i:15;"></span>
//       </div>`;
//     } 
//     chatContent = className === "outgoing" ? `<p></p>` : `<span>${logoImage.outerHTML}</span><p></p>`;
//     chatLi.querySelector("p").textContent = message;
    

//     chatLi.innerHTML = chatContent;
//     return chatLi;
// }



const generateResponse = (chatElement) => {
    const API_URL = "http://127.0.0.1:8000/chat_api";
    const messageElement = chatElement.querySelector("p");
    const requestOptions = {
        method: "POST",
        mode: "no-cors",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            type: "pdf",
            chat_history: chat_history,
            additional_prompt: "",
            model: "gpt-3.5-turbo",
            messages: [{role: "user", content: userMessage}],
        })
    }



    fetch(API_URL, requestOptions).then(res => res.json()).then(data => {
        chat_history = data.chat_history;
        if (userMessage.includes("chart") || userMessage.includes("graph") || userMessage.includes("plot")) {
            img = document.createElement('img');
            img.src = data.resp;
            img.style.width = "250px";
            img.addEventListener("click", () => {
                window.open(data.resp, "_blank");
              });
            messageElement.textContent = "";
            messageElement.appendChild(img);
        } else {
            messageElement.textContent = data.resp;
        }

    }).catch((e) => {
        console.log(e);
        messageElement.classList.add("error");
        messageElement.textContent = "Oops! Something went wrong. Please try again.";
    }).finally(() => chatbox.scrollTo(0, chatbox.scrollHeight));
}

// const generateResponse = (chatElement) => {
//     const API_URL = "https://api.openai.com/v1/chat/completions";
//     const messageElement = chatElement.querySelector("p");
//     const requestOptions = {
//         method: "POST",
//         headers: {
//             "Content-Type": "application/json",
//             "Authorization": `Bearer ${API_KEY}`
//         },
//         body: JSON.stringify({
//             model: "gpt-3.5-turbo",
//             messages: [{role: "user", content: userMessage}],
//         })
//     }
//     fetch(API_URL, requestOptions).then(res => res.json()).then(data => {
//         messageElement.textContent = data.choices[0].message.content.trim();
//     }).catch(() => {
//         messageElement.classList.add("error");
//         messageElement.textContent = "Oops! Something went wrong. Please try again.";
//     }).finally(() => chatbox.scrollTo(0, chatbox.scrollHeight));
// }

const handleChat = () => {
    userMessage = chatInput.value.trim(); 
    if(!userMessage) return;
    chatInput.value = "";
    chatInput.style.height = `${inputInitHeight}px`;

    chatbox.appendChild(createChatLi(userMessage, "outgoing"));
    chatbox.scrollTo(0, chatbox.scrollHeight);
    
    setTimeout(() => {
        const incomingChatLi = createChatLi("Thinking", "incoming");
        chatbox.appendChild(incomingChatLi);
        chatbox.scrollTo(0, chatbox.scrollHeight);
        generateResponse(incomingChatLi);
    }, 600);
}

chatInput.addEventListener("input", () => {
    chatInput.style.height = `${inputInitHeight}px`;
    chatInput.style.height = `${chatInput.scrollHeight}px`;
});

chatInput.addEventListener("keydown", (e) => {
    if(e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
        e.preventDefault();
        handleChat();
    }
});

sendChatBtn.addEventListener("click", handleChat);
closeBtn.addEventListener("click", () => document.body.classList.remove("show-chatbot"));
chatbotToggler.addEventListener("click", () => document.body.classList.toggle("show-chatbot"));